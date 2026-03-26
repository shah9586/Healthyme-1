from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
#from .models import ScanHistory  # optional (create later)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


User = get_user_model()

def home(request):
    return render(request, 'home.html')

def auth_choice(request):
    return render(request, 'auth_choice.html')



# LOGIN (email OR contact)
def login_view(request):
    error = ""

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        user = None

        if '@' in username_input:
            try:
                user_obj = User.objects.get(email=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                error = "❌ User not found"
        else:
            try:
                user_obj = User.objects.get(contact=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                error = "❌ User not found"

        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            if error == "":
                error = "❌ Incorrect password"

    return render(request, 'login.html', {'error': error})
    
   
def register_view(request):
    if request.method == 'POST':
        data = request.POST

        password1 = data.get('password1')
        password2 = data.get('password2')

        # ✅ PASSWORD MATCH CHECK (IMPORTANT)
        if password1 != password2:
            return render(request, 'register.html', {
                'error': '❌ Passwords do not match'
            })

        # ✅ STRONG PASSWORD CHECK
        import re
        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[\W_]).{8,}$', password1):
            return render(request, 'register.html', {
                'error': '❌ Password must be strong (8+ chars, capital, number, special char)'
            })

        from django.contrib.auth import get_user_model
        User = get_user_model()

        # ✅ CREATE USER
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            contact=data['contact'],
            password=password1
        )

        return redirect('/login/')

    return render(request, 'register.html')


def dashboard(request):
    return render(request, 'dashboard.html')

def scan(request):
    result = None

    if request.method == 'POST':
        product = request.POST.get('product').lower()

        # Dummy logic (you can expand later)
        if "maggi" in product:
            result = {
                "name": "Maggi",
                "score": 40,
                "message": "High in sodium. Eat occasionally."
            }
        elif "coke" in product:
            result = {
                "name": "Coca Cola",
                "score": 20,
                "message": "High sugar drink. Avoid frequently."
            }
        else:
            result = {
                "name": product,
                "score": 70,
                "message": "Seems okay. Check ingredients."
            }

    return render(request, 'scan.html', {"result": result})

def user_logout(request):
    logout(request)
    return redirect('/')




User = get_user_model()

@login_required
def admin_dashboard(request):
    users = User.objects.all()

    return render(request, 'admin_dashboard.html', {
        'users': users
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/')

    users = User.objects.all()

    return render(request, 'admin_dashboard.html', {'users': users})


# ADMIN DASHBOARD (READ)
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/')

    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})


# DELETE USER
@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('/')

    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('/admin-dashboard/')


# UPDATE USER
@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('/')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.contact = request.POST.get('contact')
        user.save()
        return redirect('/admin-dashboard/')

    return render(request, 'edit_user.html', {'user': user})


