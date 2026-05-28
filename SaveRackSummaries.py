# =============================================================================
# Module imports
# =============================================================================

import os, sys
import time
import shutil
import atexit
from pathlib import Path
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =============================================================================
# Constants
# =============================================================================

output_dir = Path(r"P:\Public\Past 7 days RackPrints")
output_dir.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Ensure only 1 program can run
# =============================================================================

LOCK_FILE = "watchdog.lock"

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# Check existing lock
if os.path.exists(LOCK_FILE):
    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read())

        os.kill(pid, 0)  # check if process exists
        print("Already running!")
        sys.exit()

    except Exception:
        print("Stale lock detected, removing...")
        os.remove(LOCK_FILE)

# Create new lock
with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

atexit.register(remove_lock)


# =============================================================================
# Helper functions
# =============================================================================

def safe_copy(src, dest, retries=5, delay=1):
    for _ in range(retries):
        try:
            shutil.copy2(src, dest)
            return True
        except Exception:
            time.sleep(delay)
    return False

# =============================================================================
# Main function
# =============================================================================

class OnMyWatch:
    
    # Set the directory on watch (use raw string for Windows path)
    watchDirectory = r"C:\Users\MEVERETT\OneDrive - Viridian Glass Limited Partnership\Test - RackPrints"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        # watch non-recursively to prevent infinite loops on moves into subfolders
        self.observer.schedule(event_handler, self.watchDirectory, recursive=False)
        self.observer.start()
        try:
            while True:
                try:
                    retain_time = datetime.now() - timedelta(days=7)
                    
                    if not output_dir.exists():
                        print("Output directory not available (network drive down?)")
                        time.sleep(5)
                        continue

                    for file in output_dir.iterdir():
                        try:
                            file_time = datetime.fromtimestamp(file.stat().st_mtime)
                            if file_time < retain_time:
                                file.unlink()
                                print(f"Deleted old file: {file}")
                        except Exception as e:
                            print(f"Failed to delete {file}: {e}")
                    time.sleep(5)

                    print(f"Rack Summary Duplication Task Alive: {datetime.now()}")
                
                except Exception as e:
                    print(f"Loop error: {e}")
                    time.sleep(5)

        finally:
            self.observer.stop()
            self.observer.join()

class Handler(FileSystemEventHandler):
    
    def __init__(self, settle_seconds: float = 0.5):
        self.settle_seconds = settle_seconds

    def on_created(self, event):
        if event.is_directory:
            return
        time.sleep(self.settle_seconds)
     
        if not output_dir.exists():
            print("Output directory not available (network drive down?)")
            time.sleep(5)
            return

        file_path = output_dir / Path(event.src_path).name
        if safe_copy(event.src_path, file_path):
            print(f"Copied: {file_path}")
        else:
            print(f"Failed to copy: {file_path}")

    def on_deleted(self, event):
        print("Watchdog received deleted event - % s." % event.src_path)


if __name__ == '__main__':
    while True:
        try:
            print("Starting watchdog...")
            watch = OnMyWatch()
            watch.run()
        except Exception as e:
            print(f"Watchdog crashed: {e}")
            time.sleep(5)  # prevent rapid crash loop
            

