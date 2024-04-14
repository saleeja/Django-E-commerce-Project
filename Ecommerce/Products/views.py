from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category,Subcategory
from .forms import ProductForm
from accounts.models import  Review
from accounts.forms import ReviewForm
from Products.models import Category,Subcategory,Product,Size,Color,Discount
from Orders.models import Cart
from django.db.models import Avg
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


def edit_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/edit_product.html', {'form': form})


def delete_product(request, product_id):
    product = Product.objects.get(pk=product_id)
    product.delete()
    return redirect('product_list')


def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/product_list.html', {'products': products})


def category_detail(request, category_id):
    category = get_object_or_404(Subcategory, pk=category_id)
    products = Product.objects.filter(subcategory=category)

    for product in products:
        product.average_rating = product.review_set.aggregate(Avg('rating'))['rating__avg']

    if request.user.is_authenticated:
        product_count_in_cart = Cart.objects.filter(user=request.user).values('product').distinct().count()
    else:
        product_count_in_cart = 0
  
    return render(request, 'products/category_detail.html', {'category': category, 'products': products,'product_count_in_cart':product_count_in_cart})


def review_list(request, product_id):
    product = Product.objects.get(pk=product_id)
    reviews = Review.objects.filter(product=product)
    
    # Calculate overall rating
    total_reviews = reviews.count()
    if total_reviews > 0:
        total_stars = sum([review.rating for review in reviews])
        overall_rating = total_stars / total_reviews
    else:
        overall_rating = None

    return render(request, 'products/product_detail.html', {'product': product, 'reviews': reviews, 'overall_rating': overall_rating})


def calculate_average_rating(product_id):
    reviews = Review.objects.filter(product_id=product_id)
    # Calculate the average rating using Django's Avg aggregation function
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    return average_rating

def product_review(request, product_id):
    product = Product.objects.get(pk=product_id)
    average_rating = calculate_average_rating(product_id)
    return render(request, 'products/product_detail.html', {'product': product, 'average_rating': average_rating})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)
    average_rating = calculate_average_rating(product_id)
    average_rating = float(average_rating) if average_rating is not None else 0.0
    if request.user.is_authenticated:
        product_count_in_cart = Cart.objects.filter(user=request.user).values('product').distinct().count()
    else:
        product_count_in_cart = 0
    # Check if available quantity is less than 3
    if product.available_quantity < 3:
        messages.info(request, f'Only {product.available_quantity} left!')

    # Check if available quantity is zero 
    if product.available_quantity == 0 :
        messages.error(request, 'This product is out of stock.')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  
            review.save()
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm()

    return render(request, 'products/product_detail.html', {'product_count_in_cart':product_count_in_cart,'product': product, 'reviews': reviews, 'average_rating': average_rating, 'form': form})


def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'products/product_list.html', {'category': category, 'products': products})


def search_products(query):
    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(category__name__icontains=query) | 
        Q(subcategory__name__icontains=query)  
    ).distinct()
    return products


def product_search(request):
    query = request.GET.get('q')
    if query:
        products = search_products(query)
    else:
        products = Product.objects.all() 
    for product in products:
        product.average_rating = product.review_set.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'products/product_search_results.html', {'products': products, 'query': query})
