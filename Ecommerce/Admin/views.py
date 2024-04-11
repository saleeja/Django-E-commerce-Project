from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import CustomUser,ShippingAddress,Review
from Products.models import Category,Subcategory,Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Themes.models import ThemesSetting
from .forms import CategoryForm,SubCategoryForm ,SizeForm,DiscountForm,ColorForm
from Orders.models import Order


def admin_main(request):
    registered_users_count = CustomUser.objects.filter(is_staff=False).count()
    products_count = Product.objects.all().count()
    orders_count = Order.objects.all().count()
    orders = Order.objects.all().order_by('-created_at')
    
    return render(request,"admin/admin_main.html",{'registered_users_count':registered_users_count,'products_count':products_count,'orders_count':orders_count,'orders':orders})


def registered_users(request):
    registered_users=CustomUser.objects.filter(is_superuser=False, is_staff=False)
    return render(request,"admin/registeruser.html",{'registered_users': registered_users})


def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        user.username = username
        user.email = email
        user.save()
        messages.success(request, 'User details updated successfully.')
        return redirect('registered_users')
    else:
        return render(request, 'accounts/edit_profile.html', {'user': user})


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        # Delete the user
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('registered_users')
    

def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    return render(request, 'admin/order_list.html', {'orders': orders})

def customer(request):
    return render (request,'admin/customers.html')

@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('order_status')
        
        if order.order_status != new_status: 
            old_status = order.order_status
            order.order_status = new_status
            order.save()
            
            # Send message based on status change
            subject = f'Status of your order has changed!'
            message = f'Your order status has been updated from {old_status} to "{new_status}".'
            recipient_email = order.user.email
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)

 
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES)
        if form.is_valid():
            # Save the category here
            form.save()
            return redirect('add_product')  # Redirect to the homepage after adding the category
    else:
        form = CategoryForm()
    return render(request, 'admin/add_category.html', {'form': form})


def add_subcategory(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST,request.FILES)
        if form.is_valid():
            # Save the category here
            form.save()
            return redirect('add_product')  
    else:
        form = CategoryForm()
    return render(request, 'admin/add_category.html', {'form': form})
 

def add_size(request):
    if request.method == 'POST':
        form = SizeForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')  
    else:
        form = SizeForm()
    return render(request, 'admin/add_category.html', {'form': form})

def add_colors(request):
    if request.method == 'POST':
        form = ColorForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')  
    else:
        form = ColorForm()
    return render(request, 'admin/add_category.html', {'form': form})


def add_discounts(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')  
    else:
        form = DiscountForm()
    return render(request, 'admin/add_category.html', {'form': form})