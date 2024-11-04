import os
import platform
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter
import styles


def encrypt_pdf(input_file: str, output_file: str, password: str) -> None:
    """
    Encrypt a PDF file with a password.

    :param input_file: Path to the input PDF file
    :param output_file: Path to save the encrypted PDF file
    :param password: Password for encrypting the PDF
    """
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    with open(output_file, "wb") as f:
        writer.write(f)


def main(root_window=None) -> None:
    """
    Main function to run the PDF Encryption tool.

    :param root_window: Root window to hide when the PDF Encryptor is opened
    """

    def go_back():
        encryptor_window.destroy()
        if root_window:
            root_window.deiconify()

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

    # Functions
    def select_input_file() -> None:
        nonlocal input_file
        file = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if file:
            input_file = file
            input_label.config(text=os.path.basename(input_file))

    def select_output_file() -> None:
        nonlocal output_file
        file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Select Output File",
        )
        output_file = file
        output_label.config(
            text=os.path.basename(output_file) or "No output file selected"
        )

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

        try:
            reader = PdfReader(input_file)
            if reader.is_encrypted:
                messagebox.showerror("Error", "The selected PDF is already encrypted.")
                return

            encrypt_pdf(input_file, output_file, password.get())
            messagebox.showinfo(
                "Success", f"PDF has been encrypted and saved as:\n{output_file}"
            )
            ask_to_open_or_close()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

    def ask_to_open_or_close() -> None:
        response = messagebox.askquestion(
            "Open Encrypted PDF",
            "Do you want to open the encrypted PDF file?",
        )
        if response == "yes":
            open_file(output_file)

    def open_file(filepath: str) -> None:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])

    def toggle_password_visibility() -> None:
        if show_password_var.get():
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    # GUI Layout
    frame = ttk.Frame(encryptor_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Back Button
    back_btn = ttk.Button(frame, text="← Back", command=go_back, style="TButton")
    back_btn.grid(row=0, column=0, sticky="w", pady=5)

    # Input File Selection
    input_btn = ttk.Button(
        frame, text="Select PDF to Encrypt", command=select_input_file, style="TButton"
    )
    input_btn.grid(row=1, column=0, sticky="w", pady=5)
    input_label = ttk.Label(frame, text="No input file selected")
    input_label.grid(row=1, column=1, sticky="w", padx=10)

    # Output File Selection
    output_btn = ttk.Button(
        frame, text="Select Output File", command=select_output_file, style="TButton"
    )
    output_btn.grid(row=2, column=0, sticky="w", pady=5)
    output_label = ttk.Label(frame, text="No output file selected")
    output_label.grid(row=2, column=1, sticky="w", padx=10)

    # Password Entry
    password_label = ttk.Label(frame, text="Enter Password:")
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
    )
    show_password_cb.grid(row=3, column=2, sticky="w", padx=10)

    # Encrypt Button
    encrypt_btn = ttk.Button(
        frame, text="Encrypt PDF", command=encrypt, width=25, style="TButton"
    )
    encrypt_btn.grid(row=5, column=0, columnspan=3, pady=20)

    # Handle the close event
    def on_encryptor_window_close():
        encryptor_window.destroy()
        if root_window:
            root_window.destroy()
        sys.exit(0)

    encryptor_window.protocol("WM_DELETE_WINDOW", on_encryptor_window_close)
    encryptor_window.mainloop()
