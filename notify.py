import io
import win32clipboard
import pyperclip
from win11toast import toast

def copy_image_to_clipboard(img):
    try:
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        toast("Copied to Clipboard", "Screenshot has been copied successfully.")
    except Exception as e:
        toast("Error", f"Failed to copy image to clipboard: {e}")

def copy_text_to_clipboard_and_notify(text):
    pyperclip.copy(text)
    toast("Upload Complete", f"Direct link copied to clipboard:\n{text}", on_click=text)
