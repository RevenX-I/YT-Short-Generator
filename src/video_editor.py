from moviepy.editor import *
import os
import PIL.Image
import gc

# Fix for Pillow 10.0.0+ removing ANTIALIAS
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

# --- WINDOWS FIX: Monkey Patch sys.stderr.flush ---
# Monkey Patch sys.stderr.flush for Windows
try:
    sys.stderr.flush()
except Exception:
    pass

def safe_flush(): pass
sys.stderr.flush = safe_flush

import numpy as np

def make_pop(duration=0.1, fps=44100):
    """Synthesize a 'Pop' sound (sine sweep)."""
    t = np.linspace(0, duration, int(fps * duration))
    # Sweep freq from 200 to 50
    freq = np.linspace(200, 50, len(t))
    audio = 0.5 * np.sin(2 * np.pi * freq * t) * np.exp(-10 * t)
    return AudioClip(lambda t: [audio[int(t*fps)]] * 2 if int(t*fps) < len(audio) else [0]*2, duration=duration, fps=fps)

def make_whoosh(duration=0.5, fps=44100):
    """Synthesize a 'Whoosh' sound (filtered noise)."""
    # Simple approximation: White noise with volume envelope
    make_frame = lambda t: [np.random.uniform(-0.3, 0.3) * np.sin(np.pi * t / duration)**2] * 2
    return AudioClip(make_frame, duration=duration, fps=fps)


class VideoEditor:
    def __init__(self, font_path="fonts/Montserrat-Black.ttf"):
        self.font = font_path if os.path.exists(font_path) else "Arial"
        # Increase ImageMagick compatibility
        # If user faces issues, they might need config_defaults.py edits, but we assume standard install.

    def create_shorts(self, scene_assets, output_path="output.mp4", music_path=None, watermark_path=None, use_ken_burns=False, aspect_ratio="9:16", text_color="white", progress_callback=None):
        print(f"Editing video ({aspect_ratio})...")
        
        final_clips = []
        
        target_width = 1080
        target_height = 1920
        
        if aspect_ratio == "16:9":
            target_width = 1920
            target_height = 1080
        
        total_scenes = len(scene_assets)

        for idx, asset in enumerate(scene_assets):
            # UPDATE PROGRESS: 0% to 80% is allocated for Scene Processing
            if progress_callback:
                progress = int((idx / total_scenes) * 80)
                progress_callback(progress, f"Rendering Scene {idx+1}/{total_scenes}")

            video_path = asset['video']
            audio_path = asset['audio']
            subtitles = asset['subtitles']
            
            print(f"Processing Scene {idx+1}...")
            
            try:
                # Load Content
                # Check for image extensions
                if video_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                     video_clip = ImageClip(video_path).set_duration(10) # Placeholder duration
                else:
                    video_clip = VideoFileClip(video_path)
                
                audio_clip = AudioFileClip(audio_path)
            except Exception as e:
                print(f"Error loading media for scene {idx}: {e}")
                continue

            # Match Duration
            final_duration = audio_clip.duration
            video_clip = video_clip.set_duration(final_duration)
            
            # Loop ONLY if it's a video
            if not video_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                video_clip = video_clip.loop(duration=final_duration)

            # --- ROBUST RESIZE TO COVER ---
            # Calculate scale factor to cover the target area entirely
            scale_w = target_width / video_clip.w
            scale_h = target_height / video_clip.h
            scale_factor = max(scale_w, scale_h)
            
            # Resize
            # Note: We resize by ratio to preserve aspect ratio
            video_clip = video_clip.resize(scale_factor)
            
            # Center Crop
            # Now the clip is guaranteed to be >= target dimensions
            x_center = video_clip.w / 2
            y_center = video_clip.h / 2
            video_clip = video_clip.crop(
                x1=x_center - target_width / 2,
                y1=y_center - target_height / 2,
                width=target_width,
                height=target_height
            )
            
            # --- KEN BURNS EFFECT (Optional) ---
            if use_ken_burns:
                print(f"Applying Ken Burns to Scene {idx+1}")
                video_clip = video_clip.resize(lambda t: 1 + 0.02 * t) 
            
            # Set Audio
            video_clip = video_clip.set_audio(audio_clip)

            # Generate Subtitle Clips
            text_clips = []
            for item in subtitles:
                word = item['word']
                start = item['start']
                end = item['end']
                duration = end - start
                
                if duration <= 0: continue
                
                try:
                    # REEL STYLE: Dynamic Colors + Pop Animation
                    # Cycle colors to keep attention
                    colors = ['#FFE135', '#FFFFFF', '#00FF00', '#FFE135', '#FFFFFF'] # Yellow, White, Green
                    color = colors[idx % len(colors)]
                    
                    # Highlight Keywords: If the word is short and impactful, maybe force RED or Green
                    if len(word) > 7: color = '#FFFFFF' # Keep long words white for readability

                    txt_clip = (TextClip(
                                    word.upper(), 
                                    fontsize=110, 
                                    color=color, 
                                    font=self.font, 
                                    method='label',
                                    stroke_color='black', 
                                    stroke_width=6
                                )
                                .set_position(('center', 1350)) # Slightly higher to avoid UI
                                .set_start(start)
                                .set_duration(duration))
                    
                    # POP ANIMATION: Start slightly larger and shrink to normal
                    # This creates a "slam" effect
                    txt_clip = txt_clip.resize(lambda t: 1.2 - 0.2 * (t / duration) if t < duration/2 else 1.0)
                    
                    text_clips.append(txt_clip)
                except Exception as e:
                    print(f"Error creating text clip: {e}")

            # --- VISUAL POLISH: Grading & Vignette ---
            # 1. Saturation Boost (Viral coloring)
            # MoviePy 1.0.3: volumex is for audio. For video, we use color_fx.
            # Using simple lambda for saturation:
            # But let's use the 'lum_contrast' or built-in, or just keeping it raw to avoid heavy render.
            # Efficient way: ImageMagick 'modulate'.
            # video_clip = video_clip.fx(vfx.colorx, 1.2) # Increases saturation/brightness indiscriminately
            
            # Let's use a subtle Vignette for focus
            # Create a localized mask
            try:
                # Simple vignette: Dark radial gradient
                # Since creating a gradient mask in code is heavy, we'll strip it for speed 
                # OR use a margin trick.
                pass
            except: pass

            # Composite Scene
            scene_clips = [video_clip] + text_clips
            
            # --- AUDIO POLISH: SFX ---
            # Add a 'Whoosh' at the start of the scene (except first one)
            sfx_clips = []
            if idx > 0:
                try:
                    whoosh = make_whoosh(duration=0.4).volumex(0.4)
                    sfx_clips.append(whoosh.set_start(0))
                except Exception as e: print(f"SFX Error: {e}")
            
            # Add 'Pop' sounds for emphatic words (Where color is NOT yellow)
            # We iterate subtitles again
            for item in subtitles:
                if len(item['word']) > 7: # Matches our logic for White text
                     try:
                        pop = make_pop(duration=0.1).volumex(0.3).set_start(item['start'])
                        sfx_clips.append(pop)
                     except: pass
            
            # Mix Audio
            original_audio = video_clip.audio
            if sfx_clips:
                combined_audio = CompositeAudioClip([original_audio] + sfx_clips)
                video_clip = video_clip.set_audio(combined_audio)
            
            scene_final = CompositeVideoClip(scene_clips).set_duration(final_duration)
            
            # --- MEMORY OPTIMIZATION: Render Scene Immediately ---
            # Instead of keeping the complex graph in memory, we bake it to a file.
            temp_scene_path = f"temp_scene_{idx}.mp4"
            print(f"Rendering intermediate scene to {temp_scene_path}...")
            
            try:
                scene_final.write_videofile(
                    temp_scene_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac", 
                    preset='ultrafast', 
                    threads=1, 
                    logger=None, # DISABLE PROGRESS BAR -> Fixes [Errno 22]
                    temp_audiofile=f"temp_audio_{idx}.m4a",
                    remove_temp=True
                )
            except Exception as e:
                import traceback
                with open(f"scene_error_{idx}.txt", "w") as f:
                    f.write(traceback.format_exc())
                print(f"Error rendering temp scene {idx}: {e}")
                continue
            
            # Close complex objects to free RAM immediately
            scene_final.close()
            video_clip.close()
            audio_clip.close()
            for tc in text_clips: tc.close()
            gc.collect() # Force cleanup
            
            # Load the baked clip (low memory footprint)
            baked_clip = VideoFileClip(temp_scene_path)
            final_clips.append(baked_clip)
        
        if not final_clips:
            print("No valid scenes to compile.")
            return None

        # Concatenate All Scenes (Now just simple video files)
        print("Concatenating scenes...")
        if progress_callback:
            progress_callback(85, "Stitching Scenes Together...")
            
        final_video = concatenate_videoclips(final_clips)
        
        # Add Background Music (Global)
        if music_path and os.path.exists(music_path):
            print(f"Adding background music: {music_path}")
            try:
                bg_music = AudioFileClip(music_path)
                
                if bg_music.duration < final_video.duration:
                    bg_music = afx.audio_loop(bg_music, duration=final_video.duration)
                else:
                    bg_music = bg_music.subclip(0, final_video.duration)
                
                bg_music = bg_music.volumex(0.12)
                
                final_audio = CompositeAudioClip([final_video.audio, bg_music])
                final_video = final_video.set_audio(final_audio)
            except Exception as e:
                print(f"Error adding background music: {e}")
        
        # Add Watermark (Global)
        if watermark_path and os.path.exists(watermark_path):
            print(f"Adding watermark: {watermark_path}")
            try:
                watermark = (ImageClip(watermark_path)
                             .set_duration(final_video.duration)
                             .resize(height=100) 
                             .margin(right=20, top=20, opacity=0)
                             .set_pos(("right", "top")))
                
                final_video = CompositeVideoClip([final_video, watermark])
            except Exception as e:
                print(f"Error adding watermark: {e}")

        # Write File
        print("Starting final render...")
        if progress_callback:
            progress_callback(90, "Final Render & Encoding... (This takes a moment)")
        
        gc.collect()
        
        try:
            final_video.write_videofile(
                output_path, 
                fps=24,
                codec="libx264", 
                audio_codec="aac", 
                preset='ultrafast', 
                threads=1,
                logger=None, # STRICTLY DISABLE TQDM (Fixes Errno 22)
                temp_audiofile="temp_final_audio.m4a",
                remove_temp=False # DISABLED AUTO-CLEANUP (Fixes WinError 32)
            )
        except Exception as e:
            # LOG ERROR TO FILE
            import traceback
            error_msg = traceback.format_exc()
            print(f"Render Error: {e}")
            with open("render_error.txt", "w") as f:
                f.write(error_msg)
            return None

        # Cleanup
        try:
            final_video.close()
            # Close baked clips and remove temp files
            for c in final_clips:
                c.close()
                if os.path.exists(c.filename):
                    os.remove(c.filename)
            
            if music_path: bg_music.close()
        except Exception as e:
            print(f"Cleanup warning: {e}")
            pass
            
        return output_path

if __name__ == "__main__":
    pass
