# =============================================================================
# Module imports
# =============================================================================

import os
import time
import shutil
import tempfile
import logging
from pathlib import Path
from datetime import datetime, timedelta
from filelock import FileLock, Timeout
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logging.handlers import RotatingFileHandler

# =============================================================================
# Constants
# =============================================================================

output_dir = Path(r"\\CH1DC01.viridianglass.net.nz\PDrive\Public\rackprints test")
output_dir.mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler(
    r"C:\Logs\SaveRackSummaries.log",
    maxBytes=5*1024*1024,
    backupCount=5
)

logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

last_seen = {}

# =============================================================================
# Helper functions
# =============================================================================

def safe_copy(src, dest, retries=5, delay=0.5):
    for _ in range(retries):
        try:
            shutil.copy2(src, dest)
            return True
        except Exception as e:
            logging.info(f"Copy retry failed {src} -> {dest}: {e}")
            time.sleep(delay)
    return False

def should_skip(path):
    try:
        stat = os.stat(path)
        sig = (stat.st_size, stat.st_mtime)

        now = time.time()

        if path in last_seen:
            if last_seen[path]["sig"] == sig:
                last_seen[path]["time"] = now
                return True

        last_seen[path] = {
            "sig": sig,
            "time": now
        }
        return False
    except Exception as e:
        logging.info(f"should_skip failed for {path}: {e}")
        return True
    
def cleanup_last_seen(max_age=3600):
    try:

        now = time.time()

        stale = [
            path for path, data in last_seen.items()
            if now - data["time"] > max_age
        ]

        for path in stale:
            del last_seen[path]

        if stale:
            logging.info(f"Cleaned {len(stale)} entries from last_seen")

    except Exception as e:
        logging.info(f"cleanup_last_seen failed: {e}")

def wait_until_stable(path, delay=0.2, retries=5):
    try:
        last_size = -1
        for _ in range(retries):
            size = os.path.getsize(path)
            if size == last_size:
                return True
            last_size = size
            time.sleep(delay)
        return False
    except Exception as e:
        logging.info(f"wait_until_stable failed for {path}: {e}")
        return False

# =============================================================================
# Main function
# =============================================================================

class OnMyWatch:
    
    # Set the directory on watch (use raw string for Windows path)
    watchDirectory = r"\\CH1DC01.viridianglass.net.nz\PDrive\Public\RackPrints"

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
                    cleanup_last_seen()

                    retain_time = datetime.now() - timedelta(days=7)
                    
                    if not output_dir.exists():
                        logging.info("Output directory not available (network drive down?)")
                        time.sleep(5)
                        continue

                    for file in output_dir.iterdir():
                        try:
                            file_time = datetime.fromtimestamp(file.stat().st_mtime)
                            if file_time < retain_time:
                                file.unlink()
                                logging.info(f"Deleted old file: {file}")
                        except Exception as e:
                            logging.info(f"Failed to delete {file}: {e}")
                    time.sleep(5)
                    logging.info(f"Rack Summary Duplication Task Alive: {datetime.now()}")

                    try:
                        temp_log = Path(r"C:\Logs\SaveRackSummaries_copy.log")

                        shutil.copy2(
                            r"C:\Logs\SaveRackSummaries.log",
                            temp_log
                        )

                        safe_copy(
                            temp_log,
                            output_dir / "SaveRackSummaries.log"
                        )

                    except Exception as e:
                        logging.info(f"Log copy to network drive failed: {e}")
                
                except Exception as e:
                    logging.info(f"Loop error: {e}")
                    time.sleep(5)

        finally:
            self.observer.stop()
            self.observer.join()

class Handler(FileSystemEventHandler):
    
    def __init__(self, settle_seconds: float = 0.5):
        self.settle_seconds = settle_seconds

    def on_modified(self, event):

        try:
            time.sleep(self.settle_seconds)
            if event.is_directory:
                return
            
            if not output_dir.exists():
                logging.info("Output directory not available (network drive down?)")
                time.sleep(5)
                return
            
            if should_skip(event.src_path):
                return
            
            if wait_until_stable(event.src_path):
                file_path = output_dir / Path(event.src_path).name

                if file_path.exists():
                    if safe_copy(event.src_path, file_path):
                        logging.info(f"Overwrote: {file_path}")
                    else:
                        logging.info(f"Failed to overwrite: {file_path}")
                else:
                    if safe_copy(event.src_path, file_path):
                        logging.info(f"Copied: {file_path}")
                    else:
                        logging.info(f"Failed to copy: {file_path}")
        
        except Exception as e:
                logging.info(f"on_modified error: {e}")


    def on_deleted(self, event):
        try:
            logging.info("Watchdog received deleted event - % s." % event.src_path)
        except Exception as e:
            logging.info(f"on_deleted error: {e}")

if __name__ == "__main__":
    lock_path = Path(tempfile.gettempdir()) / "watchdog.lock"

    lock = FileLock(lock_path, timeout=0)

    try:
        with lock:
            logging.info("Watchdog started")

            while True:
                try:
                    logging.info("Starting watchdog...")
                    watch = OnMyWatch()
                    watch.run()
                except Exception as e:
                    logging.info(f"Watchdog crashed: {e}")
                    time.sleep(5)

    except Timeout:
        logging.info("Another instance is already running")

    except KeyboardInterrupt:
        logging.info("Watchdog stopped manually")

    except Exception as e:
        logging.info(f"Unhandled error: {e}")

            

