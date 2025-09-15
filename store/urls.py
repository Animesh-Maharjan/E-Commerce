from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='store-home'),
    path('shop/', views.shop, name='store-shop'),
    path('product/<slug>/', views.product_detail, name='product-detail'),

    path('add/', views.add_product, name='add-product'),
    path('seller/products/', views.seller_products, name='seller-products'),
    path('seller/reviews/', views.all_seller_reviews, name='all-seller-reviews'),
    path('seller/reviews/<int:product_id>/', views.seller_reviews, name='seller-reviews'),
    path('seller/products/update/<int:product_id>/', views.update_product, name='update-product'),
    path('seller/products/delete/<int:product_id>/', views.delete_product, name='delete-product'),
]

