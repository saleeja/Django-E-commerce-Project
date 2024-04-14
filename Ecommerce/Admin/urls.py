from django.urls import path
from . import views

urlpatterns = [
    path('registered_users/', views.registered_users, name='registered_users'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('orders/', views.order_list, name='order_list'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin_main/',views.admin_main,name='admin_main'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_subcategory/', views.add_subcategory, name='add_subcategory'),
    path('add_size/', views.add_size, name='add_size'),
    path('add_colors/', views.add_colors, name='add_colors'),
    path('order_issue/', views.order_issue, name='order_issue'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order/<int:pk>/edit/', views.edit_order, name='edit_order'),
    path('order/<int:pk>/delete/', views.delete_order, name='delete_order'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('add_discounts/', views.add_discounts, name='add_discounts'),


]
