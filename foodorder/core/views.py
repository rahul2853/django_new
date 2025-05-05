from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse

from .models import Category, FoodItem, Order, OrderItem
from .forms import RegistrationForm, LoginForm
from .cart import Cart

import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from django.http import JsonResponse
from paypalrestsdk import Payment
import paypalrestsdk
def home(request):
    """Home page view"""
    categories = Category.objects.all()[:3]  # Get first 3 categories for display
    featured_items = FoodItem.objects.filter(is_available=True)[:4]
    
    context = {
        'categories': categories,
        'featured_items': featured_items,
    }
    return render(request, 'home.html', context)

def menu(request):
    """Menu page view"""
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    
    # Filter items by category if provided
    if category_id:
        try:
            category = Category.objects.get(id=category_id)
            food_items = FoodItem.objects.filter(category=category, is_available=True)
            active_category = int(category_id)
        except (ValueError, Category.DoesNotExist):
            food_items = FoodItem.objects.filter(is_available=True)
            active_category = None
    else:
        food_items = FoodItem.objects.filter(is_available=True)
        active_category = None
    
    context = {
        'categories': categories,
        'food_items': food_items,
        'active_category': active_category,
    }
    return render(request, 'menu.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Redirect to next parameter if available, otherwise to home
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

def cart_detail(request):
    """Cart detail view"""
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

@require_POST
def cart_add(request, food_id):
    """Add item to cart"""
    cart = Cart(request)
    food_item = get_object_or_404(FoodItem, id=food_id)
    
    # Default quantity is 1
    quantity = int(request.POST.get('quantity', 1))
    
    cart.add(food_item=food_item, quantity=quantity)
    
    # Return JSON response for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"{food_item.name} added to cart",
            'cart_total': len(cart),
        })
    
    # For regular form submission
    return redirect('cart_detail')

@require_POST
def cart_remove(request, food_id):
    """Remove item from cart"""
    cart = Cart(request)
    food_item = get_object_or_404(FoodItem, id=food_id)
    cart.remove(food_item)
    
    # Return JSON response for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"{food_item.name} removed from cart",
            'cart_total': len(cart),
        })
    
    # For regular form submission
    return redirect('cart_detail')

@require_POST
def cart_update(request, food_id):
    """Update item quantity in cart"""
    cart = Cart(request)
    food_item = get_object_or_404(FoodItem, id=food_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart.update(food_item=food_item, quantity=quantity)
    else:
        cart.remove(food_item)
    
    item_total = cart.get_item_total(food_item.id)
    cart_total = cart.get_total_price()
    
    # Return JSON response for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'item_total': str(item_total),
            'cart_total': str(cart_total),
            'item_count': len(cart),
        })
    
    # For regular form submission
    return redirect('cart_detail')

@login_required
def checkout(request):
    """Process checkout and create order"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        # Create a new order
        order = Order(
            user=request.user,
            total_price=cart.get_total_price()
        )
        order.save()
        
        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                food_item=item['food_item'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        # Clear the cart
        cart.clear()
        
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('home')
    
    return render(request, 'cart.html', {'cart': cart})



# for payment

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET
})

def create_payment(request):
    # Get cart total from the session or database
    total_amount = request.session.get('cart_total')  # Or calculate total from cart data
    
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/execute/",
            "cancel_url": "http://localhost:8000/payment/cancel/"
        },
        "transactions": [{
            "amount": {
                "total": str(total_amount),
                "currency": "USD"
            },
            "description": "Order payment"
        }]
    })

    # Create payment
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        return render(request, 'payment_failure.html', {'error': payment.error})

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment was successful
        return redirect('payment_success')
    else:
        # Payment failed
        return render(request, 'payment_failure.html', {'error': payment.error})

def cancel_payment(request):
    return render(request, 'payment_cancelled.html')


paypalrestsdk.configure({
    "mode": "sandbox",  # Change to 'live' for live environment
    "client_id": "Aa9NlQbHa-j6JAH3KpLlKWYgY4D0B9naDKISzGD98bxUwhPcXc3-klpytfwcoYupvq7h4c0AtikPo52x",
    "client_secret": "EIWjWu59ocU0hgmza0PoKWCboqcQ50hLlqlTwEobWBups-vY6Fb5yzGaHF6XeI9_3keI1nd1Opcp5LMA"
})

def create_payment(request):
    # Example for payment creation
    total_amount = 100.00  # Adjust based on your cart total

    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(total_amount),
                "currency": "USD"
            },
            "description": "Payment for Food Order"
        }],
        "redirect_urls": {
            "return_url": request.build_absolute_uri("/execute_payment/"),
            "cancel_url": request.build_absolute_uri("/cart/")
        }
    })

    if payment.create():
        # Find the approval_url for the user to approve the payment
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        return JsonResponse({"error": "Payment creation failed."}, status=400)
    
    
    def execute_payment(request):
     payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment successful
        return redirect('payment_success')  # Redirect to a success page
    else:
        # Payment failed
        return redirect('payment_failed')  # Redirect to a failure page
    
    
def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')

