from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    """
    Context of the shopping bag with delivery
    """
    bag_items = []
    total = 0
    subtotal = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            total += item_data * product.price
            product_count += item_data
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        else:
            product = get_object_or_404(Product, pk=item_id)
            for shoesize, quantity in item_data['items_by_shoesize'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'shoesize': shoesize,
                })

    vat_calc = Decimal('0.20')  # calculates the 20% UK VAT
    vat_total = (total * vat_calc).quantize(Decimal('0.01'))

    subtotal = total + vat_total

    if subtotal < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PRICE / 100)
        free_delivery_calc = settings.FREE_DELIVERY_THRESHOLD - subtotal
    else:
        delivery = 0
        free_delivery_calc = 0

    grand_total = delivery + total + vat_total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'subtotal': subtotal,
        'vat_total': vat_total,
        'delivery': delivery,
        'free_delivery_calc': free_delivery_calc,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
