# Generated by Django 3.2.25 on 2025-03-23 02:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='has_shoe_sizes',
            new_name='has_shoesizes',
        ),
    ]
