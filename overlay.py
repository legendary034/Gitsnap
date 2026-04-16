import tkinter as tk
import win32api

class ActionOverlay:
    def __init__(self, parent, img, x, y, on_copy, on_upload):
        self.img = img
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
        
        tk.Button(btn_frame, text="Copy", command=lambda: [self.window.destroy(), on_copy(self.img)]).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Upload", command=lambda: [self.window.destroy(), on_upload(self.img)]).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=2)

def show_action_overlay(parent, img, x, y, on_copy, on_upload):
    ActionOverlay(parent, img, x, y, on_copy, on_upload)
