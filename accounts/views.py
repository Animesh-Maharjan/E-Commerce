from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser 
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from store.models import Product, Review
from orders.models import Order
from cart.models import CartItem

# Create your views here.
def login_user(request):
    if request.method =='GET':
        return render(request, 'accounts/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == "customer":
                return redirect('customer-dashboard')
            elif user.role == "seller":
                return redirect('seller-dashboard')
            else:
                return redirect('store-home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('accounts-login')

def logout_user(request):
    logout(request)
    return redirect('accounts-login')

def register(request):
    if request.method == 'GET':
        return render(request, 'accounts/register.html')
    else:
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']  

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/register.html')

        CustomUser.objects.create_user(
            first_name=fn,
            last_name=ln,
            email=email,
            username=username,
            password=password,
            role=role
        )
        messages.success(request, "Registration successful. Please log in.")
        return redirect('accounts-login')

@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        return redirect('store-home')
    
    # Get customer statistics
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='pending').count()
    completed_orders = Order.objects.filter(user=request.user, status='delivered').count()
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-order_date')[:5]
    
    # Get cart items count
    cart_items_count = CartItem.objects.filter(cart__user=request.user).count()
    
    # Get total spent (sum of completed orders)
    total_spent = Order.objects.filter(
        user=request.user, 
        status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'recent_orders': recent_orders,
        'cart_items_count': cart_items_count,
        'total_spent': total_spent,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)

@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('store-home')
    
    # Get seller statistics
    my_products = Product.objects.filter(seller=request.user)
    total_products = my_products.count()
    active_products = my_products.filter(available=True).count()
    low_stock_products = my_products.filter(stock__lt=5, available=True).count()
    
    # Get recent products
    recent_products = my_products.order_by('-created')[:5]
    
    # Get reviews statistics
    total_reviews = Review.objects.filter(product__seller=request.user).count()
    avg_rating = Review.objects.filter(product__seller=request.user).aggregate(
        avg_rating=Sum('rating')
    )['avg_rating']
    if avg_rating and total_reviews:
        avg_rating = round(avg_rating / total_reviews, 1)
    else:
        avg_rating = 0
    
    # Get recent reviews
    recent_reviews = Review.objects.filter(
        product__seller=request.user
    ).select_related('product', 'customer').order_by('-created')[:5]
    
    # Get orders containing seller's products
    from orders.models import OrderItem
    seller_orders = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product').order_by('-order__order_date')[:5]
    
    # Calculate total revenue (from delivered orders)
    total_revenue = OrderItem.objects.filter(
        product__seller=request.user,
        order__status__in=['delivered', 'shipped']
    ).aggregate(
        revenue=Sum('price')
    )['revenue'] or 0
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'recent_products': recent_products,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'recent_reviews': recent_reviews,
        'seller_orders': seller_orders,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard/seller_dashboard.html', context)