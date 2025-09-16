from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem
from cart.models import CartItem
from payments.models import Payment

@login_required
def checkout(request):
    """Simple checkout process"""
    # Get user's cart items
    cart_items = CartItem.objects.filter(cart__user=request.user)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart-view')
    
    # calculate total for display
    total_amount = sum(item.quantity * item.product.price for item in cart_items)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cash')
        # total_amount already calculated above

        order = Order.objects.create(
            user=request.user,
            customer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            customer_email=request.user.email,
            shipping_address=request.POST.get('address', ''),
            phone_number=request.POST.get('phone', ''),
            total_amount=total_amount,
            status='pending'
        )
        
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
       
        # create a Payment record. For Cash on Delivery we'll set status to pending
        Payment.objects.create(
            user=request.user,
            order=order,
            amount=total_amount,
            payment_method=payment_method,
            status='pending'
        )

        cart_items.delete()

        messages.success(request, f'Order placed successfully! Order ID: {order.id}')
        return redirect('order-detail', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart_items': cart_items, 'total_amount': total_amount})

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

@login_required
def seller_orders(request):
    """List orders containing seller's products"""
    if request.user.role != 'seller':
        messages.error(request, 'Access denied. Seller account required.')
        return redirect('store-home')
    
    # Get all order items for this seller's products
    order_items = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product').order_by('-order__order_date')
    
    # Group by order for better display
    orders_dict = {}
    for item in order_items:
        order = item.order
        if order.id not in orders_dict:
            orders_dict[order.id] = {
                'order': order,
                'items': [],
                'seller_total': 0
            }
        orders_dict[order.id]['items'].append(item)
        orders_dict[order.id]['seller_total'] += item.total_price
    
    orders_data = list(orders_dict.values())
    
    return render(request, 'orders/seller_orders.html', {'orders_data': orders_data})

@login_required
@require_POST
def confirm_order(request, order_id):
    """Seller confirms an order"""
    if request.user.role != 'seller':
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    try:
        # Get the order and verify seller has products in it
        order = get_object_or_404(Order, id=order_id)
        
        # Check if seller has products in this order
        seller_items = OrderItem.objects.filter(
            order=order,
            product__seller=request.user
        )
        
        if not seller_items.exists():
            return JsonResponse({'success': False, 'message': 'No products from your store in this order'})
        
        # Update order status to confirmed if it's pending
        if order.status == 'pending':
            order.status = 'confirmed'
            order.save()
            
            messages.success(request, f'Order #{order.id} has been confirmed successfully!')
            return JsonResponse({'success': True, 'message': 'Order confirmed successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Order is not in pending status'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def seller_order_detail(request, order_id):
    """Seller view of order details"""
    if request.user.role != 'seller':
        messages.error(request, 'Access denied. Seller account required.')
        return redirect('store-home')
    
    order = get_object_or_404(Order, id=order_id)
    
    # Get only items from this seller
    seller_items = OrderItem.objects.filter(
        order=order,
        product__seller=request.user
    ).select_related('product')
    
    if not seller_items.exists():
        messages.error(request, 'No products from your store in this order.')
        return redirect('seller-orders')
    
    seller_total = sum(item.total_price for item in seller_items)
    
    context = {
        'order': order,
        'seller_items': seller_items,
        'seller_total': seller_total,
    }
    
    return render(request, 'orders/seller_order_detail.html', context)

@login_required
@require_POST
def customer_cancel_order(request, order_id):
    """Customer cancels their own order"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if not order.can_be_cancelled_by_customer():
            return JsonResponse({
                'success': False, 
                'message': 'This order cannot be cancelled. Orders can only be cancelled when pending or confirmed.'
            })
        
        if order.cancel_order(cancelled_by='customer'):
            messages.success(request, f'Order #{order.id} has been cancelled successfully.')
            return JsonResponse({'success': True, 'message': 'Order cancelled successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Unable to cancel order'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def seller_cancel_order(request, order_id):
    """Seller cancels an order containing their products"""
    if request.user.role != 'seller':
        return JsonResponse({'success': False, 'message': 'Access denied'})
    
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Check if seller has products in this order
        seller_items = OrderItem.objects.filter(
            order=order,
            product__seller=request.user
        )
        
        if not seller_items.exists():
            return JsonResponse({'success': False, 'message': 'No products from your store in this order'})
        
        if not order.can_be_cancelled_by_seller():
            return JsonResponse({
                'success': False, 
                'message': 'This order cannot be cancelled. Orders can only be cancelled when pending or confirmed.'
            })
        
        if order.cancel_order(cancelled_by='seller'):
            messages.success(request, f'Order #{order.id} has been cancelled successfully.')
            return JsonResponse({'success': True, 'message': 'Order cancelled successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Unable to cancel order'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
