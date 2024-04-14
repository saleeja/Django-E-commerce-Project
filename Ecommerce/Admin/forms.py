
from django import forms
from Products.models import Category,Subcategory,Size,Color,Discount

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','image']  

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name','category','image'] 


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name']


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['discount']



from Orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['total_amount', 'shipping_address', 'payment_method', 'order_status']  
