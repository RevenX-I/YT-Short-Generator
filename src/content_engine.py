import os
import json
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class ContentEngine:
    def __init__(self):
        # Try finding key in env vars (Local) OR Streamlit secrets (Cloud)
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key and "GEMINI_API_KEY" in st.secrets:
            self.api_key = st.secrets["GEMINI_API_KEY"]

        if not self.api_key:
             raise ValueError("GEMINI_API_KEY not found in .env or secrets")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_script(self, topic):
        prompt = f"""
        You are a professional short-form video script writer.
        Create a 30-second engaging script about: "{topic}".
        
        Strictly output strict JSON only. No markdown, no "here is the script".
        Structure:
        {{
            "title": "Video Title",
            "scenes": [
                {{
                    "text": "Voiceover text here",
                    "visual_keyword": "search term for background video"
                }},
                ...
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up potential markdown code blocks if Gemini mimics them
            text = response.text.replace('```json', '').replace('```', '').strip()
            script_data = json.loads(text)
            return script_data
        except Exception as e:
            st.error(f"Detailed Error: {e}")
            print(f"Error generating script: {e}")
            return None
    def generate_viral_topics(self, niche):
        """Brainstorms 5 viral video ideas for a given niche."""
        prompt = f"""
        You are a viral content strategist.
        List 5 clickbaity, high-potential short video topics for the niche: "{niche}".
        
        Strictly output a JSON list of strings. Example:
        ["Topic 1", "Topic 2", ...]
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error generating topics: {e}")
            # Fallback Templates
            return [
                "3 psychological tricks to control a conversation",
                "The dark history of the Roman Colosseum",
                "Why you feel like falling when you sleep",
                "3 cybersecurity tips to protect your bank account",
                "The most haunted place in India: Bhangarh Fort"
            ]

