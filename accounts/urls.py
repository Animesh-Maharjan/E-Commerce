from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_user, name='accounts-login'),
    path('logout/', views.logout_user, name='accounts-logout'),
    path('register/', views.register, name='accounts-register'),

    path('customer/dashboard/', views.customer_dashboard, name='customer-dashboard'),
    path('seller/dashboard/', views.seller_dashboard, name='seller-dashboard'),
]