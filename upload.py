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
        
        if response.status_code >= 400:
            error_msg = f"GitHub API {response.status_code}: {response.text}"
            with open("debug_log.txt", "a") as f:
                f.write(f"Upload failed - Status: {response.status_code}, Response: {response.text}\n")
            
            if response.status_code == 404:
                return (None, f"Not Found - check branch '{branch}' or repository name.")
            elif response.status_code == 401:
                return (None, "Unauthorized - check your GitHub Token.")
            return (None, f"Error: {response.status_code}")
            
        # Return raw URL
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
        return (raw_url, None)

    except Exception as e:
        with open("debug_log.txt", "a") as f:
            f.write(f"Upload Exception: {e}\n")
        return (None, str(e))
