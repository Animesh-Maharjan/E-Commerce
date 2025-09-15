from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser 
from django.contrib.auth.decorators import login_required

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
    return render(request, 'dashboard/customer_dashboard.html')

@login_required
def seller_dashboard(request):
    return render(request, 'dashboard/seller_dashboard.html')