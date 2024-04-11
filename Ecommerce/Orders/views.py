from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import ShippingAddress
from django.contrib.auth.decorators import login_required
from .models import Order,Cart,OrderItem
from Products.models import Product
from .forms import ShippingAddressForm,OrderIssueForm
from django.core.mail import send_mail
from django.conf import settings
from .forms import AddToCartForm
from .models import  Wishlist
from django.contrib import messages


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > product.available_quantity:
                # If selected quantity exceeds available quantity, display out of stock message
                messages.error(request, f"Sorry, only {product.available_quantity} units available.")
            else:
                # Check if the product is already in the cart for the current user
                cart, created = Cart.objects.get_or_create(user=request.user, product=product)
                if created:
                    cart.quantity = quantity
                else:
                    cart.quantity += quantity
                cart.save()
                product.available_quantity -= quantity  # Reduce available quantity
                product.save()
                messages.success(request, "Product added to cart successfully.")
                return redirect('cart')  # Redirect to cart page after adding to cart
    else:
        form = AddToCartForm()

    # Update availability status based on available quantity
    if product.available_quantity <= 0:
        product.is_available = False
        product.save()

    return render(request, 'orders/cart.html', {'product': product, 'form': form})


@login_required
def remove_from_cart(request, cart_item_id):
    cart = Cart.objects.get(pk=cart_item_id)
    cart.delete()
    return redirect('cart')


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def edit_shipping_address(request, address_id):
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('checkout')
    else:
        form = ShippingAddressForm(instance=address)
    
    return render(request, 'orders/edit_shipping_address.html', {'form': form, 'address': address})


@login_required
def remove_shipping_address(request, address_id):
    address = ShippingAddress.objects.get(pk=address_id)
    address.delete()
    return redirect('checkout')



def send_order_confirmation_email(email, order):
    subject = 'Order Confirmation'
    message = f'Your order (ID: {order.id}) has been successfully placed.'
    recipient_list = [email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
        address_exists = True
    except ShippingAddress.DoesNotExist:
        shipping_address = None
        address_exists = False

    if request.method == 'POST':
        # Handle the submission of the shipping address form
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            new_shipping_address = form.save(commit=False)
            new_shipping_address.user = request.user
            new_shipping_address.save()
            return redirect('checkout')  

        # Handle the selection of payment method
        payment_method = request.POST.get('payment_method')
        if payment_method == 'stripe':
            return redirect('stripe_payment')  
        elif payment_method == 'cod':
            order = confirm_order(request.user, cart_items, shipping_address, total_price, payment_method)
            cart_items.delete() 
            return redirect('order_confirmation')  

    else:
        form = ShippingAddressForm()

    return render(request, 'orders/checkout.html', {'shipping_address': shipping_address, 'address_exists': address_exists, 'cart_items': cart_items, 'total_price': total_price, 'form': form})


def confirm_order(user, cart_items, shipping_address, total_price, payment_method):
    # Create a new order instance
    order = Order.objects.create(
        user=user,
        total_amount=total_price,
        shipping_address=shipping_address,
        payment_method=payment_method,
    )

    # Create order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price * item.quantity,
        )

    return order


import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def stripe_payment(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')

        try:
            cart_items = Cart.objects.filter(user=request.user)
            total_amount = sum(item.product.price * item.quantity for item in cart_items)
            shipping_address = ShippingAddress.objects.get(user=request.user)
          

            charge = stripe.Charge.create(
                amount=total_amount * 100, 
                currency='usd',
                description='Example charge',
                source=token,
            )
            
            if charge == 'succeeded':
                new_order = confirm_order(request.user,shipping_address, cart_items, total_amount, 'stripe')
                cart_items.delete()
                return redirect('order_confirmation')
            else:
                return render(request, 'orders/payment_failure.html')

        except stripe.error.CardError as e:
            return render(request, 'orders/payment_failure.html', {'error_message': e.error.message})
        except Exception as e:
            return render(request, 'orders/payment_error.html', {'error_message': str(e)})
    return render(request, 'orders/stripe_payment.html')



def order_confirmation(request):
    latest_order = Order.objects.filter(user=request.user).latest('created_at')
    return render(request, 'orders/order_confirmation.html', {'order': latest_order})


def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if not wishlist.products.filter(pk=product_id).exists():
            wishlist.products.add(product)
            wishlist.save()
            messages.success(request, "Product added to your wishlist.")
        else:
            messages.info(request, "This product is already in your wishlist.")
        
        return redirect('product_detail', product_id=product_id)
    else:
        return redirect('login_page')


def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.products.remove(product)
        messages.success(request, "Product removed from your wishlist.")
        return redirect('wishlist')
    else:
        return redirect('login_page') 

def wishlist(request):
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        return render(request, 'orders/wishlist.html', {'wishlist': wishlist})
    else:
        return redirect('login_page')

def add_to_cart_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
        
        # If the product is already in the cart, increase the quantity
        if not created:
            cart.quantity += 1
            cart.save()
            messages.success(request, "Product quantity updated in your cart.")
        else:
            messages.success(request, "Product added to your cart.")
        
        return redirect('cart')
    else:
        return redirect('login_page')


def my_orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Prepare data to pass to the template
    data = []
    for order in user_orders:
        products  = OrderItem.objects.filter(order=order).order_by('-id')
        data.append((products , order))

    return render(request, "orders/my_order.html", {'data': data})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.order_status = 'Cancelled'
        order.save()

        # Send email notification to the user
        subject = 'Order Cancellation Confirmation'
        message = f'Your order with ID {order_id} has been cancelled.'
        recipient_email = order.user.email
        sender_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, sender_email, [recipient_email])

        return redirect('order_detail', order_id=order_id)
    return render(request, 'orders/my_order.html', {'order': order})


def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})

def report_issue(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        form = OrderIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.order = order
            issue.reported_by = request.user
            issue.save()
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderIssueForm()
    return render(request, 'orders/report_issue.html', {'form': form})
