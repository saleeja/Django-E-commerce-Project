from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Category,Subcategory
from .forms import ProductForm
from accounts.models import  Review
from accounts.forms import ReviewForm
from Products.models import Category,Subcategory,Product,Size,Color,Discount


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
    category = get_object_or_404(Category, pk=category_id)
    subcategories = Subcategory.objects.filter(category=category)
    products = Product.objects.filter(subcategory__category=category)

    # Extracting unique prices, sizes, and colors for filtering options
    prices = Product.objects.filter(subcategory__category=category).values_list('price', flat=True).distinct()
    sizes = Size.objects.all()
    colors = Color.objects.all()

    # Filter products based on size if selected
    selected_size = request.GET.get('size')
    if selected_size:
        products = products.filter(sizes__id=selected_size)

    # Filter products based on color if selected
    selected_color = request.GET.get('color')
    if selected_color:
        products = products.filter(colors__id=selected_color)

    # Filter products based on price range if selected
    selected_price = request.GET.get('price')
    if selected_price:
        if selected_price == '1':
            products = products.filter(price__lte=100)
        elif selected_price == '2':
            products = products.filter(price__range=(101, 200))
        elif selected_price == '3':
            products = products.filter(price__gte=201)

    discounts = Discount.objects.all()

    context = {
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'prices': prices,
        'sizes': sizes,
        'selected_size': selected_size,
        'colors': colors,
        'selected_color': selected_color,
        'discounts': discounts,
        'selected_price': selected_price,
    }
    return render(request, 'products/category_detail.html', context)



# def product_detail(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     cart = Cart.objects.filter(user=request.user)
#     reviews = Review.objects.filter(product=product)
#     if request.method == 'POST':
#         form = ReviewForm(request.POST, request.FILES)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = product
#             review.user = request.user  # Assuming you have authentication set up
#             review.save()
#             return redirect('product_detail', product_id=product_id)
#     else:
#         form = ReviewForm()
#     return render(request, 'products/product_detail.html', {'product': product, 'reviews': reviews, 'form': form,'cart':cart})


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

from django.db.models import Avg

def calculate_average_rating(product_id):
    # Query all reviews for the given product
    reviews = Review.objects.filter(product_id=product_id)

    # Calculate the average rating using Django's Avg aggregation function
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Return the average rating
    return average_rating



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)
    average_rating = calculate_average_rating(product_id)

    average_rating = float(average_rating) if average_rating is not None else 0.0

    if request.method == 'POST':
        # Handle form submission for adding a review
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  
            review.save()
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm()

    return render(request, 'products/product_detail.html', {'product': product, 'reviews': reviews, 'average_rating': average_rating, 'form': form})

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


