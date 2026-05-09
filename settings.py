"""
Settings window and startup management for Gitsnap.
"""
import tkinter as tk
from tkinter import messagebox, ttk
import winreg
import sys
import os
from config import load_config, save_config

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GitsnapScreenshotUtility"

LABEL_WIDTH = 8   # label column width in location rows

# ─────────────────────────── Registry helpers ────────────────────────────────

def is_run_at_startup_enabled():
    """
    Checks if the application is set to run at Windows startup.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error reading registry: {e}")
        return False


def set_run_at_startup(enable):
    """
    Enables or disables running the application at Windows startup.
    """
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


# ─────────────────────────── Settings Window ─────────────────────────────────

class SettingsWindow:
    """
    The settings window for configuring GitHub locations and hotkeys.
    """
    def __init__(self, parent):
        self.config = load_config() or {}

        self.window = tk.Toplevel(parent)
        self.window.title("Gitsnap Settings")
        self.window.resizable(True, True)
        self.window.attributes('-topmost', True)

        # ── Scrollable canvas ──────────────────────────────────────────────
        outer = tk.Frame(self.window)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def on_frame_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        self.inner.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Section 1: GitHub Locations ────────────────────────────────────
        tk.Label(self.inner, text="GitHub Locations",
                 font=("Helvetica", 11, "bold")).pack(pady=(12, 4))

        self.locations_frame = tk.Frame(self.inner, bd=1, relief="groove")
        self.locations_frame.pack(padx=16, fill="x")

        # Single grid inside locations_frame — header + rows all share same columns
        self.locations_grid = tk.Frame(self.locations_frame)
        self.locations_grid.pack(fill="x")
        # Column min-sizes (pixels): Name, Token, Repo, Branch, Folder, Delete
        # Total ≈ 80+130+120+52+65+26 = 473px  +  frame/padding ≈ 560px total
        for col, px in enumerate([80, 130, 120, 52, 65, 26]):
            self.locations_grid.columnconfigure(col, minsize=px, weight=0)

        self._loc_next_row = 0
        self._build_location_header()

        self.location_rows = []
        for loc in self.config.get("GITHUB_LOCATIONS", []):
            self._add_location_row(
                loc.get("name", ""),
                loc.get("token", ""),
                loc.get("repo", ""),
                loc.get("branch", "main"),
                loc.get("folder", "screenshots"),
            )

        tk.Button(self.inner, text="＋ Add Location",
                  command=lambda: self._add_location_row("", "", "", "main", "screenshots")
                  ).pack(pady=(4, 8))

        # ── Section 2: Default Location ────────────────────────────────────
        default_frame = tk.Frame(self.inner)
        default_frame.pack(padx=16, fill="x", pady=(0, 6))
        tk.Label(default_frame, text="Default location:").pack(side="left")
        self.default_loc_var = tk.StringVar(value=self.config.get("DEFAULT_LOCATION", ""))
        self.default_loc_combo = ttk.Combobox(
            default_frame, textvariable=self.default_loc_var, width=22, state="readonly"
        )
        self.default_loc_combo.pack(side="left", padx=6)

        # ── Section 3: Custom Hotkeys ──────────────────────────────────────
        tk.Label(self.inner, text="Custom Hotkeys (Alt + Key)",
                 font=("Helvetica", 11, "bold")).pack(pady=(8, 4))

        self._build_hotkey_header()

        self.hotkeys_frame = tk.Frame(self.inner, bd=1, relief="groove")
        self.hotkeys_frame.pack(padx=16, fill="x")

        self.hotkey_rows = []
        for hk in self.config.get("CUSTOM_HOTKEYS", []):
            self._add_hotkey_row(hk.get("key", ""), hk.get("word", ""), hk.get("location", ""), hk.get("type", "image"))

        tk.Button(self.inner, text="＋ Add Hotkey",
                  command=lambda: self._add_hotkey_row("", "", "", "image")
                  ).pack(pady=(4, 8))

        # ── Startup checkbox ───────────────────────────────────────────────
        self.startup_var = tk.BooleanVar(value=is_run_at_startup_enabled())
        tk.Checkbutton(self.inner, text="Start at Windows startup",
                       variable=self.startup_var).pack(pady=4)

        # ── Save / Cancel ──────────────────────────────────────────────────
        btn_frame = tk.Frame(self.inner)
        btn_frame.pack(pady=(4, 14))
        tk.Button(btn_frame, text="Save", command=self._save_settings, width=10
                  ).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancel", command=self.window.destroy, width=10
                  ).pack(side="left", padx=6)

        # Auto-size width to content; cap height at 90% of screen
        self._refresh_location_dropdowns()
        self.window.update_idletasks()
        req_w = self.inner.winfo_reqwidth() + 20   # +20 for scrollbar
        req_h = self.inner.winfo_reqheight() + 20
        max_h = int(self.window.winfo_screenheight() * 0.9)
        w = max(req_w, 520)
        h = min(req_h, max_h)
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.window.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── Location rows ─────────────────────────────────────────────────────

    def _build_location_header(self):
        bg = "#e0e0e0"
        r = self._loc_next_row
        self._loc_next_row += 1
        for col, text in enumerate(["Name", "Token", "Repo (user/repo)", "Branch", "Folder", ""]):
            tk.Label(self.locations_grid, text=text, bg=bg,
                     font=("Helvetica", 8, "bold"), anchor="w"
                     ).grid(row=r, column=col, sticky="ew", padx=3, pady=2)

    def _add_location_row(self, name, token, repo, branch, folder):
        r = self._loc_next_row
        self._loc_next_row += 1

        name_var   = tk.StringVar(value=name)
        token_var  = tk.StringVar(value=token)
        repo_var   = tk.StringVar(value=repo)
        branch_var = tk.StringVar(value=branch)
        folder_var = tk.StringVar(value=folder)

        e_name   = tk.Entry(self.locations_grid, textvariable=name_var)
        e_token  = tk.Entry(self.locations_grid, textvariable=token_var, show="*")
        e_repo   = tk.Entry(self.locations_grid, textvariable=repo_var)
        e_branch = tk.Entry(self.locations_grid, textvariable=branch_var)
        e_folder = tk.Entry(self.locations_grid, textvariable=folder_var)

        e_name  .grid(row=r, column=0, sticky="ew", padx=2, pady=1)
        e_token .grid(row=r, column=1, sticky="ew", padx=2, pady=1)
        e_repo  .grid(row=r, column=2, sticky="ew", padx=2, pady=1)
        e_branch.grid(row=r, column=3, sticky="ew", padx=2, pady=1)
        e_folder.grid(row=r, column=4, sticky="ew", padx=2, pady=1)

        # Refresh dropdowns when name changes
        name_var.trace_add("write", lambda *_: self._refresh_location_dropdowns())

        widgets = [e_name, e_token, e_repo, e_branch, e_folder]

        def remove():
            for w in widgets:
                w.destroy()
            del_btn.destroy()
            self.location_rows[:] = [x for x in self.location_rows if x["row"] != r]
            self._refresh_location_dropdowns()

        del_btn = tk.Button(self.locations_grid, text="✕", fg="red", command=remove)
        del_btn.grid(row=r, column=5, padx=2, pady=1)

        self.location_rows.append({
            "row": r,
            "name_var":   name_var,
            "token_var":  token_var,
            "repo_var":   repo_var,
            "branch_var": branch_var,
            "folder_var": folder_var,
        })

    def _get_location_names(self):
        return [r["name_var"].get().strip() for r in self.location_rows if r["name_var"].get().strip()]

    def _refresh_location_dropdowns(self):
        names = self._get_location_names()

        # Default location dropdown
        self.default_loc_combo["values"] = names
        if self.default_loc_var.get() not in names and names:
            self.default_loc_var.set(names[0])

        # Hotkey dropdowns — "(use default)" + named locations
        combo_values = ["(use default)"] + names
        for r in self.hotkey_rows:
            current = r["location_var"].get()
            r["location_combo"]["values"] = combo_values
            if current not in combo_values:
                r["location_var"].set("(use default)")

    # ── Hotkey rows ───────────────────────────────────────────────────────

    def _build_hotkey_header(self):
        pass  # Labels are inline in each row; header not needed

    def _add_hotkey_row(self, key_val, word_val, location_val, type_val):
        row = tk.Frame(self.hotkeys_frame)
        row.pack(fill="x", pady=2)

        tk.Label(row, text="Alt+").pack(side="left")
        key_var = tk.StringVar(value=key_val)
        tk.Entry(row, textvariable=key_var, width=3).pack(side="left")
        
        tk.Label(row, text=" Type:").pack(side="left")
        type_var = tk.StringVar(value=type_val)
        ttk.Combobox(row, textvariable=type_var, values=["image", "video"], width=6, state="readonly").pack(side="left", padx=2)

        tk.Label(row, text=" Word:").pack(side="left")
        word_var = tk.StringVar(value=word_val)
        tk.Entry(row, textvariable=word_var, width=14).pack(side="left")

        tk.Label(row, text=" Location:").pack(side="left")
        location_var = tk.StringVar()
        combo_values = ["(use default)"] + self._get_location_names()
        location_combo = ttk.Combobox(row, textvariable=location_var,
                                      values=combo_values, width=18, state="readonly")
        # Set initial value
        display_val = location_val if location_val in combo_values else "(use default)"
        location_var.set(display_val)
        location_combo.pack(side="left", padx=2)

        def remove():
            row.destroy()
            self.hotkey_rows[:] = [r for r in self.hotkey_rows if r["frame"] is not row]

        tk.Button(row, text="✕", fg="red", width=3, command=remove).pack(side="left", padx=4)

        self.hotkey_rows.append({
            "frame": row,
            "key_var": key_var,
            "type_var": type_var,
            "word_var": word_var,
            "location_var": location_var,
            "location_combo": location_combo,
        })

    # ── Save ──────────────────────────────────────────────────────────────

    def _save_settings(self):
        # Locations
        locations = []
        seen_names = set()
        for r in self.location_rows:
            n = r["name_var"].get().strip()
            if not n:
                continue
            if n in seen_names:
                messagebox.showwarning("Duplicate Name",
                                       f'Location name "{n}" is used more than once.',
                                       parent=self.window)
                return
            seen_names.add(n)
            locations.append({
                "name": n,
                "token": r["token_var"].get().strip(),
                "repo": r["repo_var"].get().strip(),
                "branch": r["branch_var"].get().strip() or "main",
                "folder": r["folder_var"].get().strip() or "screenshots",
            })

        if not locations:
            messagebox.showwarning("No Locations",
                                   "Add at least one GitHub location before saving.",
                                   parent=self.window)
            return

        self.config["GITHUB_LOCATIONS"] = locations
        self.config["DEFAULT_LOCATION"] = self.default_loc_var.get().strip()

        # Hotkeys
        hotkeys = []
        for r in self.hotkey_rows:
            k = r["key_var"].get().strip()
            if not k:
                continue
            loc_val = r["location_var"].get()
            loc_name = "" if loc_val == "(use default)" else loc_val
            hotkeys.append({
                "key": k,
                "type": r["type_var"].get().strip() or "image",
                "word": r["word_var"].get().strip(),
                "location": loc_name,
            })
        self.config["CUSTOM_HOTKEYS"] = hotkeys

        if save_config(self.config):
            set_run_at_startup(self.startup_var.get())
            messagebox.showinfo("Saved", "Settings saved successfully!", parent=self.window)
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings.", parent=self.window)


def show_settings_window(parent):
    """
    Convenience function to create and show the SettingsWindow.
    """
    return SettingsWindow(parent)
