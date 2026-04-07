from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from PIL import Image
import cv2
import pytesseract
import re
from .smart_health_engine import analyze_product



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


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


@login_required
def scan(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        # ✅ Pass image directly to Gemini (no Tesseract needed anymore)
        result = analyze_product(image_file=image_file)

        # ✅ Save scan to database
        from .models import ProductScan
        scan_obj = ProductScan.objects.create(
            user=request.user,
            product_name=result.get('product_name', 'Unknown'),
            health_score=result.get('score', 0),
            grade=result.get('grade', 'F'),
            summary=result.get('summary', ''),
            positives=result.get('positives', []),
            negatives=result.get('issues', []),
            recommendations=result.get('recommendations', []),
            points_earned=_calc_points(result.get('score', 0)),
        )

        return render(request, 'result.html', {
            'score':           result.get('score'),
            'grade':           result.get('grade'),
            'status':          result.get('status'),
            'product_name':    result.get('product_name'),
            'summary':         result.get('summary'),
            'issues':          result.get('issues'),
            'positives':       result.get('positives'),
            'recommendations': result.get('recommendations'),
            'points_earned':   scan_obj.points_earned,
        })

    return render(request, 'scan.html')


def _calc_points(score):
    if score >= 85: return 50
    if score >= 70: return 30
    if score >= 50: return 15
    if score >= 30: return 8
    return 3


   


def extract_text(image_path):
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Increase contrast
    gray = cv2.convertScaleAbs(gray, alpha=2, beta=50)

    # Remove noise
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    # Threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Resize (VERY IMPORTANT)
    thresh = cv2.resize(thresh, None, fx=2, fy=2)

    # OCR with config
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)

    return text

def extract_ingredient_section(text):
    text = text.lower()

    keywords = ["ingredient", "ingredients"]
    for key in keywords:
        if key in text:
            start = text.find(key)
            return text[start:start+400]

    return text

import re

def clean_ingredients(text):
    text = text.lower()

    # Remove weird characters
    text = re.sub(r'[^a-z, ]', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    words = text.split()

    # Remove garbage words
    filtered = [w for w in words if len(w) > 3]

    return filtered