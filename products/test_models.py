from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase

from products.models import Category, Product


class TestProductModels(TestCase):
    """
    Test Product Models
    """
    def setUp(self):
        test_user = User.objects.create_user(
            username='test_user', password="test_password")

        Category.objects.create(
            name='test_category', friendly_name='test category'
        )

        product = Product.objects.create(
            name='Product Name',
            price='99.99',
            sku='123456',
            description='Test Description',
        )

    def test_product_str_method(self):
        """
        Product String Method
        """
        product = Product.objects.get(sku='123456')
        self.assertEqual((product.__str__()), product.name)

    def test_category_str_method(self):
        """
        Category String Method
        """
        category = Category.objects.get(name='test_category')
        self.assertEqual((category.__str__()), category.name)
        self.assertEqual(
            category.get_friendly_name(), category.friendly_name)
