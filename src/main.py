import tkinter as tk
from tkinter import ttk
import sys
import webbrowser
import requests
from tkinter import messagebox
import os


def get_version():
    try:
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        version_path = os.path.join(base_path, "..", "VERSION")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


def check_for_updates(__version__):
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/P-ict0/pdf-merger-app/refs/heads/main/VERSION"
        )
        latest_version = response.text.strip()

        if latest_version > __version__:
            prompt_update(latest_version)
        else:
            print("You are using the latest version.")

    except Exception:
        pass  # Silently ignore any errors


def prompt_update(latest_version):
    if messagebox.askyesno(
        "Update Available",
        f"A new version ({latest_version}) is available. Do you want to download it?",
    ):
        webbrowser.open("https://github.com/P-ict0/pdf-merger-app/releases/latest")
        sys.exit(0)


def main():
    __version__ = get_version()
    print(f"PDF Tools version {__version__}")
    check_for_updates(__version__)

    root = tk.Tk()
    root.title("PDF Tools")
    root.geometry("400x300")
    root.resizable(True, True)

    # Create a frame
    frame = ttk.Frame(root, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Label
    label = ttk.Label(frame, text="Select a PDF tool:")
    label.pack(pady=10)

    # Buttons for each tool
    # For now, only PDF Merger
    def open_pdf_merger():
        root.destroy()  # Close the main window
        from tools.pdf_merger import pdf_merger_main

        pdf_merger_main()

    merger_button = ttk.Button(frame, text="PDF Merger", command=open_pdf_merger)
    merger_button.pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
