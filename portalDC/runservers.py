# run_servers.py
import subprocess
import os
import time
import signal
import sys

# --- Configuration ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # Assumes script is in project root
PYTHON_EXE = sys.executable # Use the python exe that runs this script
WAITRESS_HOST = "127.0.0.1"
WAITRESS_PORTS = [8000, 8001, 8002]
DJANGO_APP = "portalDC.wsgi:application" # Your WSGI application
CELERY_APP = "portalDC" # Your Celery app name (from celery.py)
CADDY_EXE = os.path.join(PROJECT_DIR, "caddy.exe") # Assumes caddy.exe is in project root
CADDY_CONFIG = os.path.join(PROJECT_DIR, "Caddyfile")

# Commands to run
commands = []

# 1. Waitress Instances
for port in WAITRESS_PORTS:
    cmd = [
        "waitress-serve",
        f"--host={WAITRESS_HOST}",
        f"--port={port}",
        DJANGO_APP,
    ]
    commands.append({"name": f"Waitress (Port {port})", "cmd": cmd})

# 2. Celery Worker
celery_cmd = [
    PYTHON_EXE, # Use python to run celery if 'celery' command isn't directly in PATH reliably
    "-m", "celery", # Run celery as a module
    "-A", CELERY_APP,
    "worker",
    "-l", "info",
    "--pool=solo", # Necessary for Windows
    "--concurrency=1", # Start with 1 on Windows
]
commands.append({"name": "Celery Worker", "cmd": celery_cmd})

# 3. Caddy Server
caddy_cmd = [
    CADDY_EXE,
    "run",
    f"--config={CADDY_CONFIG}",
    f"--adapter=caddyfile", # Explicitly specify adapter
]
commands.append({"name": "Caddy Server", "cmd": caddy_cmd})


# --- Process Management ---
processes = []

print("Starting services...")

try:
    for item in commands:
        print(f"Starting {item['name']}...")
        try:
            # CREATE_NEW_CONSOLE opens each process in its own window on Windows
            process = subprocess.Popen(
                item['cmd'],
                cwd=PROJECT_DIR, # Run command from the project directory
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            processes.append(process)
            print(f"  -> Started {item['name']} (PID: {process.pid})")
            time.sleep(1) # Small delay between starting processes
        except FileNotFoundError:
            print(f"  -> ERROR: Command not found for {item['name']}. Check path/installation.")
            print(f"     Command: {' '.join(item['cmd'])}")
        except Exception as e:
            print(f"  -> ERROR: Failed to start {item['name']}: {e}")
            print(f"     Command: {' '.join(item['cmd'])}")


    print("\nAll services launched in separate windows.")
    print("Press Ctrl+C in *this* window (the script's window) to stop all services.")

    # Keep the main script alive until Ctrl+C
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nCtrl+C received. Stopping services...")

finally:
    for i, process in enumerate(reversed(processes)): # Stop in reverse order
        print(f"Stopping process {len(processes)-i} (PID: {process.pid})...")
        try:
            # Send SIGTERM (like Ctrl+C) - terminate() is often sufficient on Windows
            process.terminate()
            # Optional: Wait a bit and force kill if needed
            # try:
            #    process.wait(timeout=5)
            # except subprocess.TimeoutExpired:
            #    print(f"  -> Process {process.pid} did not terminate gracefully, killing.")
            #    process.kill()
        except Exception as e:
            print(f"  -> Error stopping process {process.pid}: {e}")
    print("All specified services stopped.")