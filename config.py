"""
Configuration management for Gitsnap.
"""
import json
import os

def get_appdata_path():
    """
    Returns the path to the application data directory.
    Creates it if it does not exist.
    """
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    path = os.path.join(appdata, "Gitsnap")
    if not os.path.exists(path):
        os.makedirs(path)
    return path

CONFIG_FILE = os.path.join(get_appdata_path(), "config.json")
DEBUG_LOG_FILE = os.path.join(get_appdata_path(), "debug_log.txt")

DEFAULT_LOCATION = {
    "name": "Default",
    "token": "",
    "repo": "username/reponame",
    "branch": "main",
    "folder": "screenshots"
}

DEFAULT_CONFIG = {
    "DEFAULT_LOCATION": "Default",
    "GITHUB_LOCATIONS": [DEFAULT_LOCATION.copy()],
    "CUSTOM_HOTKEYS": [
        {"key": "s", "word": "", "location": "", "type": "image"}
    ]
}


def _migrate_old_config(data):
    """Migrate pre-locations flat config to the new schema."""
    old_keys = {"GITHUB_TOKEN", "GITHUB_REPO", "GITHUB_BRANCH", "UPLOAD_FOLDER"}
    if not any(k in data for k in old_keys):
        return data  # Nothing to migrate

    loc = {
        "name": "Default",
        "token": data.pop("GITHUB_TOKEN", ""),
        "repo": data.pop("GITHUB_REPO", "username/reponame"),
        "branch": data.pop("GITHUB_BRANCH", "main"),
        "folder": data.pop("UPLOAD_FOLDER", "screenshots"),
    }

    data.setdefault("DEFAULT_LOCATION", "Default")
    data.setdefault("GITHUB_LOCATIONS", [loc])

    # Ensure existing custom hotkeys have location and type fields
    for hk in data.get("CUSTOM_HOTKEYS", []):
        hk.setdefault("location", "")
        hk.setdefault("type", "image")

    # Seed Alt+S if not present
    keys_present = [hk.get("key", "") for hk in data.get("CUSTOM_HOTKEYS", [])]
    if "s" not in keys_present:
        data.setdefault("CUSTOM_HOTKEYS", []).insert(0, {"key": "s", "word": "", "location": "", "type": "image"})

    return data


def load_config():
    """
    Loads the configuration from the config.json file.
    Performs auto-migration if necessary.
    """
    if not os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG.copy()
        except Exception:
            return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    # Auto-migrate if old flat format detected
    if any(k in data for k in ("GITHUB_TOKEN", "GITHUB_REPO", "GITHUB_BRANCH", "UPLOAD_FOLDER")):
        data = _migrate_old_config(data)
        save_config(data)  # Persist migration immediately

    # Ensure Alt+S hotkey exists
    keys_present = [hk.get("key", "") for hk in data.get("CUSTOM_HOTKEYS", [])]
    if "s" not in keys_present:
        data.setdefault("CUSTOM_HOTKEYS", []).insert(0, {"key": "s", "word": "", "location": "", "type": "image"})
        save_config(data)

    return data


def save_config(config_data):
    """
    Saves the configuration to the config.json file.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_location(config, name=None):
    """
    Return the location dict matching `name`.
    Falls back to DEFAULT_LOCATION name, then the first location, then a blank default.
    """
    locations = config.get("GITHUB_LOCATIONS", [])
    default_name = config.get("DEFAULT_LOCATION", "")

    # If no name specified or empty, use the default
    target = name if name else default_name

    for loc in locations:
        if loc.get("name") == target:
            return loc

    # Fall back to first location
    if locations:
        return locations[0]

    return DEFAULT_LOCATION.copy()
