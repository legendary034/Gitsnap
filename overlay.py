import tkinter as tk
import win32api
from tkinter import filedialog

class ActionOverlay:
    def __init__(self, parent, img, x, y, on_copy, on_upload, is_video=False, video_path=None):
        self.img = img
        self.is_video = is_video
        self.video_path = video_path
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Always popup on the primary monitor's center
        p_width = win32api.GetSystemMetrics(0)
        p_height = win32api.GetSystemMetrics(1)
        
        # Center the popup (estimating size 200x50 for positioning)
        win_x = (p_width // 2) - 100
        win_y = (p_height // 2) - 25
        self.window.geometry(f"+{int(win_x)}+{int(win_y)}")
        
        btn_frame = tk.Frame(self.window, bg='white', padx=5, pady=5, bd=1, relief=tk.RAISED)
        btn_frame.pack()
        
        if self.is_video:
            tk.Label(btn_frame, text="Video Ready", bg='white', font=("Helvetica", 9, "bold")).pack(side=tk.TOP, pady=(0, 4))
            tk.Button(btn_frame, text="Save Locally", command=lambda: [self.window.destroy(), self.save_video(on_copy)]).pack(side=tk.LEFT, padx=2)
            tk.Button(btn_frame, text="Upload", command=lambda: [self.window.destroy(), on_upload(None, self.video_path)]).pack(side=tk.LEFT, padx=2)
        else:
            tk.Button(btn_frame, text="Copy", command=lambda: [self.window.destroy(), on_copy(self.img)]).pack(side=tk.LEFT, padx=2)
            tk.Button(btn_frame, text="Upload", command=lambda: [self.window.destroy(), on_upload(self.img, None)]).pack(side=tk.LEFT, padx=2)
            
        tk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=2)

    def save_video(self, on_copy):
        import shutil
        dest = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if dest and self.video_path:
            shutil.copy2(self.video_path, dest)
            # Notify user
            on_copy("saved_video") # Pass a signal that it was saved

def show_action_overlay(parent, img, x, y, on_copy, on_upload, is_video=False, video_path=None):
    ActionOverlay(parent, img, x, y, on_copy, on_upload, is_video, video_path)
