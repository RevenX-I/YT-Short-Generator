from moviepy.editor import *
import numpy as np
import os

def make_music(duration=30, filename="songs/sample_music.mp3"):
    # Create a simple beat (440Hz tone with volume modulation)
    make_frame = lambda t: [np.sin(440 * 2 * np.pi * t) * (1 + np.sin(4 * np.pi * t)) / 4] * 2
    
    # Create audio clip
    clip = AudioClip(make_frame, duration=duration, fps=44100)
    
    os.makedirs("songs", exist_ok=True)
    clip.write_audiofile(filename, fps=44100)
    print(f"Generated {filename}")

if __name__ == "__main__":
    make_music()
