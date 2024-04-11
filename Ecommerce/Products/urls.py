from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    # path('products/<int:category_id>/', views.product_list, name='category_product_list'),
    path('add_product', views.add_product, name='add_product'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
    path('search/', views.product_search, name='product_search'),
    path('review_list/', views.review_list, name='review_list'),

]
