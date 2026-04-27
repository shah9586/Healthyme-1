from unittest import result

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from core.models import ProductIndex
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from core.models import ScanHistory


import re
import requests
import pytesseract
from PIL import Image, ImageFilter, ImageOps
from core.models import RewardWallet, RewardHistory
from django.utils import timezone
from core.models import ScanHistory
from core.models import CommunityPost
from django.shortcuts import redirect
import random
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from core.models import LoginOTP
import random
from core.models import RegistrationOTP

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

User = get_user_model()


# ---------------- HOME / AUTH ----------------

def home(request):
    return render(request, 'home.html')


def auth_choice(request):
    return render(request, 'auth_choice.html')


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

        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        contact = data.get('contact', '').strip()
        password1 = data.get('password1', '').strip()
        password2 = data.get('password2', '').strip()

        if password1 != password2:
            return render(request, 'register.html', {
                'error': '❌ Passwords do not match'
            })

        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[\W_]).{8,}$', password1):
            return render(request, 'register.html', {
                'error': '❌ Password must be strong (8+ chars, capital, number, special char)'
            })

        UserModel = get_user_model()

        if UserModel.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': '❌ Email already registered'
            })

        if UserModel.objects.filter(contact=contact).exists():
            return render(request, 'register.html', {
                'error': '❌ Contact number already registered'
            })

        otp = generate_otp()

        # delete old pending OTPs for same email
        RegistrationOTP.objects.filter(email=email, is_verified=False).delete()

        RegistrationOTP.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact=contact,
            password=password1,
            otp=otp
        )

        send_mail(
            subject="HealthyMe Registration OTP",
            message=f"Your HealthyMe OTP is {otp}. It is valid for 5 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session["pending_registration_email"] = email

        return redirect('/verify-registration-otp/')

    return render(request, 'register.html')


@login_required



@login_required
def dashboard(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday

    scans = (
        ScanHistory.objects
        .filter(user=request.user, scanned_at__date__range=[start_of_week, end_of_week])
        .annotate(scan_day=TruncDate("scanned_at"))
        .values("scan_day")
        .annotate(total=Count("id"))
    )

    scan_dict = {
        item["scan_day"]: item["total"]
        for item in scans
    }

    weekly_scan_data = []
    max_count = 1

    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        count = scan_dict.get(day_date, 0)
        max_count = max(max_count, count)

        weekly_scan_data.append({
            "day": day_date.strftime("%a"),
            "count": count,
        })

    for item in weekly_scan_data:
        item["height"] = 20 if item["count"] == 0 else max(25, int((item["count"] / max_count) * 100))

    recent_scans = ScanHistory.objects.filter(user=request.user).order_by("-scanned_at")[:5]

    harmful_items = []
    for scan in recent_scans:
        if scan.harmful_ingredients:
            parts = [x.strip() for x in scan.harmful_ingredients.split(",") if x.strip()]
            harmful_items.extend(parts)

    harmful_items = list(dict.fromkeys(harmful_items))[:8]

    return render(request, "dashboard.html", {
        "weekly_scan_data": weekly_scan_data,
        "recent_scans": recent_scans,
        "harmful_items": harmful_items,
    })

def user_logout(request):
    logout(request)
    return redirect('/')


# ---------------- ADMIN ----------------

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/')

    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})


@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('/')

    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('/admin-dashboard/')


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


# ---------------- HELPERS ----------------

def clean_text(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s\-\.,]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_image_for_ocr(uploaded_file):
    img = Image.open(uploaded_file).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    threshold = 160
    img = img.point(lambda p: 255 if p > threshold else 0)
    return img


# ---------------- HEALTH ANALYSIS ----------------

def analyze_product_text(raw_text, product_name="Unknown Product"):
    text = clean_text(raw_text)
    combined_name_text = f"{product_name} {text}".lower()

    unhealthy_items = {
        "sugar": ("Contains added sugar", 18),
        "glucose": ("Contains glucose", 12),
        "fructose": ("Contains fructose", 12),
        "corn syrup": ("Contains syrup-based sweetener", 15),
        "palm oil": ("Contains palm oil", 15),
        "hydrogenated": ("Contains hydrogenated fat", 20),
        "maida": ("Contains refined flour (maida)", 18),
        "refined wheat flour": ("Contains refined flour", 18),
        "preservative": ("Contains preservatives", 10),
        "artificial color": ("Contains artificial colors", 12),
        "msg": ("Contains MSG", 10),
        "flavour enhancer": ("Contains flavour enhancer", 10),
    }

    healthy_items = {
        "fiber": ("Contains fiber", 6),
        "protein": ("Contains protein", 6),
        "oats": ("Contains oats", 8),
        "whole grain": ("Contains whole grains", 10),
        "millets": ("Contains millets", 10),
        "calcium": ("Contains calcium", 4),
        "iron": ("Contains iron", 4),
        "vitamin": ("Contains vitamins", 4),
        "milk": ("Natural dairy source", 8),
    }

    bad_product_hints = {
        "biscuit": ("Highly processed snack", 10),
        "cookie": ("Highly processed snack", 10),
        "chips": ("Fried processed snack", 15),
        "soft drink": ("Sugary processed beverage", 20),
        "cola": ("Sugary processed beverage", 20),
        "sprite": ("Sugary soft drink", 20),
        "fanta": ("Sugary soft drink", 20),
        "pepsi": ("Sugary soft drink", 20),
        "coca cola": ("Sugary soft drink", 20),
        "instant noodles": ("Highly processed instant food", 15),
        "chocolate": ("Sugar-rich processed product", 12),
        "milkshake": ("Often contains added sugar", 12),
        "bread": ("May contain refined flour", 8),
    }

    issues = []
    positives = []
    score = 100

    weak_text = len(text) < 20 or text.count(" ") < 3
    if weak_text:
        for item, (reason, points) in bad_product_hints.items():
            if item in combined_name_text:
                issues.append(reason)
                score -= points

        score = max(0, min(score, 100))

        if issues:
            status = "Moderate ⚠️" if score >= 45 else "Unhealthy ❌"
            return {
                "product_name": product_name,
                "score": score,
                "status": status,
                "issues": list(dict.fromkeys(issues)),
                "positives": [],
                "text": raw_text or "",
                "confidence": "medium",
                "source": "analysis"
            }

        return {
            "product_name": product_name,
            "score": None,
            "status": "Insufficient Data ⚠️",
            "issues": [
                "Not enough ingredient or nutrition data was available to calculate a reliable score."
            ],
            "positives": [],
            "text": raw_text or "",
            "confidence": "low",
            "source": "analysis"
        }

    for item, (reason, points) in unhealthy_items.items():
        if item in text:
            issues.append(reason)
            score -= points

    for item, (reason, points) in healthy_items.items():
        if item in text:
            positives.append(reason)
            score += points

    for item, (reason, points) in bad_product_hints.items():
        if item in combined_name_text:
            issues.append(reason)
            score -= points

    sugar_match = re.search(r"sugars?\s*(\d+(\.\d+)?)\s*g", text)
    if sugar_match:
        sugar = float(sugar_match.group(1))
        if sugar > 15:
            issues.append(f"High sugar ({sugar}g/100g)")
            score -= 20
        elif sugar > 8:
            issues.append(f"Moderate sugar ({sugar}g/100g)")
            score -= 10

    fat_match = re.search(r"fat\s*(\d+(\.\d+)?)\s*g", text)
    if fat_match:
        fat = float(fat_match.group(1))
        if fat > 20:
            issues.append(f"High fat ({fat}g/100g)")
            score -= 12

    fiber_match = re.search(r"fiber\s*(\d+(\.\d+)?)\s*g", text)
    if fiber_match:
        fiber = float(fiber_match.group(1))
        if fiber >= 5:
            positives.append(f"Good fiber ({fiber}g/100g)")
            score += 8
        elif fiber < 2:
            issues.append(f"Low fiber ({fiber}g/100g)")
            score -= 8

    protein_match = re.search(r"protein\s*(\d+(\.\d+)?)\s*g", text)
    if protein_match:
        protein = float(protein_match.group(1))
        if protein >= 8:
            positives.append(f"Good protein ({protein}g/100g)")
            score += 8

    score = max(0, min(score, 100))

    if score >= 75:
        status = "Healthy ✅"
    elif score >= 45:
        status = "Moderate ⚠️"
    else:
        status = "Unhealthy ❌"

    return {
        "product_name": product_name,
        "score": score,
        "status": status,
        "issues": list(dict.fromkeys(issues)),
        "positives": list(dict.fromkeys(positives)),
        "text": raw_text or "",
        "confidence": "high",
        "source": "analysis"
    }


def get_healthier_recommendation(product_name, text, score):
    if score is None or score >= 50:
        return None

    combined = f"{product_name} {text}".lower()

    # Strong priority order
    category_keywords = [
        ("chocolate", ["kitkat", "dairy milk", "munch", "perk", "5 star", "chocolate", "cocoa"]),
        ("biscuit", ["biscuit", "cookie", "cracker", "hide & seek", "oreo", "parle"]),
        ("chips", ["chips", "kurkure", "nachos", "lays", "wafers"]),
        ("soft_drink", ["sprite", "coca cola", "coke", "pepsi", "fanta", "soft drink", "cola", "soda"]),
        ("noodles", ["noodles", "maggi", "yippee", "instant noodles"]),
        ("ice_cream", ["ice cream", "frozen dessert"]),
        ("juice", ["juice", "fruit drink"]),
        ("milkshake", ["milkshake", "shake"]),
        ("bread", ["bread", "bun", "pav"]),
        ("butter", ["butter", "cheese spread"]),
    ]

    matched_category = None

    for category, keywords in category_keywords:
        if any(keyword in combined for keyword in keywords):
            matched_category = category
            break

    recommendation_map = {
        "chocolate": {
            "category": "Chocolate",
            "options": [
                {"name": "Dark Chocolate (70%+ cocoa)", "query": "dark chocolate 70 cocoa"},
                {"name": "Dates with Nuts", "query": "dates with nuts snack"},
                {"name": "Roasted Almond Snack", "query": "roasted almonds snack"}
            ]
        },
        "biscuit": {
            "category": "Biscuit",
            "options": [
                {"name": "Oats Biscuit", "query": "oats biscuit"},
                {"name": "Whole Wheat Biscuit", "query": "whole wheat biscuit"},
                {"name": "Ragi Biscuit", "query": "ragi biscuit"}
            ]
        },
        "chips": {
            "category": "Chips",
            "options": [
                {"name": "Roasted Makhana", "query": "roasted makhana"},
                {"name": "Baked Chips", "query": "baked chips"},
                {"name": "Khakhra", "query": "khakhra healthy snack"}
            ]
        },
        "soft_drink": {
            "category": "Soft Drink",
            "options": [
                {"name": "Coconut Water", "query": "coconut water"},
                {"name": "Lemon Water", "query": "lemon water drink"},
                {"name": "Buttermilk", "query": "buttermilk drink"}
            ]
        },
        "noodles": {
            "category": "Instant Noodles",
            "options": [
                {"name": "Oats Noodles", "query": "oats noodles"},
                {"name": "Whole Wheat Noodles", "query": "whole wheat noodles"},
                {"name": "Millet Noodles", "query": "millet noodles"}
            ]
        },
        "ice_cream": {
            "category": "Ice Cream",
            "options": [
                {"name": "Frozen Yogurt", "query": "frozen yogurt"},
                {"name": "Fruit Yogurt", "query": "fruit yogurt"},
                {"name": "Homemade Fruit Smoothie", "query": "fruit smoothie"}
            ]
        },
        "juice": {
            "category": "Juice",
            "options": [
                {"name": "Fresh Fruit", "query": "fresh fruits"},
                {"name": "Unsweetened Juice", "query": "unsweetened juice"},
                {"name": "Coconut Water", "query": "coconut water"}
            ]
        },
        "milkshake": {
            "category": "Milkshake",
            "options": [
                {"name": "Unsweetened Smoothie", "query": "unsweetened smoothie"},
                {"name": "Protein Milk Drink", "query": "protein milk drink"},
                {"name": "Buttermilk", "query": "buttermilk drink"}
            ]
        },
        "bread": {
            "category": "Bread",
            "options": [
                {"name": "Whole Wheat Bread", "query": "whole wheat bread"},
                {"name": "Multigrain Bread", "query": "multigrain bread"},
                {"name": "Brown Bread", "query": "brown bread"}
            ]
        },
        "butter": {
            "category": "Butter",
            "options": [
                {"name": "Low Fat Paneer", "query": "low fat paneer"},
                {"name": "Greek Yogurt", "query": "greek yogurt"},
                {"name": "Nut Butter", "query": "natural peanut butter"}
            ]
        }
    }

    default_rec = {
        "category": "Healthy Alternatives",
        "options": [
            {"name": "Fresh Fruit", "query": "fresh fruits"},
            {"name": "Roasted Snacks", "query": "roasted snacks"},
            {"name": "Whole Grain Options", "query": "whole grain snacks"}
        ]
    }

    rec = recommendation_map.get(matched_category, default_rec)

    # Add shopping/search links
    for option in rec["options"]:
        q = option["query"].replace(" ", "+")
        option["amazon_link"] = f"https://www.amazon.in/s?k={q}"
        option["bigbasket_link"] = f"https://www.bigbasket.com/ps/?q={q}"
        option["jiomart_link"] = f"https://www.jiomart.com/search/{q}"

    return rec


# ---------------- DATA LOOKUP ----------------

def fetch_from_local_db(barcode=None, product_name=None):
    if barcode:
        product = ProductIndex.objects.filter(barcode=str(barcode).strip()).first()
        if product:
            text = " ".join(filter(None, [
                product.name,
                product.categories,
                product.ingredients,
                product.brands
            ])).strip()

            return {
                "product_name": product.name or "Unknown Product",
                "text": text,
                "barcode": product.barcode,
                "lookup_source": "local db"
            }

    if product_name:
        product = ProductIndex.objects.filter(name__icontains=product_name.strip()).first()
        if product:
            text = " ".join(filter(None, [
                product.name,
                product.categories,
                product.ingredients,
                product.brands
            ])).strip()

            return {
                "product_name": product.name or "Unknown Product",
                "text": text,
                "barcode": product.barcode,
                "lookup_source": "local db"
            }

    return None

def fetch_product_by_barcode(barcode):
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url, timeout=8)

        if response.status_code != 200:
            return None

        data = response.json()
        if data.get("status") != 1:
            return None

        product = data.get("product", {})
        nutriments = product.get("nutriments", {})

        extras = []
        for key, label in [
            ("sugars_100g", "sugar"),
            ("fat_100g", "fat"),
            ("proteins_100g", "protein"),
            ("fiber_100g", "fiber"),
            ("salt_100g", "salt"),
        ]:
            value = nutriments.get(key)
            if value not in [None, ""]:
                extras.append(f"{label} {value}g")

        text = " ".join(filter(None, [
            product.get("product_name", ""),
            product.get("ingredients_text", ""),
            product.get("categories", ""),
            product.get("brands", ""),
            " ".join(extras),
        ])).strip()

        if not text:
            return None

        return {
            "product_name": product.get("product_name", "Unknown Product"),
            "text": text,
            "lookup_source": "api"
        }

    except Exception as e:
        print("BARCODE API ERROR:", e)
        return None


def fetch_product_by_name(product_name):
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": product_name,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 1
        }

        response = requests.get(url, params=params, timeout=8)
        if response.status_code != 200:
            return None

        data = response.json()
        products = data.get("products", [])
        if not products:
            return None

        product = products[0]
        nutriments = product.get("nutriments", {})

        extras = []
        for key, label in [
            ("sugars_100g", "sugar"),
            ("fat_100g", "fat"),
            ("proteins_100g", "protein"),
            ("fiber_100g", "fiber"),
            ("salt_100g", "salt"),
        ]:
            value = nutriments.get(key)
            if value not in [None, ""]:
                extras.append(f"{label} {value}g")

        text = " ".join(filter(None, [
            product.get("product_name", ""),
            product.get("ingredients_text", ""),
            product.get("categories", ""),
            product.get("brands", ""),
            " ".join(extras),
        ])).strip()

        if not text:
            return None

        return {
            "product_name": product.get("product_name", product_name),
            "text": text,
            "barcode": product.get("code", ""),
            "lookup_source": "api"
        }

    except Exception as e:
        print("NAME API ERROR:", e)
        return None

def fetch_product_advanced(barcode=None, product_name=None):
    local_product = fetch_from_local_db(barcode=barcode, product_name=product_name)

    if local_product and len(clean_text(local_product["text"])) >= 20:
        return local_product

    if barcode:
        api_product = fetch_product_by_barcode(barcode)
        if api_product and len(clean_text(api_product["text"])) >= 20:
            return api_product

    if product_name:
        api_product = fetch_product_by_name(product_name)
        if api_product and len(clean_text(api_product["text"])) >= 20:
            return api_product

    if local_product:
        return local_product

    return None


# ---------------- MAIN SCAN VIEW ----------------
def _calc_points(score):
    if score is None:
        return 0

    if score >= 85:
        return 50
    elif score >= 70:
        return 30
    elif score >= 50:
        return 15
    elif score >= 30:
        return 8
    else:
        return 3

@login_required
def scan(request):
    if request.method == "POST":
        barcode = request.POST.get("barcode", "").strip()
        product_name_input = request.POST.get("product_name", "").strip()

        product = fetch_product_advanced(
            barcode=barcode if barcode else None,
            product_name=product_name_input if product_name_input else None
        )

        if product:
            result = analyze_product_text(
                product["text"],
                product_name=product["product_name"]
            )

            recommendation = get_healthier_recommendation(
                product["product_name"],
                product["text"],
                result["score"]
            )

            result["recommendation"] = recommendation
            result["barcode"] = barcode if barcode else product.get("barcode", "")
            result["source"] = product.get("lookup_source", "unknown")
            result["confidence"] = "high" if product.get("lookup_source") in ["local db", "api"] else "medium"

            ScanHistory.objects.create(
                user=request.user,
                product_name=result.get("product_name", "Unknown Product"),
                barcode=result.get("barcode", ""),
                score=result.get("score"),
                status=result.get("status", ""),
                harmful_ingredients=", ".join(result.get("issues", [])),
                good_ingredients=", ".join(result.get("positives", []))
            )

            give_scan_reward(request.user, result)

            wallet = RewardWallet.objects.get(user=request.user)
            result["reward_points"] = wallet.points

            if result.get("score") is not None:
                result["scan_points"] = _calc_points(result["score"])
            else:
                result["scan_points"] = 0

            return render(request, "result.html", result)

        return render(request, "result.html", {
            "product_name": product_name_input if product_name_input else "Unknown Product",
            "barcode": barcode if barcode else "",
            "score": None,
            "status": "Product Not Found ❌",
            "issues": ["No product data found in local database or API."],
            "positives": [],
            "text": "",
            "confidence": "low",
            "source": "not found",
            "recommendation": None,
            "reward_points": None,
            "scan_points": 0,
        })

    return render(request, "scan.html")

def give_scan_reward(user, result):
    wallet, _ = RewardWallet.objects.get_or_create(user=user)

    points_to_add = 5
    action_text = "Product scanned"

    wallet.total_scans += 1

    if result.get("score") is not None and result["score"] >= 75:
        points_to_add += 10
        wallet.healthy_scans += 1
        action_text = "Healthy product scanned"

    today = timezone.now().date()
    already_rewarded_today = RewardHistory.objects.filter(
        user=user,
        action="First scan of the day",
        created_at__date=today
    ).exists()

    if not already_rewarded_today:
        points_to_add += 5
        RewardHistory.objects.create(
            user=user,
            action="First scan of the day",
            points_added=5
        )

    wallet.points += points_to_add
    wallet.save()

    RewardHistory.objects.create(
        user=user,
        action=action_text,
        points_added=points_to_add
    )

@login_required
def rewards_page(request):
    wallet, _ = RewardWallet.objects.get_or_create(user=request.user)
    history = RewardHistory.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "rewards.html", {
        "wallet": wallet,
        "history": history
    })

@login_required
def health_score_page(request):
    recent_scans = ScanHistory.objects.filter(user=request.user).order_by("-scanned_at")

    return render(request, "health_score.html", {
        "recent_scans": recent_scans
    })


@login_required
def ingredients_page(request):

    recent_scans = ScanHistory.objects.filter(user=request.user).order_by("-scanned_at")

    harmful_items = []
    for scan in recent_scans:
        if scan.harmful_ingredients:
            parts = [x.strip() for x in scan.harmful_ingredients.split(",") if x.strip()]
            harmful_items.extend(parts)

    harmful_items = list(dict.fromkeys(harmful_items))

    return render(request, "ingredients.html", {
        "harmful_items": harmful_items,
        "recent_scans": recent_scans
    })


def generate_otp():
    return str(random.randint(100000, 999999))


@login_required
def community(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            CommunityPost.objects.create(
                user=request.user,
                content=content
            )
        return redirect("community")

    posts = CommunityPost.objects.all().order_by("-created_at")

    return render(request, "community.html", {
        "posts": posts
    })

def generate_otp():
    return str(random.randint(100000, 999999))

def login_otp_request(request):
    if request.method == "POST":
        username_input = request.POST.get("username", "").strip()

        user = None

        if "@" in username_input:
            user = User.objects.filter(email=username_input).first()
        else:
            user = User.objects.filter(contact=username_input).first()

        if not user:
            return render(request, "login_otp_request.html", {
                "error": "❌ User not found"
            })

        otp = generate_otp()

        LoginOTP.objects.create(
            user=user,
            otp=otp
        )

        # Email OTP
        if user.email:
            send_mail(
                subject="HealthyMe Login OTP",
                message=f"Your OTP is: {otp}. It is valid for 5 minutes.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        # Store user id in session for verify step
        request.session["otp_user_id"] = user.id

        return redirect("/verify-otp/")

    return render(request, "login_otp_request.html")

def verify_otp(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        return redirect("/login-otp/")

    user = User.objects.filter(id=user_id).first()

    if not user:
        return redirect("/login-otp/")

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()

        otp_obj = LoginOTP.objects.filter(
            user=user,
            otp=entered_otp,
            is_used=False
        ).order_by("-created_at").first()

        if not otp_obj:
            return render(request, "verify_otp.html", {
                "error": "❌ Invalid OTP"
            })

        if otp_obj.is_expired():
            return render(request, "verify_otp.html", {
                "error": "❌ OTP expired. Please request a new one."
            })

        otp_obj.is_used = True
        otp_obj.save()

        login(request, user)

        if "otp_user_id" in request.session:
            del request.session["otp_user_id"]

        return redirect("/dashboard/")

    return render(request, "verify_otp.html")

def verify_registration_otp(request):
    pending_email = request.session.get("pending_registration_email")

    if not pending_email:
        return redirect('/register/')

    otp_record = RegistrationOTP.objects.filter(
        email=pending_email,
        is_verified=False
    ).order_by('-created_at').first()

    if not otp_record:
        return redirect('/register/')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        if otp_record.is_expired():
            return render(request, 'verify_registration_otp.html', {
                'error': '❌ OTP expired. Please register again.'
            })

        if otp_record.otp != entered_otp:
            return render(request, 'verify_registration_otp.html', {
                'error': '❌ Invalid OTP'
            })

        UserModel = get_user_model()

        UserModel.objects.create_user(
            username=otp_record.email,
            email=otp_record.email,
            first_name=otp_record.first_name,
            last_name=otp_record.last_name,
            contact=otp_record.contact,
            password=otp_record.password
        )

        otp_record.is_verified = True
        otp_record.save()

        if "pending_registration_email" in request.session:
            del request.session["pending_registration_email"]

        return redirect('/login/')

    return render(request, 'verify_registration_otp.html')