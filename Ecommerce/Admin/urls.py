from django.urls import path
from . import views

urlpatterns = [
    path('registered_users/', views.registered_users, name='registered_users'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('orders/', views.order_list, name='order_list'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin_main/',views.admin_main,name='admin_main'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('add_size/', views.add_size, name='add_size'),
    path('add_colors/', views.add_colors, name='add_colors'),
    path('customer/', views.customer, name='customer'),

    path('add_discounts/', views.add_discounts, name='add_discounts'),


]
