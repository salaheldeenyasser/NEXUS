import subprocess
import threading
import os
import sys
import atexit
import time

# === Prevent Duplicate Instances ===
pid_file = "/tmp/doorlock_run.lock"
if os.path.exists(pid_file):
    print("Another instance of run.py is already running.")
    sys.exit(1)

with open(pid_file, "w") as f:
    f.write(str(os.getpid()))

atexit.register(lambda: os.remove(pid_file) if os.path.exists(pid_file) else None)

# === 🔧 Track subprocesses for cleanup ===
subprocesses = []

def run_script(path, wait=False):
    print(f"[STARTING] {path}")
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = "/home/salah/doorLockGui"
        env["DISPLAY"] = ":0"
        p = subprocess.Popen(["/home/salah/doorLockGui/venv/bin/python3", path], env=env)
        subprocesses.append(p)

        if wait:
            print("[INFO] Waiting for MJPEG server to initialize camera...")
            time.sleep(3)
    except Exception as e:
        print(f"[ERROR] Failed to run {path}: {e}")

def cleanup():
    print("Cleaning up child processes...")
    for p in subprocesses:
        if p.poll() is None:
            try:
                p.terminate()
                p.wait(timeout=3)
                print(f"Terminated process PID {p.pid}")
            except subprocess.TimeoutExpired:
                print(f"Force killing PID {p.pid}")
                p.kill()

atexit.register(cleanup)

# === 🚀 Main Execution ===
if __name__ == "__main__":
    base_dir = "/home/salah/doorLockGui"

    scripts = [
        f"{base_dir}/Blynk/blynk_code.py",
        f"{base_dir}/gui/start_react.py",
        #f"{base_dir}/deepface_scripts/recognize_from_camera.py",
        f"{base_dir}/hardware/aggregator.py",
        f"{base_dir}/start_mjpeg.py",                              # MJPEG server first
        f"{base_dir}/hardware/fp_input.py",
        f"{base_dir}/hardware/keypad_listener.py",
        f"{base_dir}/hardware/bell_listener.py",
        f"{base_dir}/backend/main.py",                                # FastAPI server and webview
        f"{base_dir}/hardware/UnlockDoor.py",
        f"{base_dir}/hardware/ToggleDoor.py"
        
    ]

    for i, script in enumerate(scripts):
        if not os.path.exists(script):
            print(f"[WARNING] Script not found: {script}")
            continue
        wait = (i == 0)  # Wait after MJPEG server only
        threading.Thread(target=run_script, args=(script, wait), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down run.py gracefully...")