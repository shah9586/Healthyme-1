from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.core.mail import send_mail


def home(request):
    return render(request, 'home.html')

def auth_choice(request):
    return render(request, 'auth_choice.html')

# REGISTER
def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    return render(request, 'register.html', {'form': form})


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

        if data['password1'] != data['password2']:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        try:
            validate_password(data['password1'])
        except ValidationError as e:
            return render(request, 'register.html', {'error': e.messages})

        from .models import User
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            contact=data['contact'],
            password=data['password1']
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
