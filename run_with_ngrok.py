import os
import sys
from pyngrok import ngrok
# Authenticate
ngrok.set_auth_token("394QhzCnI4nka5klynK3k0dvoQu_5CdPX4pCJrt1RgjbUDebw")

import subprocess
import time

import signal

def kill_zombie_process(port):
    """Finds and kills any process listening on the specified port."""
    try:
        # specific to Windows
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f">> Killing zombie process on port {port} (PID: {pid})...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass # No process found

def run_app():
    # Back to Port 8501 (Since we killed the zombie)
    PORT = 8501
    kill_zombie_process(PORT)
    
    # 1. Start Streamlit in the background
    print(f">> Starting Streamlit App Locally (Port {PORT})...", flush=True)
    
    # Start Streamlit
    proc = subprocess.Popen(
        ["streamlit", "run", "main.py", "--server.port", str(PORT), "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,            # Line buffered
        encoding='utf-8'      # Force UTF-8
    )

    print("\n" + "="*50)
    print(f"🏠  LOCAL ACCESS: http://localhost:{PORT}")
    print("="*50 + "\n")
    
    # Give it a second to start
    time.sleep(5) 

    # Try Ngrok (Optional)
    # 2. Open Secure Tunnel
    print(">> Creating Public Tunnel (Ngrok)...", flush=True)
    try:
        # Open a HTTP tunnel on standard port
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
                break
        
    except Exception as e:
        print(f"\nError starting tunnel: {e}", flush=True)
    finally:
        process.kill()
        ngrok.kill()

if __name__ == "__main__":
    run_app()
