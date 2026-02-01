from moviepy.editor import *
import os
import PIL.Image

# Fix for Pillow 10.0.0+ removing ANTIALIAS
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})



class VideoEditor:
    def __init__(self, font_path="fonts/Montserrat-Black.ttf"):
        self.font = font_path if os.path.exists(font_path) else "Arial"
        # Increase ImageMagick compatibility
        # If user faces issues, they might need config_defaults.py edits, but we assume standard install.

    def create_shorts(self, scene_assets, output_path="output.mp4", music_path=None, watermark_path=None, use_ken_burns=False, aspect_ratio="9:16", text_color="white"):
        print(f"Editing video ({aspect_ratio})...")
        
        final_clips = []
        
        target_width = 1080
        target_height = 1920
        
        if aspect_ratio == "16:9":
            target_width = 1920
            target_height = 1080
        
        for idx, asset in enumerate(scene_assets):
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
                    txt_clip = (TextClip(word, fontsize=80, color=text_color, font=self.font, stroke_color='black', stroke_width=2)
                                .set_position('center')
                                .set_start(start)
                                .set_duration(duration))
                    text_clips.append(txt_clip)
                except Exception as e:
                    print(f"Error creating text clip: {e}")

            # Composite Scene
            scene_final = CompositeVideoClip([video_clip] + text_clips).set_duration(final_duration)
            final_clips.append(scene_final)
        
        if not final_clips:
            print("No valid scenes to compile.")
            return None

        # Concatenate All Scenes
        print("Concatenating scenes...")
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
        final_video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", preset='ultrafast', logger=None)
        return output_path

if __name__ == "__main__":
    pass

if __name__ == "__main__":
    pass

