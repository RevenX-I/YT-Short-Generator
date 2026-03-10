from moviepy.editor import *
import numpy as np
import os

def make_tone(freq, time, func=np.sin):
    return func(freq * 2 * np.pi * time)

def generate_tracks():
    os.makedirs("songs", exist_ok=True)
    fps = 44100
    duration = 10 

    # 1. Horror (Low frequency drone + dissonance)
    print("Generating Horror...")
    make_horror = lambda t: [
        (make_tone(60, t) * 0.5 + make_tone(66, t) * 0.3) * (1 + np.sin(2 * np.pi * t * 0.5)) * 0.3
    ] * 2
    AudioClip(make_horror, duration=duration, fps=fps).write_audiofile("songs/bgm_horror.mp3", fps=fps)

    # 2. Upbeat (Faster beat, major key-ish appregio feel)
    print("Generating Upbeat...")
    make_upbeat = lambda t: [
        (make_tone(220, t, np.sin) * np.abs(np.sin(8 * np.pi * t)) + 
         make_tone(440, t) * np.abs(np.sin(4 * np.pi * t))) * 0.2
    ] * 2
    AudioClip(make_upbeat, duration=duration, fps=fps).write_audiofile("songs/bgm_upbeat.mp3", fps=fps)

    # 3. Epic (Heavy bass pulse + high string-ish drone)
    print("Generating Epic...")
    make_epic = lambda t: [
        (make_tone(55, t, np.cos) * (1 + np.sin(4 * np.pi * t)) + # Bass pulse
         make_tone(110, t) * 0.3) * 0.3
    ] * 2
    AudioClip(make_epic, duration=duration, fps=fps).write_audiofile("songs/bgm_epic.mp3", fps=fps)

    # 4. Sad (Slow, minor feel)
    print("Generating Sad...")
    make_sad = lambda t: [
        (make_tone(150, t) * 0.4 + make_tone(180, t) * 0.2) * (1 + np.sin(np.pi * t * 0.5)) * 0.2
    ] * 2
    AudioClip(make_sad, duration=duration, fps=fps).write_audiofile("songs/bgm_sad.mp3", fps=fps)
    
    # 5. Calm (Steady low-mid tone)
    print("Generating Calm...")
    make_calm = lambda t: [
        (make_tone(300, t) * 0.1)
    ] * 2
    AudioClip(make_calm, duration=duration, fps=fps).write_audiofile("songs/bgm_calm.mp3", fps=fps)

if __name__ == "__main__":
    generate_tracks()
