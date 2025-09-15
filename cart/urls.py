from django.urls import path
from cart import views

urlpatterns = [
    path('', views.cart_view, name='cart-view'),
    path('add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.checkout, name='cart-checkout'),
]
