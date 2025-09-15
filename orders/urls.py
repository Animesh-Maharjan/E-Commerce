from django.urls import path
from orders import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order-list'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),
]
