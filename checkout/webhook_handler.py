from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import stripe
import json
import time


class StripeWH_Handler:
    """
    Handle Stripe Webhooks
    """
    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """
        Send the user a confirmation email after placing an order
        """
        try:
            cust_email = order.email
            subject = render_to_string(
                'checkout/confirmation_emails/confirmation_email_subject.txt',
                {'order': order})
            body = render_to_string(
                'checkout/confirmation_emails/confirmation_email_body.txt',
                {'order': order, 'contact_email': settings.EMAIL_FROM_ORDERS})
            send_mail(
                subject,
                body,
                settings.EMAIL_FROM_ORDERS,
                [cust_email]
            )
        except Exception as e:
            raise Exception(f"Error sending confirmation email: {e}")

    def handle_event(self, event):
        """
        Handles generic webhook events inc unknown/unexpected
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handles payment_intent.succeeded webhook from Stripe
        """
        try:
            intent = event.data.object
            pid = intent.id
            bag = intent.metadata.get('bag', '{}')
            save_info = intent.metadata.get('save_info', False)

            print("Received metadata:", intent.metadata) # debugging

            # Get the Charge object
            stripe_charge = stripe.Charge.retrieve(
                intent.latest_charge
            )

            billing_details = stripe_charge.billing_details
            shipping_details = intent.shipping
            grand_total = round(stripe_charge.amount / 100, 2)

            for field, value in shipping_details.address.items():
                if value == "":
                    shipping_details.address[field] = None

            # Update profile information if save_info was checked
            profile = None
            username = intent.metadata.get('username', 'AnonymousUser')
            if username != 'AnonymousUser':
                profile = UserProfile.objects.get(user__username=username)
                if save_info:
                    profile.default_street_address1 = shipping_details.get('address', {}).get('line1')
                    profile.default_street_address2 = shipping_details.get('address', {}).get('line2')
                    profile.default_town_or_city = shipping_details.get('address', {}).get('city')
                    profile.default_county = shipping_details.get('address', {}).get('state')
                    profile.default_postcode = shipping_details.get('address', {}).get('postal_code')
                    profile.default_country = shipping_details.get('address', {}).get('country')
                    profile.default_phone_number = shipping_details.get('phone')
                    profile.save()

            order_exists = False
            attempt = 1
            while attempt <= 5:
                try:
                    order = Order.objects.get(
                        full_name__iexact=shipping_details.get('name', ''),
                        email__iexact=billing_details.get('email', ''),
                        street_address1__iexact=shipping_details.get('address', {}).get('line1', ''),
                        street_address2__iexact=shipping_details.get('address', {}).get('line2', ''),
                        town_or_city__iexact=shipping_details.get('address', {}).get('city', ''),
                        county__iexact=shipping_details.get('address', {}).get('state', ''),
                        postcode__iexact=shipping_details.get('address', {}).get('postal_code', ''),
                        country__iexact=shipping_details.get('address', {}).get('country', ''),
                        phone_number__iexact=shipping_details.get('phone', ''),
                        grand_total=grand_total,
                        original_bag=bag,
                        stripe_pid=pid,
                    )
                    order_exists = True
                    break
                except Order.DoesNotExist:
                    attempt += 1
                    time.sleep(1)
            if order_exists:
                self._send_confirmation_email(order)
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | Success: \
                        Verified order in database.',
                    status=200)
            else:
                order = None
                try:
                    order = Order.objects.create(
                                full_name=shipping_details.get('name', ''),
                                user_profile=profile,
                                email=billing_details.get('email', ''),
                                street_address1=shipping_details.get('address', {}).get('line1', ''),
                                street_address2=shipping_details.get('address', {}).get('line2', ''),
                                town_or_city=shipping_details.get('address', {}).get('city', ''),
                                county=shipping_details.get('address', {}).get('state', ''), 
                                postcode=shipping_details.get('address', {}).get('postal_code', ''),
                                country=shipping_details.get('address', {}).get('country', ''),
                                phone_number=shipping_details.get('phone', ''),
                                grand_total=grand_total,
                                original_bag=bag,
                                stripe_pid=pid,
                            )
                    for item_id, item_data in json.loads(bag).items():
                        product = Product.objects.get(id=item_id)
                        if isinstance(item_data, int):
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                            order_line_item.save()
                        else:
                            for shoesize, quantity in (
                                item_data['items_by_shoesize'].items()
                            ):
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=shoesize,
                                    )
                                order_line_item.save()
                except Exception as e:
                    if order:
                        order.delete()
                    return HttpResponse(
                        content=f'Webhook received: {event["type"]} | ERROR: {e}',
                        status=500)
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: \
                    Created order in webhook.', status=200)
        except Exception as e:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {str(e)}',
                status=500)

    def handle_payment_intent_failed(self, event):
        """
        Handles payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
