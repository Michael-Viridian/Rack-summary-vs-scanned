# =============================================================================
# Module imports
# =============================================================================

import os
import time
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from filelock import FileLock, Timeout
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =============================================================================
# Constants
# =============================================================================

output_dir = Path(r"P:\Public\Past 7 days RackPrints")
output_dir.mkdir(parents=True, exist_ok=True)

last_seen = {}

# =============================================================================
# Helper functions
# =============================================================================

def safe_copy(src, dest, retries=5, delay=0.5):
    for _ in range(retries):
        try:
            shutil.copy2(src, dest)
            return True
        except Exception:
            time.sleep(delay)
    return False

def should_skip(path):
    stat = os.stat(path)
    sig = (stat.st_size, stat.st_mtime)

    if path in last_seen and last_seen[path] == sig:
        return True

    last_seen[path] = sig
    return False

def wait_until_stable(path, delay=0.2, retries=5):
    last_size = -1
    for _ in range(retries):
        size = os.path.getsize(path)
        if size == last_size:
            return True
        last_size = size
        time.sleep(delay)
    return False

# =============================================================================
# Main function
# =============================================================================

class OnMyWatch:
    
    # Set the directory on watch (use raw string for Windows path)
    watchDirectory = r"P:\Public\RackPrints"

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

    def on_modified(self, event):

        time.sleep(self.settle_seconds)

        if event.is_directory:
            return
        
        if not output_dir.exists():
                print("Output directory not available (network drive down?)")
                time.sleep(5)
                return
        
        if should_skip(event.src_path):
            return
        
        if wait_until_stable(event.src_path):
            file_path = output_dir / Path(event.src_path).name

            if file_path.exists():
                if safe_copy(event.src_path, file_path):
                    print(f"Overwrote: {file_path}")
                else:
                    print(f"Failed to overwrite: {file_path}")
            else:
                if safe_copy(event.src_path, file_path):
                    print(f"Copied: {file_path}")
                else:
                    print(f"Failed to copy: {file_path}")

    def on_deleted(self, event):
        print("Watchdog received deleted event - % s." % event.src_path)

if __name__ == "__main__":
    lock_path = tempfile.gettempdir() + "/watchdog.lock"

    lock = FileLock(lock_path, timeout=0)

    try:
        with lock:
            print("Watchdog started")

            while True:
                try:
                    print("Starting watchdog...")
                    watch = OnMyWatch()
                    watch.run()
                except Exception as e:
                    print(f"Watchdog crashed: {e}")
                    time.sleep(5)

    except Timeout:
        print("Another instance is already running")

    except KeyboardInterrupt:
        print("Watchdog stopped manually")

            

