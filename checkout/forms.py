from django import forms
from .models import Order
from django_countries.widgets import CountrySelectWidget


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email',
                  'street_address1', 'street_address2',
                  'town_or_city', 'county', 'postcode',
                  'country', 'phone_number',)
        widgets = {
            'country': CountrySelectWidget(
                attrs={
                    'class': 'stripe-style-input'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """ Adds placeholdes and classes, removes auto-generated
        labels and sets autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'town_or_city': 'Town/City',
            'county': 'County or State',
            'postcode': 'Postal Code',
            'phone_number': 'Phone Number',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
                self.fields[field].widget.attrs['class'] = 'stripe-style-input'
                self.fields[field].label = (
                    placeholders[field].replace(' *', '')
                )
