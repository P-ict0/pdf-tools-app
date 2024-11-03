# src/main.py

import tkinter as tk
from tkinter import ttk
import sys
import webbrowser
import requests
from tkinter import messagebox
import os

from config import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_URL,
    AUTHOR_GITHUB,
    get_version,
)
import styles


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
        webbrowser.open(f"{APP_URL}/releases/latest")
        sys.exit(0)


def main():
    __version__ = get_version()
    print(f"{APP_NAME} version {__version__}")
    check_for_updates(__version__)

    # Create the main window
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("600x400")
    root.resizable(False, False)

    # Set up styles
    style = ttk.Style()
    styles.set_theme(style)

    # Create a frame
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True, fill=tk.BOTH)

    # Title Label
    label = ttk.Label(frame, text="Select a PDF Tool:", font=styles.FONT_LARGE_BOLD)
    label.pack(pady=20)

    # Available tools
    tools = {
        "PDF Merger": "pdf_merger",
        # Add more tools here
    }

    # Function to open selected tool
    def open_tool(tool_module_name):
        root.withdraw()
        tool_module = __import__(f"tools.{tool_module_name}", fromlist=[""])
        tool_module.main(root)

    # Function to dynamically create tool buttons
    def create_tool_buttons():
        tool_frame = ttk.Frame(frame)
        tool_frame.pack(pady=10)

        max_cols = 3
        row = 0
        col = 0

        for tool_name, module_name in tools.items():
            btn = ttk.Button(
                tool_frame,
                text=tool_name,
                command=lambda m=module_name: open_tool(m),
                width=20,
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    create_tool_buttons()

    # Credits at the bottom
    def open_author_github(event):
        webbrowser.open(AUTHOR_GITHUB)

    credits_label = ttk.Label(
        frame,
        text=f"Created by {APP_AUTHOR}",
        foreground=styles.HIGHLIGHT_COLOR,
        cursor="hand2",
        font=styles.FONT_DEFAULT,
    )
    credits_label.pack(side="bottom", pady=10)
    credits_label.bind("<Button-1>", open_author_github)

    # Handle the close event
    def on_root_close():
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_root_close)

    root.mainloop()


if __name__ == "__main__":
    main()
