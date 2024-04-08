from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category,Subcategory
from .forms import ProductForm
from django.shortcuts import render, get_object_or_404
from accounts.models import  Review
from accounts.forms import ReviewForm

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
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def category_detail(request, category_id):
    category = get_object_or_404(Subcategory, pk=category_id)
    products = Product.objects.filter(subcategory=category)
    return render(request, 'products/category_detail.html', {'category': category, 'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # Assuming you have authentication set up
            review.save()
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm()
    return render(request, 'products/product_detail.html', {'product': product, 'reviews': reviews, 'form': form})


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


def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    return render(request, 'products/product_list.html', {'category': category, 'products': products})


def product_search(request):
    query = request.GET.get('query')
    category = request.GET.get('category')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if query:
        products = products.filter(title__icontains=query)

    if category:
        products = products.filter(category__name__icontains=category)

    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'products': products
    }
    return render(request, 'products/product_search_results.html', context)


