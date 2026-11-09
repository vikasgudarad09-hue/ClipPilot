"""
Folder Watcher Module
Monitors designated video export directories (e.g. Blender render output)
and automatically ingests newly rendered videos into the queue.
"""
import os
import time
import threading
from typing import Callable, Optional

class FolderWatcher:
    def __init__(self, watch_directory: str, on_new_video: Callable[[str], None]):
        self.watch_directory = watch_directory
        self.on_new_video = on_new_video
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._known_files = set()

    def start(self):
        if not os.path.exists(self.watch_directory):
            try:
                os.makedirs(self.watch_directory, exist_ok=True)
            except Exception:
                return

        # Pre-seed existing files
        for f in os.listdir(self.watch_directory):
            if f.lower().endswith((".mp4", ".mov", ".mkv")):
                self._known_files.add(os.path.join(self.watch_directory, f))

        self.running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _poll_loop(self):
        while self.running:
            try:
                if os.path.exists(self.watch_directory):
                    current_files = os.listdir(self.watch_directory)
                    for f in current_files:
                        if f.lower().endswith((".mp4", ".mov", ".mkv")):
                            full_path = os.path.join(self.watch_directory, f)
                            if full_path not in self._known_files:
                                # Ensure file is completely written (size stops changing)
                                initial_size = -1
                                while True:
                                    try:
                                        cur_size = os.path.getsize(full_path)
                                        if cur_size == initial_size and cur_size > 0:
                                            break
                                        initial_size = cur_size
                                        time.sleep(1)
                                    except Exception:
                                        break
                                self._known_files.add(full_path)
                                if self.on_new_video:
                                    self.on_new_video(full_path)
            except Exception as e:
                print(f"Error in folder watcher: {e}")
            time.sleep(3)
