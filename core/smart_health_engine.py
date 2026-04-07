import pytesseract
from PIL import Image

from .ai_model import predict_health

def analyze_product(text):
    text = text.lower()

    unhealthy_items = {
        "sugar": "High sugar → risk of diabetes",
        "palm oil": "Unhealthy fat → heart risk",
        "maida": "Refined flour → low nutrition",
        "preservative": "Chemicals → harmful long term",
        "artificial color": "Synthetic → may cause allergies"
    }

    healthy_items = {
        "fiber": "Good for digestion",
        "protein": "Helps muscle growth",
        "vitamin": "Boosts immunity",
        "iron": "Good for blood",
        "calcium": "Strengthens bones"
    }

    issues = []
    positives = []

    score = 100

    # ❌ Check unhealthy
    for item, reason in unhealthy_items.items():
        if item in text:
            issues.append(f"{item} → {reason}")
            score -= 15

    # ✅ Check healthy
    for item, reason in healthy_items.items():
        if item in text:
            positives.append(f"{item} → {reason}")
            score += 5

    # Clamp score
    score = max(0, min(score, 100))

    # Status
    if score > 70:
        status = "Healthy ✅"
    elif score > 40:
        status = "Moderate ⚠️"
    else:
        status = "Unhealthy ❌"

    return {
        "score": score,
        "status": status,
        "issues": issues,
        "positives": positives
    }