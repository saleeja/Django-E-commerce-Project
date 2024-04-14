from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import ShippingAddress,Review
from django.contrib.auth.decorators import login_required
from .models import Order,Cart,OrderItem
from Products.models import Product
from .forms import ShippingAddressForm,OrderIssueForm
from django.core.mail import send_mail
from django.conf import settings
from .forms import AddToCartForm
from .models import  Wishlist
from django.contrib import messages
import time


@login_required(login_url='login_user')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    max_quantity = 6  
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > max_quantity:
                messages.error(request, f"Sorry, you can only add up to {max_quantity} units of this product.")
            elif product.available_quantity == 0:
                messages.error(request, "This product is out of stock.")
            elif quantity > product.available_quantity:
                messages.error(request, f"Sorry, only {product.available_quantity} units available.")
           
            else:
                # Store product ID and quantity in session
                if 'cart' not in request.session:
                    request.session['cart'] = {}
                cart = request.session['cart']
                if str(product_id) in cart:
                    cart[str(product_id)] += quantity
                else:
                    cart[str(product_id)] = quantity
                request.session['cart'] = cart

                # Check if the product is already in the cart for the current user
                cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
                if created:
                    # Ensure the quantity doesn't exceed 6
                    cart_item.quantity = min(quantity, 6)
                else:
                    # Update the quantity, ensuring it doesn't exceed 6
                    cart_item.quantity = min(cart_item.quantity + quantity, 6)
                cart_item.save()

                
                messages.success(request, "Product added to cart successfully.")
                time.sleep(2)
                return redirect('cart')  
    else:
        form = AddToCartForm()

    # Update availability status based on available quantity
    if product.available_quantity <= 0:
        product.is_available = False
        product.save()

    # Count the number of unique products in the user's cart
    product_count_in_cart = Cart.objects.filter(user=request.user).values('product').distinct().count()

    return render(request, 'orders/cart.html', {'product': product, 'form': form, 'product_count_in_cart': product_count_in_cart, 'cart': request.session.get('cart', {})})


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
        item.save() 
    
    total_price = sum(item.total_price for item in cart_items)
    
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def update_cart_quantity(request, cart_item_id, action):
    if request.method == 'POST':
        cart_item = Cart.objects.get(id=cart_item_id)

        if action == 'plus':
            if cart_item.quantity < cart_item.product.available_quantity:  # Check if adding one more item exceeds the available quantity
                if cart_item.quantity < 6:  
                    cart_item.quantity += 1
                else:
                    messages.warning(request, "You can only add up to 6 units of this product.")
            else:
                messages.warning(request, "The available quantity for this product has been reached.")
        elif action == 'minus' and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.total_price = cart_item.product.price * cart_item.quantity
        cart_item.save()

        return redirect('cart')
    else:
        return redirect('cart')



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
        item.product.available_quantity -= item.quantity
        item.product.save()
    order.order_status = 'Order Confirmed'
    order.save()
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


from django.http import HttpResponseRedirect

@login_required(login_url='login_user')
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

        # Get the referring page's URL or redirect to a default page if not available
        next_page = request.META.get('HTTP_REFERER', 'default_page_url')
        return HttpResponseRedirect(next_page)
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
        reviews = Review.objects.all()
        product_count_in_cart = Cart.objects.filter(user=request.user).values('product').distinct().count()

        return render(request, 'orders/wishlist.html', {'wishlist': wishlist,'reviews':reviews,'product_count_in_cart':product_count_in_cart})
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

        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.products.remove(product)
        
        
        return redirect('cart')
    else:
        return redirect('login_page')


@login_required(login_url='login_user')
def add_to_wishlist_from_cart(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Check if the product is already in the wishlist
        if not wishlist.products.filter(pk=product_id).exists():
            wishlist.products.add(product)
            wishlist.save()
            messages.success(request, "Product added to your wishlist.")
        else:
            messages.info(request, "This product is already in your wishlist.")

        # Remove the product from the cart after adding it to the wishlist
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            cart_item.delete()
            messages.success(request, "Product removed from your cart.")
        
        return redirect('cart')
    else:
        return redirect('login_page')


def my_orders(request,order_id=None):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
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

        return render(request, 'orders/order_cancelled.html')

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
            return render(request, 'orders/report_issue_success.html')

    else:
        form = OrderIssueForm()
    return render(request, 'orders/report_issue.html', {'form': form})


# ___________________________________________________________________________________________________________


import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_path, context_dict):
    """
    Generate a PDF file from a Django template and context data.
    
    Args:
        template_path (str): The path to the template file.
        context_dict (dict): The context data to be rendered in the template.
        
    Returns:
        HttpResponse: The PDF file as an HTTP response.
    """
    # Load template
    template = get_template(template_path)
    html = template.render(context_dict)

    # Create PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    # Check if PDF generation was successful
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="generated_pdf.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)

def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items,
    }

    return render_to_pdf('orders/invoice.html', context)
