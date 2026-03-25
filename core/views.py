from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


User = get_user_model()

def home(request):
    return render(request, 'home.html')

def auth_choice(request):
    return render(request, 'auth_choice.html')



# LOGIN (email OR contact)
def login_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        # Check if input is email or contact
        user = None
        if '@' in username_input:
            try:
                user_obj = User.objects.get(email=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except:
                pass
        else:
            try:
                user_obj = User.objects.get(contact=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except:
                pass

        if user:
            login(request, user)

            # 📩 Send Email on Login
            send_mail(
                'Welcome to HealthyMe 🎉',
                'You have successfully logged in!',
                'your_email@gmail.com',  # sender
                [user.email],
                fail_silently=True,
            )

            return redirect('/dashboard/')
    
    return render(request, 'login.html')

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



