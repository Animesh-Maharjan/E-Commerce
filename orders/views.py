from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import CartItem

@login_required
def checkout(request):
    """Simple checkout process"""
    # Get user's cart items
    cart_items = CartItem.objects.filter(cart__user=request.user)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart-view')
    
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            customer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            customer_email=request.user.email,
            shipping_address=request.POST.get('address', ''),
            phone_number=request.POST.get('phone', ''),
            total_amount=sum(item.quantity * item.product.price for item in cart_items),
            status='pending'
        )
        
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
       
        cart_items.delete()
        
        messages.success(request, f'Order placed successfully! Order ID: {order.id}')
        return redirect('order-detail', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart_items': cart_items})

@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_list(request):
    """List user's orders"""
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/order_list.html', {'orders': orders})
