# Gitsnap: Windows 11 System Tray Screenshot Utility

A lightweight, High-DPI aware screenshot utility that resides in the system tray and allows you to quickly upload standard region screenshots directly to your configured GitHub Repository using the `Alt+S` global hotkey.

## Preparation / Configuration
Before using the upload function, you must configure your GitHub credentials:
1. Create a GitHub Personal Access Token (PAT) with `repo` scopes.
2. Open `config.json` in the application folder and set:
   - `GITHUB_TOKEN`: Your personal access token
   - `GITHUB_REPO`: `username/reponame`
   - `GITHUB_BRANCH`: `main` (or whichever branch)
   - `UPLOAD_FOLDER`: The destination folder (e.g. `screenshots`)

## Features
- **Minimalist System Tray Icon**: Provides an unobtrusive way to manage lifecycle.
- **Global Hotkey (`Alt+S`)**: Instantly captures screen regions anywhere on the device.
- **High-DPI Aware**: Ensures precise capture boundaries even on scaled Windows 11 displays.
- **Action Overlay**: Prompts users post-capture to either "Copy" to clipboard or "Upload".
- **GitHub Hosted**: Uploads image straight to a GitHub repository of your choice.
- **Instant Hotlink Copy**: Uploads image and automatically copies the raw `raw.githubusercontent.com` link to clipboard, displaying a rich Windows 11 Toast notification upon completion.

## Development Setup
Make sure you have Python 3.9+ and pip installed.
1. Create a virtual environment:
   ```cmd
   python -m venv venv
   call venv\Scripts\activate
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Run the tool:
   ```cmd
   python main.py
   ```

## Packaging into a Windows 11 Executable (`.exe`)
You can build a standalone executable that doesn't require Python on the target machine using `PyInstaller`. 

1. Open PowerShell or Command Prompt.
2. Ensure you are in your activated virtual environment.
3. Install PyInstaller:
   ```cmd
   pip install pyinstaller
   ```
4. Build the executable parameter:
   ```cmd
   pyinstaller --noconfirm --onefile --windowed main.py
   ```
   *Note: Providing `--windowed` hides the standard console window during execution, keeping it a pure background tray application. `--onefile` compiles it all into one convenient '.exe'.*
5. Navigate to `dist` to find the compiled `main.exe`. Make sure to place `config.json` next to the `.exe` so it can authenticate uploads.
