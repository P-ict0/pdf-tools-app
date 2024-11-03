import sys
import os

# Application metadata
APP_NAME = "PDF Tools"
APP_AUTHOR = "P-ict0"
APP_URL = "https://github.com/P-ict0/pdf-merger-app"
AUTHOR_GITHUB = "https://github.com/P-ict0"


# Version retrieval
def get_base_path():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def get_version():
    try:
        base_path = get_base_path()
        version_path = os.path.join(base_path, "..", "VERSION")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


APP_VERSION = get_version()
