from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'image', 'category','subcategory','sizes','colors','discount', 'available_quantity']
        widgets = {
                    'sizes': forms.CheckboxSelectMultiple,  
                    'colors': forms.CheckboxSelectMultiple(),
                    'discount':forms.NumberInput(),
                }

        

class ProductSearchForm(forms.Form):
    title = forms.CharField(required=False)
    category = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
