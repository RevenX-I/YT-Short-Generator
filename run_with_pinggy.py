
import os
import sys
import subprocess
import time

def kill_zombie_process(port):
    """Finds and kills any process listening on the specified port."""
    try:
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                # print(f">> Killing zombie process on port {port} (PID: {pid})...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def run_app():
    PORT = 8501
    kill_zombie_process(PORT)
    
    # 1. Start Streamlit
    print(f">> Starting App Locally (Port {PORT})...", flush=True)
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "main.py", "--server.headless=true", f"--server.port={PORT}"]
    
    # Run Streamlit
    proc = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, 
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace'
    )
    
    print("\n" + "="*50)
    print(f"[LOCAL]: http://localhost:{PORT}")
    print("="*50 + "\n")

    time.sleep(3)

    # 2. Start Tunnel (using Pinggy) in a NEW WINDOW
    print(">> Launching Tunnel (Pinggy) in a new window...")
    print(">> Please check the POP-UP terminal for your Public URL!")
    
    # Pinggy command
    # -p 443: Port 443
    # -R0:localhost:8501: Forward content
    # a.pinggy.io: Host
    ssh_args = ["ssh", "-o", "StrictHostKeyChecking=no", "-p", "443", "-R0:localhost:8501", "a.pinggy.io"]

    # Use creationflags=subprocess.CREATE_NEW_CONSOLE to FORCE a new window
    # This is a Windows-specific flag (0x00000010)
    CREATE_NEW_CONSOLE = 0x00000010
    
    tunnel_proc = subprocess.Popen(
        ssh_args,
        creationflags=CREATE_NEW_CONSOLE
    )

    try:
        while True:
            # Check if Streamlit is still running
            if proc.poll() is not None:
                print("App stopped.")
                break
            
            # Check if Tunnel is still running (if user closed the window)
            if tunnel_proc.poll() is not None:
                print("Tunnel window was closed.")
                break

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        proc.kill()
        if tunnel_proc.poll() is None:
            tunnel_proc.kill()

if __name__ == "__main__":
    run_app()
