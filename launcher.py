
import os
import sys
import subprocess
import time
import webbrowser

def find_script():
    # When frozen by PyInstaller, sys._MEIPASS is the temp folder
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'main.py')
    return os.path.join(os.path.dirname(__file__), 'main.py')

def main():
    print("[*] Starting ShortsGPT Premium...", flush=True)
    
    script_path = find_script()
    port = 8501
    
    # We set an env var to tell Streamlit we are frozen
    if hasattr(sys, '_MEIPASS'):
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Define the streamlit command
    cmd = [
        sys.executable,
        "-m", "streamlit",
        "run",
        script_path,
        "--global.developmentMode=false",
        f"--server.port={port}",
        "--server.headless=true",
    ]

    print(f"Executing: {' '.join(cmd)}")
    
    # On Windows, using shell=True allows the console window to stay open
    # We want this for the progress logs
    process = subprocess.Popen(cmd, shell=True) 

    print(f"Waiting for app to launch on port {port}...")
    time.sleep(3)
    
    webbrowser.open(f"http://localhost:{port}")

    try:
        process.wait()
    except KeyboardInterrupt:
        process.kill()

if __name__ == "__main__":
    main()
