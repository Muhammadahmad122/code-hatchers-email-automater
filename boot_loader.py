import time
import socket
import os
import sys
import subprocess

def check_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Check if there is an active internet connection.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def main():
    print("========================================")
    print("   Code Hatchers AI System Boot Loader  ")
    print("========================================")
    print("[*] Checking Internet Connection...")

    while True:
        if check_internet():
            print("[+] Internet Connected!")
            break
        else:
            print("[-] No Internet. Retrying in 5 seconds...")
            time.sleep(5)

    # Path to the main application entry point (to be created)
    # Assuming main.py will be in the same directory
    main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

    if not os.path.exists(main_script):
        print(f"[!] Error: main.py not found at {main_script}")
        print("[*] Please ensuring the installation is complete.")
        input("Press Enter to exit...")
        return

    print("[+] Starting AI Business Development System (UI)...")
    print("----------------------------------------")
    
    # Launch Streamlit App
    # Use os.path.join properly for Windows paths
    app_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "ui", "app.py")
    if not os.path.exists(app_script): 
         print(f"[!] Could not find app at {app_script}")
         input("Press Enter...")
         return
         
    try:
        # Use simple 'streamlit run' command structure if -m fails, but -m is preferred for venv
        cmd = [sys.executable, "-m", "streamlit", "run", app_script]
        print(f"[+] Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[!] System stopped by user.")
    except Exception as e:
        print(f"[!] detailed error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
