from django.urls import path
from .views import *

urlpatterns = [
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('remove_from_cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('edit_shipping_address/<int:address_id>/', edit_shipping_address, name='edit_shipping_address'),
    path('remove_shipping_address/<int:address_id>/', remove_shipping_address, name='remove_shipping_address'),
    path('add_to_wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', wishlist, name='wishlist'),
    path('add_to_cart_from_wishlist/<int:product_id>/', add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),
    path('wishlist/', wishlist, name='wishlist'),
    path('confirm_order/', confirm_order, name='confirm_order'),
    path('stripe_payment/', stripe_payment, name='stripe_payment'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('my_orders/', my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', order_detail, name='order_detail'),
    path('cancel_order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('report_issue/<int:order_id>/', report_issue, name='report_issue'),
    path('download_invoice/<int:order_id>/', download_invoice, name='download_invoice'),


]



