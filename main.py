import ctypes
import os
import sys

# Mutex to ensure only one instance runs
mut = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\GitsnapScreenshotUtility")
if ctypes.windll.kernel32.GetLastError() == 183:
    os._exit(0)

# Simple logging for debug
with open("debug_log.txt", "a") as f:
    import datetime
    f.write(f"\n[{datetime.datetime.now()}] Application starting...\n")

try:
    import tkinter as tk
    import pystray
    from PIL import Image, ImageDraw
    from pynput import keyboard
    import threading
    
    from capture import CaptureOverlay, set_dpi_awareness
    from overlay import show_action_overlay
    from upload import upload_image
    from notify import copy_image_to_clipboard, copy_text_to_clipboard_and_notify
    from settings import show_settings_window
except Exception as e:
    with open("debug_log.txt", "a") as f:
        f.write(f"Import Error: {e}\n")
    os._exit(1)

def create_tray_icon():
    image = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill="blue", outline="black")
    return image

def on_copy(img):
    threading.Thread(target=copy_image_to_clipboard, args=(img,), daemon=True).start()

def on_upload(img, word=None):
    def process():
        link, error = upload_image(img, word)
        if link:
            copy_text_to_clipboard_and_notify(link)
        else:
            from win11toast import toast
            toast("Upload Failed", error or "Could not upload image.")
    threading.Thread(target=process, daemon=True).start()

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.bind("<<TriggerCapture>>", self.init_capture)
        self.root.bind("<<OpenSettings>>", self.open_settings)
        self.icon = None
        
    def start(self):
        try:
            with open("debug_log.txt", "a") as f:
                f.write("Initializing tray icon...\n")
            
            menu = pystray.Menu(
                pystray.MenuItem('Settings', self.trigger_settings),
                pystray.MenuItem('Quit', self.quit)
            )
            self.icon = pystray.Icon("ScreenshotUtility", create_tray_icon(), "Screenshot Utility", menu)
            threading.Thread(target=self.icon.run, daemon=True).start()
            
            self.reload_hotkeys()
            
            with open("debug_log.txt", "a") as f:
                f.write("Hotkeys active. Starting Tkinter mainloop.\n")
                
            self.root.mainloop()
        except Exception as e:
            with open("debug_log.txt", "a") as f:
                f.write(f"Runtime Error in App.start: {e}\n")
            os._exit(1)
        
    def reload_hotkeys(self):
        if hasattr(self, 'listener'):
            self.listener.stop()
            
        from config import load_config
        config = load_config() or {}
        custom_hotkeys = config.get("CUSTOM_HOTKEYS", [])
        
        hotkeys_dict = {'<alt>+s': lambda: self.on_hotkey(None)}
        
        for hk in custom_hotkeys:
            key = hk.get("key")
            word = hk.get("word")
            if key and word:
                hotkey_str = f'<alt>+{key}'
                # Default arg trick to bind current loop variables
                hotkeys_dict[hotkey_str] = lambda w=word: self.on_hotkey(w)
                
        self.listener = keyboard.GlobalHotKeys(hotkeys_dict)
        self.listener.start()

    def on_hotkey(self, word=None):
        self.current_word = word
        self.root.event_generate("<<TriggerCapture>>", when="tail")

    def trigger_settings(self, icon, _item):
        self.root.event_generate("<<OpenSettings>>", when="tail")

    def open_settings(self, _event):
        sw = show_settings_window(self.root)
        self.root.wait_window(sw.window)
        self.reload_hotkeys()
        
    def init_capture(self, event):
        word = getattr(self, 'current_word', None)
        def on_capture(img, x, y):
            show_action_overlay(self.root, img, x, y, on_copy, lambda i: on_upload(i, word))
        CaptureOverlay(self.root, on_capture)
        
    def quit(self, icon, item):
        icon.stop()
        self.root.quit()

if __name__ == "__main__":
    set_dpi_awareness()
    App().start()
