# core/smart_health_engine.py

from google import genai
from google.genai import types
import json
import re
import io
from PIL import Image


GEMINI_API_KEY = "AIzaSyDSRLx1Fw6B4VCMKxYGmNtnnc6B6tSgLp4"


def analyze_product(image_file=None, text=None):

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = """
You are a certified nutritionist and food scientist. Analyze this food product carefully.

Look at:
- Product name and brand visible on the packaging
- Ingredients list (if visible)
- Nutrition facts label (if visible)
- Any health claims on the packaging

Respond ONLY with a valid JSON object. No extra text, no markdown, no backticks.

{
  "product_name": "detected product name or Unknown Product",
  "score": <integer 0 to 100>,
  "grade": "<one of: A, B, C, D, F>",
  "status": "<one of: Healthy, Moderate, Unhealthy>",
  "summary": "<2 to 3 sentence plain English summary>",
  "positives": ["up to 4 positive nutritional aspects"],
  "issues": ["up to 4 concerns or negative aspects"],
  "recommendations": [
    {
      "name": "<healthier alternative>",
      "reason": "<why it is healthier in one sentence>"
    }
  ]
}

Scoring: 85-100=A Healthy, 70-84=B Good, 50-69=C Moderate, 30-49=D Poor, 0-29=F Unhealthy
"""

    try:
        if image_file is not None:
            image_bytes = image_file.read()
            img = Image.open(io.BytesIO(image_bytes))
            buffered = io.BytesIO()
            img = img.convert("RGB")
            img.save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()

            response = client.models.generate_content(
                model="models/gemini-2.0-flash-lite",
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )

        else:
            text_prompt = prompt + f"\n\nIngredients text: {text}"
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=text_prompt
            )

        raw = response.text.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)

        return {
            'product_name':    result.get('product_name', 'Unknown Product'),
            'score':           int(result.get('score', 0)),
            'grade':           result.get('grade', 'F'),
            'status':          result.get('status', 'Unhealthy'),
            'summary':         result.get('summary', ''),
            'positives':       result.get('positives', []),
            'issues':          result.get('issues', []),
            'recommendations': result.get('recommendations', []),
        }

    except Exception as e:
        print("GEMINI ERROR:", str(e))
        return _fallback_result(str(e))


def _fallback_result(error_msg):
    return {
        'product_name':    'Unknown Product',
        'score':           0,
        'grade':           'F',
        'status':          'Unhealthy',
        'summary':         error_msg,
        'positives':       [],
        'issues':          ['Could not analyze product. Please try again with a clearer image.'],
        'recommendations': [],
    }


def calculate_reward_points(score: int) -> int:
    if score >= 85: return 50
    if score >= 70: return 30
    if score >= 50: return 15
    if score >= 30: return 8
    return 3