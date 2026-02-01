import os
import sys
from pyngrok import ngrok
# Authenticate
ngrok.set_auth_token("394QhzCnI4nka5klynK3k0dvoQu_5CdPX4pCJrt1RgjbUDebw")

import subprocess
import time

def run_app():
    # Try Port 8502 (Fallback)
    PORT = 8502
    
    # 1. Start Streamlit in the background
    print(f">> Starting Streamlit App Locally (Port {PORT})...", flush=True)
    
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "main.py", "--server.headless=true", f"--server.port={PORT}"]
    process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it a second to start
    time.sleep(5) 

    # 2. Open Secure Tunnel
    print(">> Creating Public Tunnel (Ngrok)...", flush=True)
    try:
        # Open a HTTP tunnel on the fallback port
        public_url = ngrok.connect(PORT).public_url
        print(f"\n" + "="*50, flush=True)
        print(f"APP IS LIVE GLOBALLY!", flush=True)
        print(f"Link: {public_url}", flush=True)
        print("="*50 + "\n", flush=True)
        print("(Press Ctrl+C to stop)", flush=True)
        
        # Keep alive loop
        while True:
            time.sleep(1)
            if process.poll() is not None:
                print("Streamlit process ended.", flush=True)
                out, err = process.communicate()
                print(str(out), flush=True)
                print(str(err), flush=True)
                break
        
    except Exception as e:
        print(f"\nError starting tunnel: {e}", flush=True)
    finally:
        process.kill()
        ngrok.kill()

if __name__ == "__main__":
    run_app()
