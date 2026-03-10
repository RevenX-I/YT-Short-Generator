
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = "AIzaSyCnzDZac851JchfscBRbxcnP5oJHlfaOxE"

print(f"Testing Key: {api_key[:10]}...")
genai.configure(api_key=api_key)

candidates = [
    "gemini-2.0-flash", # Try 2.0 first
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-flash-latest",
    "gemini-pro",
    "gemini-1.0-pro"
]

for model_name in candidates:
    print(f"\n--- Testing: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say OK")
        print(f"SUCCESS! [OK] Response: {response.text}")
        print(f"Use this model: {model_name}")
        break  # Stop at first success
    except Exception as e:
        print(f"FAILED [X] Error: {e}")
