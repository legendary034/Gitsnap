"""
Module for handling the screen capture overlay and selection.
"""
import ctypes
import tkinter as tk
from PIL import ImageGrab
import win32api
import win32con

def set_dpi_awareness():
    """
    Sets the process to be DPI aware to ensure correct screen coordinates on high-DPI displays.
    """
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        pass

class CaptureOverlay:
    """
    A full-screen transparent overlay for selecting an area to capture.
    """
    def __init__(self, parent, on_capture, on_cancel, is_video=False):
        self.parent = parent
        self.on_capture = on_capture
        self.on_cancel = on_cancel
        self.is_video = is_video

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
        self.window.bind("<Escape>", lambda e: self.on_cancel())

    def show(self):
        """
        Placeholder for showing the overlay (currently unused as it shows on init).
        """

    def on_press(self, event):
        """
        Handles the mouse button press event to start selection.
        """
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        color = 'green' if self.is_video else 'red'
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline=color, width=2, fill='white'
        )

    def on_drag(self, event):
        """
        Handles the mouse drag event to update selection.
        """
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        """
        Handles the mouse button release event to finalize selection.
        """
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        if not self.is_video:
            self.window.destroy()
        if x2 - x1 > 5 and y2 - y1 > 5:
            # Map selection coordinates to absolute virtual screen coordinates
            abs_x1 = x1 + self.v_left
            abs_y1 = y1 + self.v_top
            abs_x2 = x2 + self.v_left
            abs_y2 = y2 + self.v_top
            # bbox coordinates relative to virtual screen
            if self.is_video:
                self.enter_passive_mode()
                self.on_capture(None, abs_x2, abs_y2, bbox=(abs_x1, abs_y1, abs_x2, abs_y2))
            else:
                img = ImageGrab.grab(bbox=(abs_x1, abs_y1, abs_x2, abs_y2), all_screens=True)
                self.on_capture(img, abs_x2, abs_y2, bbox=None)
        else:
            if self.is_video:
                self.window.destroy()

    def enter_passive_mode(self):
        """
        Enters passive mode during recording, making the overlay click-through.
        """
        # Make the recorded area (white fill) completely clear and click-through
        self.window.attributes('-transparentcolor', 'white')
        # Make the rest of the window (grey part) click-through as well
        hwnd = self.window.winfo_id()
        # GWL_EXSTYLE = -20, WS_EX_TRANSPARENT = 0x20
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x20)
        # Unbind selection events so clicks pass through to apps below
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        # Increase border thickness for better visibility during recording
        self.canvas.itemconfig(self.rect, width=3)
