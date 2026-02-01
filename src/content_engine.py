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
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def generate_script(self, topic):
        prompt = f"""
        You are a professional short-form video script writer.
        Create a 90-second minimum viral script about: "{topic}".
        
        Strictly output strict JSON only. No markdown.
        Structure:
        {{
            "title": "Video Title",
            "scenes": [
                {{
                    "text": "Voiceover text here (approx 2 sentences)",
                    "visual_keyword": "precise search term"
                }},
                ... (create 12-15 scenes)
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
            st.warning(f"⚠️ AI Busy ({e}). Switching to Offline Template.")
            print(f"Error generating script: {e}")
            # Fallback Template so the app NEVER stops working
            return {
                "title": f"Viral Video: {topic}",
                "scenes": [
                    {
                        "text": f"Stop scrolling right now! Did you know this mind-blowing secret about {topic}?",
                        "visual_keyword": "mystery dark background"
                    },
                    {
                        "text": "So many people get this completely wrong, and it's costing them big time.",
                        "visual_keyword": "stressed person face"
                    },
                    {
                        "text": "History proves that {topic} has been misunderstood for centuries.",
                        "visual_keyword": "ancient history dusty book"
                    },
                    {
                        "text": "But a new study reveals the shocking truth that changes everything we thought we knew.",
                        "visual_keyword": "scientific research future technology"
                    },
                    {
                        "text": "Let's dive deeper. Imagine a world where this wasn't the case.",
                        "visual_keyword": "utopia futuristic city"
                    },
                    {
                        "text": "The details are actually hidden in plain sight if you know where to look.",
                        "visual_keyword": "detective looking magnifying glass"
                    },
                    {
                        "text": "Experts have been arguing about this for decades, but the answer is finally here.",
                        "visual_keyword": "scientists arguing meeting"
                    },
                    {
                        "text": "It all starts with a simple concept that most of us ignore daily.",
                        "visual_keyword": "crowded city street timelapse"
                    },
                    {
                        "text": "Once you see it, you can never unsee it. It changes your entire perspective.",
                        "visual_keyword": "eye opening close up"
                    },
                    {
                        "text": "So next time you encounter {topic}, remember this one key fact.",
                        "visual_keyword": "writing in notebook pen"
                    },
                    {
                        "text": "It could be the difference between success and failure in this area.",
                        "visual_keyword": "chess game checkmate"
                    },
                    {
                        "text": "Share this with a friend who needs to hear this truth today.",
                        "visual_keyword": "friends talking happy"
                    },
                    {
                        "text": "If you want to stay ahead of the curve, you need to pay attention now.",
                        "visual_keyword": "successful person skyline"
                    },
                    {
                        "text": "We are uncovering more secrets like this every single day.",
                        "visual_keyword": "digital data stream matrix"
                    },
                    {
                        "text": "Hit that subscribe button for more secrets they don't want you to know!",
                        "visual_keyword": "subscribe button animation neon"
                    }
                ]
            }
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

