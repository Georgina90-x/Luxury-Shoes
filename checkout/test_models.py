from django.test import TestCase

from products.models import Product
from luxury_shoes import settings
from .models import Order
from .models import OrderLineItem


class TestCheckoutModels(TestCase):
    """
    Checkout Models Test
    """
    def setUp(self):
        """
        Creates a checkout test model for users, products and an order.
        """

        Product.objects.create(
            name='Test Name',
            price='9.99',
            sku='123456',
            description='Test Description',
        )

        Order.objects.create(
            full_name='mr test',
            email='test@test.com',
            phone_number='123345',
            country='GB',
            town_or_city='Test City',
            street_address1='Test Street',
        )

    def test_order_str_method(self):
        """
        Order String Method
        """
        order = Order.objects.get(email='test@test.com')
        self.assertEqual(str(order), order.order_number)
