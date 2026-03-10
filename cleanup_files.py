
import os
import glob

patterns = [
    "scene_error_*.txt",
    "temp_scene_*.mp4",
    "temp_scene_*.mp3",
    "temp_audio_*.m4a",
    "render_error.txt",
    "temp_scene_*TEMP_MPY_wvf_snd.mp3" 
]

deleted_count = 0
for pattern in patterns:
    for filepath in glob.glob(pattern):
        try:
            os.remove(filepath)
            deleted_count += 1
            print(f"Deleted: {filepath}")
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")

print(f"Cleanup complete. Deleted {deleted_count} files.")
