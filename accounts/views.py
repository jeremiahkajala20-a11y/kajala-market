from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import BuyerRegisterForm, SellerRegisterForm

def register_buyer(request):
    if request.method == 'POST':
        form = BuyerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'buyer'
            user.is_approved = True
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Kajala Market.')
            return redirect('home')
    else:
        form = BuyerRegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Buyer'})

def register_seller(request):
    if request.method == 'POST':
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'seller'
            user.is_approved = False
            user.save()
            messages.success(request, 'Registration submitted! Wait for admin approval.')
            return redirect('login')
    else:
        form = SellerRegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'role': 'Seller'})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == 'seller' and user.is_approved:
                return redirect('seller_dashboard')
            elif user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})