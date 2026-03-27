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