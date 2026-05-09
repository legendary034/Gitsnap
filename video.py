import mss
import imageio
import threading
import time
import uuid
import os
import numpy as np
from config import get_appdata_path, DEBUG_LOG_FILE

class VideoRecorder:
    def __init__(self, bbox):
        self.bbox = bbox # (left, top, right, bottom)
        self.is_recording = False
        self.thread = None
        self.output_path = os.path.join(get_appdata_path(), f"temp_video_{uuid.uuid4().hex[:8]}.mp4")
        self.writer = None

    def start(self):
        self.is_recording = True
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

    def _record_loop(self):
        fps = 15
        frame_time = 1.0 / fps
        
        try:
            self.writer = imageio.get_writer(self.output_path, format='FFMPEG', fps=fps, codec='libx264')
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
            with open(DEBUG_LOG_FILE, "a") as f:
                f.write(f"Recording error: {e}\n")
        finally:
            if self.writer:
                self.writer.close()

    def stop(self):
        self.is_recording = False
        if self.thread:
            self.thread.join(timeout=3.0)
        return self.output_path
