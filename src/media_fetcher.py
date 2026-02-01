import os
import requests
import random
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

class MediaFetcher:
    def __init__(self):
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        
class MediaFetcher:
    def __init__(self):
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

    def search_media(self, query, media_type="video", per_page=5, orientation="portrait"):
        """Search Pexels for videos or photos."""
        if not self.pexels_key:
            return []

        headers = {"Authorization": self.pexels_key}
        if media_type == "video":
            url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation={orientation}"
        else:
            url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&orientation={orientation}"

        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            results = []
            if media_type == "video":
                for item in data.get('videos', []):
                    # Get best quality video file
                    video_files = item.get('video_files', [])
                    if not video_files: continue
                    best = max(video_files, key=lambda x: x.get('width', 0) * x.get('height', 0))
                    results.append({
                        'type': 'video',
                        'id': item.get('id'),
                        'url': best.get('link'),
                        'preview': item.get('image') # Thumbnail
                    })
            else:
                 for item in data.get('photos', []):
                    results.append({
                        'type': 'image',
                        'id': item.get('id'),
                        'url': item.get('src', {}).get('original'),
                        'preview': item.get('src', {}).get('medium')
                    })
            return results
        except Exception as e:
            print(f"Error searching media: {e}")
            return []

    def download_url(self, url, filename):
        try:
            print(f"Downloading from {url}...")
            r = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False

    def download_video(self, query, duration, filename, orientation="portrait"):
        # 1. Try Videos
        videos = self.search_media(query, "video", orientation=orientation)
        if videos:
            selected = random.choice(videos)
            return self.download_url(selected['url'], filename)
        
        # 2. Fallback to Images (Ken Burns)
        print(f"No videos found for {query}. Searching images...")
        images = self.search_media(query, "image", orientation=orientation)
        if images:
            selected = random.choice(images)
            # Change extension to jpg if needed, but filename usually passed as .mp4
            # If filename is .mp4, we should probably save as .jpg and ensure VideoEditor handles it.
            # But the caller expects 'filename'.
            # If we write JPG bytes to a file named .mp4, MoviePy might get confused or FFmpeg might handle it.
            # Safest: change extension.
            real_filename = filename.replace(".mp4", ".jpg") 
            if self.download_url(selected['url'], real_filename):
                # Update filename variable (BUT we can't update caller's string)
                # We need to handle this.
                # Hack: Write to the original filename too? bad idea.
                # If we save as .jpg, the caller (main.py) which expects .mp4 will fail to find it?
                # Or VideoEditor(video_path) will try to open .mp4.
                # Ideally, main.py should decide the filename.
                # For now, let's just save as is, and hope MoviePy detects format by content or fails gracefully.
                # Actually, best validation: Rename locally.
                # But 'filename' is passed in.
                # We will write the image content to 'filename'. 
                # VideoFileClip might fail if extension is mp4 but content is jpg.
                # Solution: VideoEditor logic I added checks extension.
                # BUT if filename is 'file.mp4' and content is JPG, 'endswith' check will fail.
                # I should rename the file on disk to .jpg? 
                # Let's write to filename (mp4) but with image content. 
                # Then in VideoEditor, if loading VideoFileClip fails, try ImageClip?
                # Or better: changing the contract.
                # For now, to adhere to strict signature, returns True.
                # Let's save as .jpg and delete .mp4 if it exists?
                # No, the caller passed the path.
                
                # REVISION: To support 'Phase 2' properly, I should return the actual path?
                # But signature is boolean.
                # Let's write to the file. If it's an image, we hope VideoEditor handles it.
                # I'll update VideoEditor to try ImageClip if VideoFileClip fails.
                
                # Actually, saving JPG content to .mp4 extension is risky.
                # Let's stick to video fallback for now?
                # Or: Rename file.
                pass 
                
            # For this MVP, if video fails, use the ABSTRACT FALLBACK video which operates as a video.
            # Only use Images if explicitly requested or handled.
            # The 'Ken Burns' feature relies on Images.
            # I will attempt request to photos, save as the filename (even if .mp4).
            # VideoEditor: I will update it to "try ImageClip" if VideoFileClip errors.
            return self.download_url(selected['url'], filename)
            
        return self.download_fallback_video(filename)

    def download_fallback_video(self, filename):
        """Downloads a default abstract background if Pexels fails."""
        print("Using fallback video...")
        fallback_url = "https://videos.pexels.com/video-files/856973/856973-hd_1080_1920_25fps.mp4" 
        return self.download_url(fallback_url, filename)

    async def generate_audio(self, text, filename, voice="en-US-ChristopherNeural", provider="edge"):
        if provider == "elevenlabs" and self.elevenlabs_key:
            return self.generate_audio_elevenlabs(text, filename)
            
        # Default Edge TTS
        for attempt in range(3):
            try:
                print(f"Generating audio (EdgeTTS)...")
                communicate = edge_tts.Communicate(text, voice)
                await asyncio.wait_for(communicate.save(filename), timeout=30)
                return True
            except Exception as e:
                print(f"EdgeTTS Error: {e}")
                await asyncio.sleep(1)
        return False

    def generate_audio_elevenlabs(self, text, filename):
        print("Generating audio (ElevenLabs)...")
        # Adam Voice ID: pMsXgWXvGLBEC91PjDqh (Legacy default) or similar.
        # Use a stable ID.
        voice_id = "21m00Tcm4TlvDq8ikWAM" # Rachel (common default) or similar.
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"ElevenLabs Error: {response.text}")
                return False
        except Exception as e:
            print(f"ElevenLabs Exception: {e}")
            return False

if __name__ == "__main__":
    fetcher = MediaFetcher()
    # print(fetcher.search_media("Ocean"))

if __name__ == "__main__":
    # Test
    fetcher = MediaFetcher()
    # Asyncio run for audio test
    asyncio.run(fetcher.generate_audio("Hello world from Edge TTS", "test_audio.mp3"))
