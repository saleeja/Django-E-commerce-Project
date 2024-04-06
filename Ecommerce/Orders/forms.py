from django import forms
from .models import Order
from accounts.models import ShippingAddress


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField()
    class Meta:
        model = Order
        fields = ['items']


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name','phone_number','address_line1','address_line2','city', 'state', 'country', 'postal_code']
