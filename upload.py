import io
import base64
import requests
import uuid
from datetime import datetime
from config import load_config

def upload_image(img):
    config = load_config()
    if not config or not config.get("GITHUB_TOKEN") or config.get("GITHUB_TOKEN") == "YOUR_PERSONAL_ACCESS_TOKEN_HERE":
        print("GitHub configuration is missing or incomplete.")
        return None
        
    try:
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Base64 encode for GitHub API
        b64_content = base64.b64encode(img_bytes).decode('utf-8')
        
        token = config.get("GITHUB_TOKEN")
        repo = config.get("GITHUB_REPO")
        branch = config.get("GITHUB_BRANCH", "main")
        folder = config.get("UPLOAD_FOLDER", "screenshots").strip("/")
        
        # Generate filename
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
        path = f"{folder}/{filename}" if folder else filename
        
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "message": f"Upload {filename}",
            "content": b64_content,
            "branch": branch
        }
        
        response = requests.put(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        # Return raw URL
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
        return raw_url

    except Exception as e:
        print(f"Upload failed: {e}")
        return None
