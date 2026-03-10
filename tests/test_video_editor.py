import os
import sys
import unittest
import shutil
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.video_editor import VideoEditor
from moviepy.editor import ColorClip, AudioClip
import numpy as np

class TestVideoEditor(unittest.TestCase):
    def setUp(self):
        self.editor = VideoEditor()
        self.output_path = "test_output.mp4"
        self.assets_dir = "test_assets"
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Create dummy assets
        self.video_path = os.path.join(self.assets_dir, "test_video.mp4")
        self.audio_path = os.path.join(self.assets_dir, "test_audio.mp3")
        
        # Generate 2s video
        # Using ColorClip as a lightweight video source
        print("Generating test video asset...")
        ColorClip(size=(540, 960), color=(255, 0, 0), duration=2).set_fps(24).write_videofile(self.video_path, verbose=False, logger=None, codec="libx264")
        
        # Generate 2s audio
        print("Generating test audio asset...")
        make_frame = lambda t: [np.sin(440 * 2 * np.pi * t) * 0.5] * 2
        AudioClip(make_frame, duration=2, fps=44100).write_audiofile(self.audio_path, verbose=False, logger=None)
        
        self.scene_assets = [{
            'video': self.video_path,
            'audio': self.audio_path,
            'subtitles': [{'word': 'Hello', 'start': 0.5, 'end': 1.0}, {'word': 'World', 'start': 1.0, 'end': 1.5}]
        }]

    def test_create_shorts(self):
        print("\nRunning VideoEditor.create_shorts test...")
        # Use a dummy progress callback
        callback = lambda prog, msg: print(f"Progress: {prog}% - {msg}")
        
        result = self.editor.create_shorts(self.scene_assets, output_path=self.output_path, progress_callback=callback)
        
        self.assertTrue(os.path.exists(self.output_path), "Output video should exist")
        self.assertEqual(result, self.output_path)
        
        # Check if file is released (try to rename it)
        try:
            temp_name = self.output_path + ".moved"
            os.rename(self.output_path, temp_name)
            os.rename(temp_name, self.output_path)
            print("File lock check passed.")
        except PermissionError:
            self.fail("Output file is still locked by the process!")

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
            except PermissionError:
                print(f"WARNING: Could not remove {self.output_path} - file might still be in use!")
        
        # Cleanup assets
        if os.path.exists(self.assets_dir):
            try:
                shutil.rmtree(self.assets_dir)
            except Exception as e:
                print(f"Warning: Could not remove assets dir: {e}")

if __name__ == '__main__':
    unittest.main()
