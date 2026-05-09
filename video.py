"""
Module for handling screen recording to MP4 format.
"""
import os
import threading
import time
import uuid
import imageio
import mss
import numpy as np
from config import get_appdata_path, DEBUG_LOG_FILE

class VideoRecorder:
    """
    Handles capturing screen frames and writing them to an MP4 file.
    """
    def __init__(self, bbox):
        """
        Initialize the recorder with a bounding box.
        """
        self.bbox = bbox # (left, top, right, bottom)
        self.is_recording = False
        self.thread = None

        # Use C:\temp for temporary video storage as requested
        temp_dir = "C:\\temp"
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir)
            except OSError:
                # Fallback to AppData if C:\temp cannot be created or accessed
                temp_dir = get_appdata_path()

        self.output_path = os.path.join(temp_dir, f"temp_video_{uuid.uuid4().hex[:8]}.mp4")
        self.writer = None

    def start(self):
        """
        Start the recording thread.
        """
        self.is_recording = True
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

    def _record_loop(self):
        """
        Main loop for capturing and writing frames.
        """
        fps = 15
        frame_time = 1.0 / fps

        try:
            self.writer = imageio.get_writer(
                self.output_path, format='FFMPEG', fps=fps, codec='libx264'
            )
            with mss.mss() as sct:
                monitor = {
                    "left": int(self.bbox[0]),
                    "top": int(self.bbox[1]),
                    "width": int(self.bbox[2] - self.bbox[0]),
                    "height": int(self.bbox[3] - self.bbox[1])
                }

                while self.is_recording:
                    loop_start = time.time()

                    sct_img = sct.grab(monitor)
                    img = np.array(sct_img)
                    img_rgb = img[:, :, :3][:, :, ::-1] # BGRA -> RGB

                    self.writer.append_data(img_rgb)

                    elapsed = time.time() - loop_start
                    sleep_time = frame_time - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
        except Exception as e:
            with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"Recording error: {e}\n")
        finally:
            if self.writer:
                self.writer.close()

    def stop(self):
        """
        Stop the recording and return the path to the video file.
        """
        self.is_recording = False
        if self.thread:
            self.thread.join(timeout=3.0)
        return self.output_path
