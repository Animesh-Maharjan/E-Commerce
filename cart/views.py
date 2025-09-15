from django.shortcuts import render, redirect, get_object_or_404
from cart.models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from store.models import Product
from orders.models import Order, OrderItem

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, "cart/cart.html", {"cart_items": cart_items, "total_price": total_price})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart-view")

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect("cart-view")

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect("cart-view")  # nothing to checkout

    if request.method == "POST":
        order = Order.objects.create(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )
        cart_items.delete()  # clear cart after placing order
        return redirect("order-list")

    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, "cart/checkout.html", {"cart_items": cart_items, "total_price": total_price})
