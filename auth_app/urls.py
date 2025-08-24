from django.urls import path
from auth_app import views

urlpatterns = [
    path('login/', views.login_user, name='authapp-login'),
    path('logout/', views.logout_user, name='authapp-logout'),
    path('register/', views.register, name='authapp-register'),
]