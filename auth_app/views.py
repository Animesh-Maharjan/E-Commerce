from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here.

def login_user(request):
    if request.method =='GET':
        return render(request, 'auth_app/login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.Get.get('next')
            if next_url is not None:
                return redirect(next_url)
            return redirect('store-home')
        else:
            return redirect('authapp-login')

def logout_user(request):
    logout(request)
    return redirect('authapp-login')

def register(request):
    if request.method == 'GET':
        return render(request, 'auth_app/register.html')
    else:
        fn = request.POST['firstname']
        ln = request.POST['lastname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(first_name=fn, last_name=ln, email=email, username=username, password=password)

        return redirect('authapp-login')