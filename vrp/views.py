from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from vrp.forms import SignupForm, LoginForm


def signup_view(request):
    """Signup / registration view"""
    if request.user.is_authenticated:
        return redirect("dashboard", path="")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        password_confirm = form.cleaned_data["confirm_password"]

        if password != password_confirm:
            messages.error(request, "Passwords don't match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect("dashboard", path="")

    return render(request, "index.html", {"form": form})



def login_view(request):
    """Login view"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard", path="")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username} 👋")
            return redirect("dashboard", path="")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "index.html")



def home(request, *args, **kwargs):
    return render(request, 'index.html', context={})

@login_required(login_url='/login/')  # redirect to login page if not logged in
def dashboard(request, *args, **kwargs):
    return render(request, 'index.html', context={})
