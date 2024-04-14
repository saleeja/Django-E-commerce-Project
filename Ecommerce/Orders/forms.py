from django import forms
from .models import OrderIssue
from accounts.models import ShippingAddress

from django import forms

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity')


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name','phone_number','address_line1','address_line2','city', 'state', 'postal_code']

class OrderIssueForm(forms.ModelForm):
    class Meta:
        model = OrderIssue
        fields = ['description']