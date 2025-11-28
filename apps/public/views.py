from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse


def home(request):
    """Landing page для неаутентифицированных пользователей"""
    if request.user.is_authenticated:
        # Редирект на роль-специфичную страницу
        if request.user.role == 'dean':
            return redirect('dean:dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_panel:dashboard')
        elif request.user.role == 'zamdekan':
            return redirect('zamdekan:dashboard')
        elif request.user.role == 'teacher':
            return redirect('teacher:dashboard')
    
    return render(request, 'public/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Пас аз login ба dashboard-и мувофиқ равон мекунад
            if user.role == 'dean':
                return redirect('dean:index')
            elif user.role == 'admin':
                return redirect('admin_panel:dashboard')
            elif user.role == 'zamdekan':
                return redirect('zamdekan:index')
            elif user.role == 'teacher':
                return redirect('teacher:index')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Username ё password нодуруст аст')
    return render(request, 'public/login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('login'))
