import tkinter as tk
from tkinter import messagebox
import winreg
import sys
import os
from config import load_config, save_config

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GitsnapScreenshotUtility"

def is_run_at_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
            value, regtype = winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error reading registry: {e}")
        return False

def set_run_at_startup(enable):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                if getattr(sys, 'frozen', False):
                    app_path = f'"{sys.executable}"'
                else:
                    app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
            else:
                winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error writing registry: {e}")

class SettingsWindow:
    def __init__(self, parent):
        self.config = load_config() or {}
        
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("500x550")
        self.window.attributes('-topmost', True)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (550 // 2)
        self.window.geometry(f"+{x}+{y}")
        
        tk.Label(self.window, text="GitHub Settings", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        form_frame = tk.Frame(self.window)
        form_frame.pack(padx=20, fill="x")
        
        # Token
        tk.Label(form_frame, text="GitHub Token:").grid(row=0, column=0, sticky="e", pady=5)
        self.token_var = tk.StringVar(value=self.config.get("GITHUB_TOKEN", ""))
        tk.Entry(form_frame, textvariable=self.token_var, width=40).grid(row=0, column=1, sticky="w", pady=5)
        
        # Repo
        tk.Label(form_frame, text="Repository (user/repo):").grid(row=1, column=0, sticky="e", pady=5)
        self.repo_var = tk.StringVar(value=self.config.get("GITHUB_REPO", ""))
        tk.Entry(form_frame, textvariable=self.repo_var, width=40).grid(row=1, column=1, sticky="w", pady=5)
        
        # Branch
        tk.Label(form_frame, text="Branch:").grid(row=2, column=0, sticky="e", pady=5)
        self.branch_var = tk.StringVar(value=self.config.get("GITHUB_BRANCH", "main"))
        tk.Entry(form_frame, textvariable=self.branch_var, width=40).grid(row=2, column=1, sticky="w", pady=5)
        
        # Folder
        tk.Label(form_frame, text="Upload Folder:").grid(row=3, column=0, sticky="e", pady=5)
        self.folder_var = tk.StringVar(value=self.config.get("UPLOAD_FOLDER", "screenshots"))
        tk.Entry(form_frame, textvariable=self.folder_var, width=40).grid(row=3, column=1, sticky="w", pady=5)
        
        # Custom Hotkeys
        tk.Label(self.window, text="Custom Hotkeys (Alt + Key -> Appended Word)", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
        
        # Container with a scrollbar or just a frame
        self.hotkeys_frame = tk.Frame(self.window)
        self.hotkeys_frame.pack(padx=20, fill="both", expand=True)
        
        self.hotkey_rows = []
        
        for hk in self.config.get("CUSTOM_HOTKEYS", []):
            self.add_hotkey_row(hk.get("key", ""), hk.get("word", ""))
            
        tk.Button(self.window, text="Add Hotkey", command=lambda: self.add_hotkey_row("", "")).pack(pady=5)
        
        # Startup Checkbox
        self.startup_var = tk.BooleanVar(value=is_run_at_startup_enabled())
        tk.Checkbutton(self.window, text="Start at Windows startup", variable=self.startup_var).pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Save", command=self.save_settings, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.window.destroy, width=10).pack(side="left", padx=5)
        
    def add_hotkey_row(self, key_val, word_val):
        row_frame = tk.Frame(self.hotkeys_frame)
        row_frame.pack(fill="x", pady=2)
        
        tk.Label(row_frame, text="Alt + ").pack(side="left")
        key_var = tk.StringVar(value=key_val)
        tk.Entry(row_frame, textvariable=key_var, width=5).pack(side="left")
        
        tk.Label(row_frame, text=" -> Word: ").pack(side="left")
        word_var = tk.StringVar(value=word_val)
        tk.Entry(row_frame, textvariable=word_var, width=20).pack(side="left")
        
        def remove_row():
            row_frame.destroy()
            self.hotkey_rows = [r for r in self.hotkey_rows if r["frame"] != row_frame]
            
        tk.Button(row_frame, text="X", fg="red", command=remove_row).pack(side="left", padx=5)
        
        self.hotkey_rows.append({
            "frame": row_frame,
            "key_var": key_var,
            "word_var": word_var
        })
        
    def save_settings(self):
        self.config["GITHUB_TOKEN"] = self.token_var.get()
        self.config["GITHUB_REPO"] = self.repo_var.get()
        self.config["GITHUB_BRANCH"] = self.branch_var.get()
        self.config["UPLOAD_FOLDER"] = self.folder_var.get()
        
        self.config["CUSTOM_HOTKEYS"] = []
        for r in self.hotkey_rows:
            k = r["key_var"].get().strip()
            w = r["word_var"].get().strip()
            if k and w:
                self.config["CUSTOM_HOTKEYS"].append({"key": k, "word": w})
        
        if save_config(self.config):
            set_run_at_startup(self.startup_var.get())
            messagebox.showinfo("Success", "Settings saved successfully!", parent=self.window)
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings.", parent=self.window)

def show_settings_window(parent):
    return SettingsWindow(parent)
