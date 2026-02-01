import streamlit as st
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

# Fix for Windows asyncio Loop Error (WinError 6)
# Fix for Windows asyncio Loop Error (WinError 6)
try:
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except Exception as e:
    print(f"Warning: Could not set event loop policy: {e}")

from src.content_engine import ContentEngine
from src.media_fetcher import MediaFetcher
from src.subtitle_gen import SubtitleGenerator
from src.video_editor import VideoEditor

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="ShortsGPT Premium", page_icon="🎬", layout="wide")

# Hide Streamlit Branding & Add Custom CSS
st.markdown("""
<style>
    /* GLOBAL STYLES & ANIMATIONS */
    .stApp {
        background: linear-gradient(to bottom right, #222831, #393E46);
    }
    
    /* Buttons: Hover & Transition */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0, 173, 181, 0.4);
    }

    /* MOBILE OPTIMIZATION (Responsiveness) */
    @media (max-width: 768px) {
        /* Optimize padding for mobile */
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 2rem;
        }
        
        /* Larger Touch Targets for Buttons */
        .stButton>button {
            min-height: 50px; /* Fat finger friendly */
            font-size: 16px;
        }
        
        /* Adjust Heading Sizes */
        h1 {
            font-size: 28px !important;
        }
        h2 {
            font-size: 24px !important;
        }
        h3 {
            font-size: 20px !important;
        }
        
        /* Stack columns nicely if Streamlit doesn't automatically */
        /* (Streamlit handles flex wrap, but we can enforce spacing) */
        [data-testid="column"] {
            margin-bottom: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE MANAGEMENT ---
# Initialize session state for "Director's Cut" flow
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1=Input, 2=Script Review, 3=Asset Review, 4=Generating
if 'script_data' not in st.session_state:
    st.session_state.script_data = None
if 'scene_assets' not in st.session_state:
    st.session_state.scene_assets = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Studio Settings")
    
    # THEME SETTINGS
    st.subheader("🎨 Appearance")
    dark_mode = st.toggle("Dark Mode", value=True)
    
    # Define Theme Colors based on toggle
    theme = {
        "bg_gradient": "linear-gradient(to bottom right, #222831, #393E46)" if dark_mode else "linear-gradient(to bottom right, #ffffff, #f0f2f6)",
        "text_color": "#EEEEEE" if dark_mode else "#333333",
        "card_bg": "rgba(0, 173, 181, 0.1)" if dark_mode else "rgba(0, 173, 181, 0.1)",
        "border_color": "#00ADB5",
        "loader_text": "#EEE" if dark_mode else "#333"
    }

    # 1. VISUALS
    st.subheader("📹 Video Style")
    
    # Aspect Ratio
    aspect_ratio = st.radio("Video Format", ["Shorts (9:16)", "Landscape (16:9)"], horizontal=True)
    orientation = "landscape" if "16:9" in aspect_ratio else "portrait"
    
    # Font & Color
    col_font, col_color = st.columns([2, 1])
    with col_font:
        font_files = [f for f in os.listdir("fonts") if f.endswith('.ttf')] if os.path.exists("fonts") else ["Arial"]
        font_choice = st.selectbox("Font", font_files, label_visibility="collapsed")
    with col_color:
        text_color = st.color_picker("Color", "#FFFFFF", label_visibility="collapsed")

    
    # Ken Burns
    use_ken_burns = st.toggle("📸 Ken Burns (Zoom Effect)", value=False, help="Adds slow zoom to images. Compiles slower.")
    
    # Watermarking
    uploaded_logo = st.file_uploader("Brand Logo (Watermark)", type=['png', 'jpg'])
    watermark_path = None
    if uploaded_logo:
        with open("assets/temp_logo.png", "wb") as f:
            f.write(uploaded_logo.getbuffer())
        watermark_path = "assets/temp_logo.png"
        st.success("Logo Uploaded!")

    # 2. AUDIO
    st.subheader("🔊 Audio")
    music_files = [f for f in os.listdir("songs") if f.endswith(('.mp3', '.wav'))] if os.path.exists("songs") else []
    music_choice = st.selectbox("Background Music", ["None"] + music_files)
    
    # ElevenLabs
    el_key_exists = os.getenv("ELEVENLABS_API_KEY") is not None
    use_elevenlabs = st.toggle("🗣️ Voice Clone (ElevenLabs)", value=False, disabled=not el_key_exists, help="Requires ELEVENLABS_API_KEY in .env")
    if use_elevenlabs and not el_key_exists:
        st.warning("Add ELEVENLABS_API_KEY to .env to enable.")
    
    st.divider()
    if st.button("🔄 Reset Project"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 4. MAIN APP LOGIC ---
st.title("🎬 ShortsGPT Premium")
st.markdown("### The AI Director's Suite")

# Apply Theme CSS Dynamically
st.markdown(f"""
<style>
    /* GLOBAL STYLES & ANIMATIONS */
    .stApp {{
        background: {theme['bg_gradient']};
        color: {theme['text_color']};
    }}
    
    /* Buttons: Hover & Transition */
    .stButton>button {{
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0, 173, 181, 0.4);
    }}

    /* MOBILE OPTIMIZATION (Responsiveness) */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 2rem;
        }}
        .stButton>button {{
            min-height: 50px; 
            font-size: 16px;
        }}
        h1 {{ font-size: 28px !important; }}
        h2 {{ font-size: 24px !important; }}
        h3 {{ font-size: 20px !important; }}
        [data-testid="column"] {{ margin-bottom: 20px; }}
    }}
</style>
""", unsafe_allow_html=True)

# ... (Step 1, 2, 3 logic remains largely same, just ensure text colors don't clash if hardcoded) ...
# Skipping to Step 4 Modification for Time Estimate

# STEP 1: INPUT & CONCEPT
if st.session_state.step == 1:
    
    # Inspiration Expander (Cleaner Layout)
    with st.expander("✨ Need Inspiration? Generate Ideas here"):
        c1, c2 = st.columns([3, 1])
        niche = c1.text_input("Enter Niche (e.g., History)", label_visibility="collapsed", placeholder="E.g. History, Tech, Mystery")
        if c2.button("Inspire Me"):
            with st.spinner("Analyzing viral trends..."):
                engine = ContentEngine()
                ideas = engine.generate_viral_topics(niche)
                st.session_state.viral_ideas = ideas
        
        # Show Viral Ideas inside expander
        if 'viral_ideas' in st.session_state and st.session_state.viral_ideas:
            st.info("🔥 **Viral Hooks Generated:**")
            for i, idea in enumerate(st.session_state.viral_ideas):
                 if st.button(idea, key=f"idea_{i}"):
                     st.session_state.selected_topic = idea
                     st.rerun()

    # Main Input
    topic_val = st.session_state.get("selected_topic", "Psychology Facts about Love")
    topic = st.text_input("What is your video about?", topic_val)
    
    if st.button("📝 Draft Script", type="primary"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner("🧠 Brainstorming creative angles..."):
                engine = ContentEngine()
                script_data = engine.generate_script(topic)
                if script_data:
                    st.session_state.script_data = script_data
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Failed to generate script. Check your API Key.")

# STEP 2: SCRIPT DOCTOR (Review & Edit)
elif st.session_state.step == 2:
    st.info("✍️ **Script Doctor**: Review and edit the AI-generated script before production.")
    
    script_data = st.session_state.script_data
    new_title = st.text_input("Video Title", script_data['title'])
    st.session_state.script_data['title'] = new_title
    
    # Editable Scenes
    updated_scenes = []
    for idx, scene in enumerate(script_data['scenes']):
        with st.expander(f"Scene {idx+1}: {scene['visual_keyword']}", expanded=True):
            col_text, col_vis = st.columns([2, 1])
            with col_text:
                new_text = st.text_area(f"Voiceover {idx+1}", scene['text'], height=70)
            with col_vis:
                new_keyword = st.text_input(f"Visual Search Term {idx+1}", scene['visual_keyword'])
            
            updated_scenes.append({
                "text": new_text,
                "visual_keyword": new_keyword
            })
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🎥 Approve & Fetch Assets", type="primary"):
            st.session_state.script_data['scenes'] = updated_scenes
            st.session_state.step = 3
            st.rerun()

# STEP 3: ASSET PRODUCTION & REVIEW
elif st.session_state.step == 3:
    st.success("✅ Script Approved! Fetching media assets...")
    
    script_data = st.session_state.script_data
    total_scenes = len(script_data['scenes'])
    
    # Progress Bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Result container
    scene_assets = []
    os.makedirs("assets", exist_ok=True)
    
    # Fetch Loop
    if not st.session_state.get('assets_ready'):
        fetcher = MediaFetcher()
        sub_gen = SubtitleGenerator(model_size="tiny")
        
        # Audio Provider
        voice_provider = "elevenlabs" if use_elevenlabs else "edge"
        
        for idx, scene in enumerate(script_data['scenes']):
            status_text.text(f"🎬 Producing Scene {idx+1}/{total_scenes}: {scene['visual_keyword']}")
            
            video_filename = f"assets/video_{idx}.mp4"
            audio_filename = f"assets/audio_{idx}.mp3"
            
            # 1. Video
            # Pass orientation from sidebar
            fetcher.download_video(scene['visual_keyword'], 5, video_filename, orientation=orientation)  
            
            # 2. Audio
            if use_elevenlabs:
                fetcher.generate_audio_elevenlabs(scene['text'], audio_filename)
            else:
                asyncio.run(fetcher.generate_audio(scene['text'], audio_filename))
            
            # 3. Subtitles
            subtitles = sub_gen.generate_subtitles(audio_filename)
            
            scene_assets.append({
                'video': video_filename,
                'audio': audio_filename,
                'subtitles': subtitles
            })
            
            progress_bar.progress((idx + 1) / total_scenes)

        st.session_state.scene_assets = scene_assets
        st.session_state.assets_ready = True
        st.rerun()
    
    # Asset Review UI
    else:
        st.subheader("🎞️ Storyboard Preview")
        
        # Display assets in a grid
        cols = st.columns(3)
        for i, asset in enumerate(st.session_state.scene_assets):
            with cols[i % 3]:
                st.video(asset['video'])
                st.caption(f"Scene {i+1} Asset")
        
        if st.button("🚀 Render Final Video", type="primary"):
            st.session_state.step = 4
            st.rerun()

# STEP 4: FINAL ASSEMBLY
elif st.session_state.step == 4:
    with st.status("✂️ Stitching Director's Cut...", expanded=True) as status:
        
        # Calculate Estimated Time
        num_scenes = len(st.session_state.scene_assets)
        est_time = num_scenes * 15 # Approx 15 seconds per scene for rendering
        
        # Premium Loading Animation (Dynamic Theme)
        st.markdown(f"""
        <style>
            @keyframes pulse {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(1.05); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            .rendering-loader {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                border: 2px solid {theme['border_color']};
                border-radius: 10px;
                background: {theme['card_bg']};
                animation: pulse 2s infinite ease-in-out;
            }}
            .loader-text {{
                font-size: 18px;
                font-weight: bold;
                color: {theme['loader_text']};
                margin-top: 10px;
            }}
            .est-time {{
                margin-top: 5px;
                font-size: 14px;
                color: {theme['loader_text']};
                opacity: 0.8;
            }}
        </style>
        <div class="rendering-loader">
            <div style="font-size: 40px;">🎬</div>
            <div class="loader-text">AI is directing your masterpiece...</div>
            <div class="est-time">⏱️ Estimated time: ~{est_time} seconds</div>
            <div style="font-size: 12px; color: #aaa; margin-top: 5px;">Stitching • Mixing Audio • Color Grading</div>
        </div>
        """, unsafe_allow_html=True)

        editor = VideoEditor(font_path=f"fonts/{font_choice}")
        output_file = "assets/final_director_cut.mp4"
        
        music_path = f"songs/{music_choice}" if music_choice != "None" else None
        
        # Extract 9:16 or 16:9 from selector "Shorts (9:16)"
        clean_aspect = "9:16"
        if "16:9" in aspect_ratio:
            clean_aspect = "16:9"

        result_path = editor.create_shorts(
            st.session_state.scene_assets, 
            output_file, 
            music_path=music_path,
            watermark_path=watermark_path,
            use_ken_burns=use_ken_burns,
            aspect_ratio=clean_aspect,
            text_color=text_color
        )
        status.update(label="Rendering Complete!", state="complete")
    
    if result_path:
        st.balloons()
        st.success("✨ Your Masterpiece is Ready!")
        st.video(result_path)
