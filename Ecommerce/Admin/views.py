from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import CustomUser,ShippingAddress,Review
from Products.models import Category,Subcategory,Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Themes.models import ThemesSetting
from .forms import CategoryForm,SubCategoryForm ,SizeForm,DiscountForm,ColorForm,OrderForm
from Orders.models import Order,OrderIssue,OrderItem


def admin_main(request):
    registered_users_count = CustomUser.objects.filter(is_staff=False).count()
    products_count = Product.objects.all().count()
    orders_count = Order.objects.all().count()
    orders = Order.objects.all().order_by('-created_at')
    issue_reports = OrderIssue.objects.all()

    return render(request,"admin/admin_main.html",{'registered_users_count':registered_users_count,'products_count':products_count,'orders_count':orders_count,'orders':orders,"issue_reports":issue_reports})


def registered_users(request):
    registered_users=CustomUser.objects.filter(is_superuser=False, is_staff=False)
    return render(request,"admin/registeruser.html",{'registered_users': registered_users})


def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    shipping_addresses = user.shipping_addresses.all()
    return render(request, "admin/user_detail.html", {'user': user,'shipping_addresses':shipping_addresses})


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


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('order_status')
        
        if order.order_status != new_status: 
            old_status = order.order_status
            order.order_status = new_status
            order.save()
            
            subject = f'Status of your order has changed!'
            message = f'Your order status has been updated from {old_status} to "{new_status}".'
            recipient_email = order.user.email
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)
        return redirect('order_list')
        
 
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES)
        if form.is_valid():
            # Save the category here
            form.save()
            return redirect('add_product')  
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
    return render(request, 'admin/add_subcategory.html', {'form': form})
 

def add_size(request):
    if request.method == 'POST':
        form = SizeForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')  
    else:
        form = SizeForm()
    return render(request, 'admin/add_size.html', {'form': form})


def add_colors(request):
    if request.method == 'POST':
        form = ColorForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')  
    else:
        form = ColorForm()
    return render(request, 'admin/add_colors.html', {'form': form})


def add_discounts(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')  
    else:
        form = DiscountForm()
    return render(request, 'admin/add_discounts.html', {'form': form})

def order_issue(request):
    issue_reports = OrderIssue.objects.all()
    return render(request, 'admin/order_issues.html', {'issue_reports': issue_reports})


def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list', pk=pk)
    else:
        form = OrderForm(instance=order)
    return render(request, 'admin/edit_order.html', {'form': form})


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    order.delete()
    return redirect('order_list')  


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'admin/order_detail.html', {'order': order,'order_items':order_items})
