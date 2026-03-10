import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()

# Hardcoded Voice ID from media_fetcher.py (Rachel)
voice_id = "21m00Tcm4TlvDq8ikWAM" 

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}

payload = {
    "text": "This is a test of the emergency broadcast system.",
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}

print(f"Testing TTS Generation with key: {api_key[:10]}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("SUCCESS! TTS Generated.")
        with open("test_el_output.mp3", "wb") as f:
            f.write(response.content)
    else:
        print(f"FAILED. Response: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
