from faster_whisper import WhisperModel
import os

class SubtitleGenerator:
    def __init__(self, model_size="tiny"):
        # "tiny" is fast and sufficient for clear TTS audio
        # Run on CPU to avoid complex CUDA setup requirements for the user
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def generate_subtitles(self, audio_path):
        """
        Generates word-level timestamps for the given audio file.
        Returns a list of dicts: {'word': str, 'start': float, 'end': float}
        """
        if not os.path.exists(audio_path):
            print(f"Audio file not found: {audio_path}")
            return []
        
        # Check if file is empty (0 bytes) which crashes faster-whisper
        if os.path.getsize(audio_path) == 0:
             print(f"Audio file is empty: {audio_path}")
             return []

        print("Transcribing audio for subtitles...")
        segments, info = self.model.transcribe(audio_path, word_timestamps=True)
        
        word_list = []
        for segment in segments:
            for word in segment.words:
                word_list.append({
                    "word": word.word,
                    "start": word.start,
                    "end": word.end
                })
        
        return word_list

if __name__ == "__main__":
    # Test
    # Create a dummy audio first or ensure one exists
    pass
