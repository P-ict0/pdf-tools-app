import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PyPDF2 import PdfReader, PdfWriter
from typing import Optional

import styles
from helpers import (
    go_back,
    select_files,
    select_output_file,
    on_failed,
    ask_to_open_or_close,
    open_file,
    Animation,
)


def encrypt_pdf(input_file: str, output_file: str, password: str) -> None:
    """
    Encrypt a PDF file with a password.

    :param input_file: Path to the input PDF file.
    :param output_file: Path to save the encrypted PDF file.
    :param password: Password for encrypting the PDF.
    """
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    with open(output_file, "wb") as f:
        writer.write(f)


def main(root_window: Optional[tk.Tk] = None) -> None:
    """
    Main function to run the PDF Encryption tool.

    :param root_window: Root window to hide when the PDF Encryptor is opened.
    """

    # Hide the root window if provided
    if root_window:
        root_window.withdraw()

    # Create a new window for the PDF Encryptor
    encryptor_window = tk.Toplevel()
    encryptor_window.title("PDF Encryptor")
    encryptor_window.geometry("600x400")
    encryptor_window.resizable(False, False)

    # Set up styles
    style = ttk.Style()
    styles.set_theme(style)
    encryptor_window.configure(bg=styles.BG_COLOR)

    # Variables
    input_file = ""
    output_file = ""
    password = tk.StringVar()

    # Initialize Animation
    encrypt_btn_text = tk.StringVar(value="Encrypt PDF")
    animation = Animation(encryptor_window, encrypt_btn_text, "Encrypting", interval=500)

    # Functions
    def select_input_file() -> None:
        nonlocal input_file
        files = select_files(
            multiple=False,
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if files:
            input_file = files[0]
            input_label.config(text=os.path.basename(input_file))

    def select_output() -> None:
        nonlocal output_file
        file = select_output_file(title="Select Output File")
        if file:
            output_file = file
            output_label.config(text=os.path.basename(output_file) or "No output file selected")

    def encrypt() -> None:
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        if not output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return

        if not password.get():
            messagebox.showerror("Error", "Please enter a password.")
            return

        # Disable button and start loading animation
        encrypt_btn.config(state="disabled")
        animation.start()

        # Perform encryption in a separate thread
        encrypt_thread = threading.Thread(target=perform_encryption)
        encrypt_thread.start()

    def perform_encryption() -> None:
        try:
            reader = PdfReader(input_file)
            if reader.is_encrypted:
                raise Exception("The selected PDF is already encrypted.")

            encrypt_pdf(input_file, output_file, password.get())
            # Schedule the success callback in the main thread
            encryptor_window.after(
                0,
                lambda: encryption_completed(),
            )
        except Exception as e:
            # Schedule the failure callback in the main thread
            encryptor_window.after(0, lambda: encryption_failed(e))

    def encryption_completed() -> None:
        messagebox.showinfo(
            "Success", f"PDF has been encrypted and saved as:\n{output_file}"
        )
        animation.stop("Encrypt PDF")
        ask_to_open_or_close("Open Encrypted PDF", "Do you want to open the encrypted PDF file?", output_file)
        encrypt_btn.config(state="normal")

    def encryption_failed(e: Exception) -> None:
        on_failed(e, "An error occurred during encryption:")
        animation.stop("Encrypt PDF")
        encrypt_btn.config(state="normal")

    def toggle_password_visibility() -> None:
        if show_password_var.get():
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    # GUI Layout
    frame = ttk.Frame(encryptor_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Back Button
    back_btn = ttk.Button(
        frame,
        text="← Back",
        command=lambda: go_back(encryptor_window, root_window),
        style="TButton"
    )
    back_btn.grid(row=0, column=0, sticky="w", pady=5)

    # Input File Selection
    input_btn = ttk.Button(
        frame,
        text="Select PDF to Encrypt",
        command=select_input_file,
        style="TButton"
    )
    input_btn.grid(row=1, column=0, sticky="w", pady=5)
    input_label = ttk.Label(frame, text="No input file selected", background=styles.BG_COLOR)
    input_label.grid(row=1, column=1, sticky="w", padx=10)

    # Output File Selection
    output_btn = ttk.Button(
        frame,
        text="Select Output File",
        command=select_output,
        style="TButton"
    )
    output_btn.grid(row=2, column=0, sticky="w", pady=5)
    output_label = ttk.Label(frame, text="No output file selected", background=styles.BG_COLOR)
    output_label.grid(row=2, column=1, sticky="w", padx=10)

    # Password Entry
    password_label = ttk.Label(frame, text="Enter Password:", background=styles.BG_COLOR)
    password_label.grid(row=3, column=0, sticky="w", pady=5)
    password_entry = ttk.Entry(frame, textvariable=password, show="*")
    password_entry.grid(row=3, column=1, sticky="w", padx=10)

    # Checkbox to view password
    show_password_var = tk.BooleanVar(value=False)
    show_password_cb = ttk.Checkbutton(
        frame,
        text="Show Password",
        variable=show_password_var,
        command=toggle_password_visibility,
        style="TCheckbutton"
    )
    show_password_cb.grid(row=3, column=2, sticky="w", padx=10)

    # Encrypt Button
    encrypt_btn = ttk.Button(
        frame,
        textvariable=encrypt_btn_text,
        command=encrypt,
        width=25,
        style="Large.TButton",
    )
    encrypt_btn.grid(row=5, column=0, columnspan=3, pady=20)

    # Handle the close event
    def on_encryptor_window_close():
        go_back(encryptor_window, root_window)

    encryptor_window.protocol("WM_DELETE_WINDOW", on_encryptor_window_close)

    encryptor_window.mainloop()


if __name__ == "__main__":
    main()
