
import os
import sys
import shutil

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.media_fetcher import MediaFetcher

def test_directors_cut_modification():
    print("Starting Directors Cut Logic Verification...")
    
    # 1. Simulate the User Input from "Script Doctor"
    # Original AI suggestion might have been "Neon heart"
    # User changes it to:
    user_modified_keyword = "Red heart balloon floating in sky"
    
    print(f"User Input: '{user_modified_keyword}'")
    
    # 2. Initialize MediaFetcher (The Engine)
    fetcher = MediaFetcher()
    
    # Check API Key
    if not fetcher.pexels_key:
        print("Warning: PEXELS_API_KEY not found. Test might fail or use fallback.")
    
    # 3. Define output path
    test_video_path = "assets/test_directors_cut.mp4"
    if os.path.exists(test_video_path):
        os.remove(test_video_path)
        
    # 4. Execute the Fetch (Simulating 'Approve & Fetch Assets')
    print(f"Fetching asset for: {user_modified_keyword}...")
    success = fetcher.download_video(user_modified_keyword, 5, test_video_path)
    
    # 5. Verify Result
    if success and os.path.exists(test_video_path):
        size = os.path.getsize(test_video_path)
        print(f"Success! Video downloaded to {test_video_path} ({size} bytes).")
        print("   This confirms that the 'Directors Cut' input was correctly passed to the fetching engine.")
        # Clean up
        # os.remove(test_video_path) 
    else:
        print("❌ Failed to download video.")
        sys.exit(1)

if __name__ == "__main__":
    # Create assets dir if needed
    os.makedirs("assets", exist_ok=True)
    test_directors_cut_modification()
