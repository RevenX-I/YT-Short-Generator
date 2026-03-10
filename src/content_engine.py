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
        You are an elite viral content strategist (Alex Hormozi style).
        Create a high-retention 90-second script about: "{topic}".
        
        RULES:
        1. HOOK (0-3s): NO "Hey guys" or generic intros. Start IMMEDIATELY with a "Pattern Interrupt" or controversial statement (e.g., "Stop doing this", "Everything you know is wrong").
        2. LANGUAGE: Write at a GRADE 5 reading level. Simple, punchy, direct. No complex words.
        3. PACING: Ultra-fast. Max 7-10 words per sentence.
        4. STRUCTURE: Hook -> Agitation -> Solution/Twist -> CTA (Call to Action).
        5. VISUALS: 
           - 'visual_search_term': SIMPLE 1-3 word keyword for stock footage search (e.g. "Money", "Sunset", "Angry Man"). NO modifiers like "Cinematic" or "Blurry".
           - 'visual_description': Detailed description for context (e.g. "Close up of hands counting cash").
        
        Strictly output strict JSON only. No markdown.
        Structure:
        {{
            "title": "Clickbaity Title",
            "bgm_mood": "Select one: 'horror', 'sad', 'upbeat', 'epic', 'calm'",
            "scenes": [
                {{
                    "text": "Punchy voiceover line (max 10 words)",
                    "visual_search_term": "Simple Keyword",
                    "visual_description": "Detailed idea"
                }},
                ... (create 25-30 fast-paced scenes)
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
            st.toast(f"Using Offline Content (AI Busy)", icon="⚡")
            print(f"[WARN] Error generating script: {e}")
            # Fallback Template so the app NEVER stops working
            return {
                "title": f"Viral Video: {topic}",
                "scenes": [
                    {
                        "text": f"Stop scrolling right now! Did you know this mind-blowing secret about {topic}?",
                        "visual_search_term": "Stop Sign",
                        "visual_description": "Hand stopping camera, red light"
                    },
                    {
                        "text": "So many people get this completely wrong, and it's costing them big time.",
                        "visual_search_term": "Stressed Man",
                        "visual_description": "Person looking stressed holding head"
                    },
                    {
                        "text": "History proves that {topic} has been misunderstood for centuries.",
                        "visual_search_term": "Old Book",
                        "visual_description": "Dusty old books in library"
                    },
                    {
                        "text": "But a new study reveals the shocking truth that changes everything we thought we knew.",
                        "visual_search_term": "Microscope",
                        "visual_description": "Scientist looking into microscope"
                    },
                    {
                        "text": "Let's dive deeper. Imagine a world where this wasn't the case.",
                        "visual_search_term": "Futuristic City",
                        "visual_description": "Wide shot of neon city"
                    },
                    {
                        "text": "The details are actually hidden in plain sight if you know where to look.",
                        "visual_search_term": "Magnifying Glass",
                        "visual_description": "Detective looking through glass"
                    },
                    {
                        "text": "Experts have been arguing about this for decades, but the answer is finally here.",
                        "visual_search_term": "Debate",
                        "visual_description": "People arguing in meeting"
                    },
                    {
                        "text": "It all starts with a simple concept that most of us ignore daily.",
                        "visual_search_term": "Crowd",
                        "visual_description": "Time lapse of city crowd"
                    },
                    {
                        "text": "Once you see it, you can never unsee it. It changes your entire perspective.",
                        "visual_search_term": "Human Eye",
                        "visual_description": "Extreme close up of eye opening"
                    },
                    {
                        "text": "So next time you encounter {topic}, remember this one key fact.",
                        "visual_search_term": "Writing",
                        "visual_description": "Hand writing in notebook"
                    },
                    {
                        "text": "It could be the difference between success and failure in this area.",
                        "visual_search_term": "Chess",
                        "visual_description": "King piece on chess board"
                    },
                    {
                        "text": "Share this with a friend who needs to hear this truth today.",
                        "visual_search_term": "Friends Laughing",
                        "visual_description": "Group of friends talking"
                    },
                    {
                        "text": "If you want to stay ahead of the curve, you need to pay attention now.",
                        "visual_search_term": "Success",
                        "visual_description": "Person looking at skyline"
                    },
                    {
                        "text": "We are uncovering more secrets like this every single day.",
                        "visual_search_term": "Data",
                        "visual_description": "Digital matrix stream"
                    },
                    {
                        "text": "Hit that subscribe button for more secrets they don't want you to know!",
                        "visual_search_term": "Subscribe",
                        "visual_description": "Neon subscribe button"
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
            # Show error in UI so user knows WHY it is offline
            st.toast(f"Using Offline Content (AI Busy)", icon="⚡")
            print(f"[WARN] AI Error: {e}")
            # Fallback Templates
            return [
                "3 psychological tricks to control a conversation",
                "The dark history of the Roman Colosseum",
                "Why you feel like falling when you sleep",
                "3 cybersecurity tips to protect your bank account",
                "The most haunted place in India: Bhangarh Fort"
            ]

