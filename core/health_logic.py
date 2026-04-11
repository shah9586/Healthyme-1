def analyze_product(text):
    text = text.lower()

    score = 100
    issues = []
    positives = []

    # -------------------------
    # ❌ SUGAR CHECK
    # -------------------------
    if "sugar" in text:
        score -= 20
        issues.append("High sugar content")

    # -------------------------
    # ❌ BAD OILS
    # -------------------------
    if "palm oil" in text:
        score -= 15
        issues.append("Contains palm oil")

    if "hydrogenated" in text:
        score -= 20
        issues.append("Contains trans fat (hydrogenated oil)")

    # -------------------------
    # ❌ PRESERVATIVES
    # -------------------------
    bad_preservatives = ["e211", "sodium benzoate", "e220", "e321", "e320"]

    for p in bad_preservatives:
        if p in text:
            score -= 15
            issues.append(f"Contains harmful preservative ({p})")

    # -------------------------
    # ⚠️ MODERATE ADDITIVES
    # -------------------------
    moderate = ["e202", "e330", "e322"]

    for m in moderate:
        if m in text:
            score -= 5
            issues.append(f"Contains additive ({m})")

    # -------------------------
    # ❌ ARTIFICIAL COLORS
    # -------------------------
    colors = ["e102", "e110", "e122", "artificial color"]

    for c in colors:
        if c in text:
            score -= 15
            issues.append("Contains artificial color")

    # -------------------------
    # ✅ GOOD THINGS (BONUS)
    # -------------------------
    if "fiber" in text:
        score += 5
        positives.append("Contains fiber")

    if "protein" in text:
        score += 5
        positives.append("Contains protein")

    if "whole grain" in text or "oats" in text:
        score += 10
        positives.append("Made from whole grains")

    # -------------------------
    # LIMIT SCORE
    # -------------------------
    if score > 100:
        score = 100
    if score < 0:
        score = 0

    # -------------------------
    # SUGGESTION ENGINE
    # -------------------------
    suggestion = "Good choice 👍"

    if score < 50:
        suggestion = "Avoid this product ❌"
    elif score < 70:
        suggestion = "Consume in moderation ⚠️"
    else:
        suggestion = "Healthy choice ✅"

    return {
        "score": score,
        "issues": issues,
        "positives": positives,
        "suggestion": suggestion
    }
def analyze_product_text(raw_text, product_name="Unknown Product", confidence="medium"):
    text = (raw_text or "").lower()

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
    }

    issues = []
    positives = []
    score = 100

    if len(text.strip()) < 20:
        return {
            "product_name": product_name,
            "score": 25,
            "status": "Uncertain ⚠️",
            "issues": [
                "Could not read enough product information clearly",
                "Result is not reliable from this input"
            ],
            "positives": [],
            "text": raw_text or "",
            "confidence": "low",
            "source": "image"
        }

    for item, (reason, points) in unhealthy_items.items():
        if item in text:
            issues.append(reason)
            score -= points

    for item, (reason, points) in healthy_items.items():
        if item in text:
            positives.append(reason)
            score += points

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
        "confidence": confidence,
        "source": "barcode" if confidence == "high" else "image"
    }