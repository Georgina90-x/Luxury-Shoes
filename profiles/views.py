from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import UserProfile, MarketingEmail, EmailLog
from .forms import UserProfileForm, MarketingEmailForm
from django.core.mail import send_mail
from django.conf import settings

from checkout.models import Order


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed, please ensure \
                            the form in valid.')
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True,
    }

    return render(request, template, context)


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}.'
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)


@login_required
def send_marketing_email(request):
    if request.method == "POST":
        subject = request.POST.get("subject", "Special Offer Just for You!")
        message = request.POST.get("message", "Check out our latest products!")

        # Render email template
        html_message = render_to_string("profiles/marketing_email.html", {
            "subject": subject,
            "message": message
        })
        plain_message = strip_tags(html_message)  # Fallback for non-HTML email clients

        recipients = User.objects.filter(is_active=True, email__isnull=False).values_list("email", flat=True)

        if not recipients:
            messages.warning(request, "No active users with email addresses found.")
            return redirect("send_marketing_email")

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # Use configured email sender
            to=[],
            bcc=list(recipients)  # Send as BCC to protect user privacy
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        # Create a new MarketingEmail record
        marketing_email = MarketingEmail.objects.create(subject=subject, message=message)

        # Log only users who received the email
        users_received = User.objects.filter(email__in=recipients)
        for user in users_received:
            EmailLog.objects.create(user=user, email=marketing_email)

        messages.success(request, "Marketing email sent successfully!")
        return redirect("send_marketing_email")

    return render(request, "profiles/send_marketing_email.html")
