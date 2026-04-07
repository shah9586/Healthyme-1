# Run this in your terminal to see available models:
# python check_models.py

from google import genai

GEMINI_API_KEY = "AIzaSyCf6HzM31JwPwfnzITE-03CdsuPJ7A8_Nc"

client = genai.Client(api_key=GEMINI_API_KEY)

for model in client.models.list():
    print(model.name)
