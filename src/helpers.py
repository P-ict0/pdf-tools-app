import sys
import os
from PyPDF2 import PdfReader


# Version retrieval
def get_base_path() -> str:
    """
    Get the base path of the application.
    """
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def get_version() -> str:
    """
    Get the current version of the local application.
    """
    try:
        base_path = get_base_path()
        version_path = os.path.join(base_path, "VERSION")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


def pdf_is_encrypted(file_path: str) -> bool:
    """
    Check if a PDF file is encrypted.
    """

    try:
        reader = PdfReader(file_path)
        return reader.is_encrypted
    except Exception:
        return False
