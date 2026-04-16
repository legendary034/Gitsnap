import tkinter as tk
from PIL import ImageGrab
import ctypes
import win32api
import win32con

def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

class CaptureOverlay:
    def __init__(self, parent, on_capture):
        self.parent = parent
        self.on_capture = on_capture

        # Get virtual screen metrics
        self.v_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self.v_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        self.v_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        self.v_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        self.window = tk.Toplevel(self.parent)
        self.window.attributes('-alpha', 0.3)
        # Use overrideredirect and geometry to span all screens
        self.window.overrideredirect(True)
        self.window.geometry(f"{self.v_width}x{self.v_height}+{self.v_left}+{self.v_top}")
        self.window.configure(background='black')
        self.window.attributes('-topmost', True)
        self.window.config(cursor="cross")

        self.canvas = tk.Canvas(self.window, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.window.bind("<Escape>", lambda e: self.window.destroy())

    def show(self):
        pass

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2, fill='white')

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        self.window.destroy()
        
        if x2 - x1 > 5 and y2 - y1 > 5:
            # Map selection coordinates to absolute virtual screen coordinates
            abs_x1 = x1 + self.v_left
            abs_y1 = y1 + self.v_top
            abs_x2 = x2 + self.v_left
            abs_y2 = y2 + self.v_top
            
            # bbox coordinates relative to virtual screen
            img = ImageGrab.grab(bbox=(abs_x1, abs_y1, abs_x2, abs_y2), all_screens=True)
            self.on_capture(img, abs_x2, abs_y2)
