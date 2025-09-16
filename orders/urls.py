from django.urls import path
from orders import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order-list'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),
    path('seller-orders/', views.seller_orders, name='seller-orders'),
    path('seller-order-detail/<int:order_id>/', views.seller_order_detail, name='seller-order-detail'),
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm-order'),
    path('customer-cancel-order/<int:order_id>/', views.customer_cancel_order, name='customer-cancel-order'),
    path('seller-cancel-order/<int:order_id>/', views.seller_cancel_order, name='seller-cancel-order'),
]
