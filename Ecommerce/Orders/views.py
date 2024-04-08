from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import ShippingAddress
from django.contrib.auth.decorators import login_required
from .models import Order,Cart
from Products.models import Product
from django.shortcuts import get_object_or_404
from .forms import ShippingAddressForm
from django.core.mail import send_mail
from django.conf import settings


from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart
from .forms import AddToCartForm

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            # Check if the product is already in the cart for the current user
            cart, created = Cart.objects.get_or_create(user=request.user, product=product)
            if created:
                # If the product is not in the cart, create a new entry
                cart.quantity = quantity
                cart.save()
            else:
                # If the product is already in the cart, update the quantity
                cart.quantity += quantity
                cart.save()
            return redirect('cart')
    else:
        form = AddToCartForm()
    return render(request, 'orders/cart.html', {'product': product, 'form': form})


# @login_required
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user, product=product)
#     if not created:
#         cart.quantity += 1
#         cart.save()
#     return redirect('cart')


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
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            new_shipping_address = form.save(commit=False)
            new_shipping_address.user = request.user
            new_shipping_address.save()
            return redirect('checkout')  
    else:
        form = ShippingAddressForm()

    return render(request, 'orders/checkout.html', {'shipping_address': shipping_address, 'address_exists': address_exists, 'cart_items': cart_items, 'total_price': total_price, 'form': form})


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
def place_order(request):
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_amount=0,  
            shipping_address=request.user.shippingaddress_set.latest('id'),  
            payment_method=request.POST.get('payment_method'),  
            order_status='Pending'
        )
        send_order_confirmation_email(request.user.email, order)
        return redirect('order_confirmation', order_id=order.id)
    else:
        return redirect('checkout')

@login_required
def payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None

    order_summary = {
        'items': total_price,
    }
    return render(request, 'orders/payment.html', {'cart_items': cart_items, 'order_summary': order_summary, 'shipping_address': shipping_address})


def place_order(request):
    return redirect('order_confirmation')

@login_required
def order_confirmation(request):
    return render(request, 'orders/order_confirmation.html')



from django.shortcuts import render, redirect
from .models import Product, Wishlist

from django.shortcuts import render, redirect
from .models import Product, Wishlist

def add_to_wishlist(request, product_id):
    # Assuming you have a Product model
    product = Product.objects.get(pk=product_id)
    
    # Assuming you have a Wishlist model and the user is logged in
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product)
        wishlist.save()
        # Optionally, you may want to redirect the user to a different page after adding to the wishlist
        return redirect('wishlist')
    else:
        # Handle the case when the user is not authenticated (e.g., redirect to login page)
        return redirect('login_page')

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.products.remove(product)
        return redirect('wishlist')
    else:
        return redirect('login')  # Redirect to login page if user is not authenticated

def wishlist(request):
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        return render(request, 'orders/wishlist.html', {'wishlist': wishlist})
    else:
        return redirect('login')  # Redirect to login page if user is not authenticated
 # Redirect to login page if user is not authenticated
