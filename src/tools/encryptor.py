import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import fitz
from typing import Optional

from helpers import pdf_is_encrypted
import styles
from .tool_window import ToolWindow, Animation


class Encryptor(ToolWindow):
    def __init__(self, root_window: Optional[tk.Tk] = None):
        self.input_file = ""
        self.output_file = ""
        self.password = tk.StringVar()
        super().__init__(root_window)

    def build_gui(self):
        self.title("PDF Encryptor/Decryptor")
        self.geometry("600x450")
        self.resizable(False, False)
        self.configure(bg=styles.BG_COLOR)

        # Set up styles
        style = ttk.Style()
        styles.set_theme(style)

        # Initialize Animation
        self.encrypt_btn_text = tk.StringVar(value="Encrypt PDF")
        self.decrypt_btn_text = tk.StringVar(value="Decrypt PDF")
        self.animation = None  # Will be initialized in encrypt/decrypt methods

        # GUI Layout
        frame = ttk.Frame(self, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        # Back Button
        back_btn = ttk.Button(
            frame, text="← Back", command=self.go_back, style="TButton"
        )
        back_btn.grid(row=0, column=0, sticky="w", pady=5)

        # Input File Selection
        input_btn = ttk.Button(
            frame,
            text="Select PDF File",
            command=self.select_input_file,
            style="TButton",
        )
        input_btn.grid(row=1, column=0, sticky="w", pady=5)
        self.input_label = ttk.Label(
            frame, text="No input file selected", background=styles.BG_COLOR
        )
        self.input_label.grid(row=1, column=1, sticky="w", padx=10)

        # Output File Selection
        output_btn = ttk.Button(
            frame,
            text="Select Output File",
            command=self.select_output,
            style="TButton",
        )
        output_btn.grid(row=2, column=0, sticky="w", pady=5)
        self.output_label = ttk.Label(
            frame, text="No output file selected", background=styles.BG_COLOR
        )
        self.output_label.grid(row=2, column=1, sticky="w", padx=10)

        # Password Entry
        password_label = ttk.Label(
            frame, text="Enter Password:", background=styles.BG_COLOR
        )
        password_label.grid(row=3, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, textvariable=self.password, show="*")
        self.password_entry.grid(row=3, column=1, sticky="w", padx=10)

        # Checkbox to view password
        self.show_password_var = tk.BooleanVar(value=False)
        show_password_cb = ttk.Checkbutton(
            frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            style="TCheckbutton",
        )
        show_password_cb.grid(row=3, column=2, sticky="w", padx=10)

        # Warning Label
        warning_label = ttk.Label(
            frame,
            text=(
                "⚠️ Warning: Encrypting or decrypting large PDF files may "
                "take a significant amount of time."
            ),
            foreground="red",
            wraplength=580,
            justify="center",
            font=("Helvetica", 10, "italic"),
            background=styles.BG_COLOR,
        )
        warning_label.grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky="w")

        # Encrypt and Decrypt Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        self.encrypt_btn = ttk.Button(
            button_frame,
            textvariable=self.encrypt_btn_text,
            command=self.encrypt,
            width=20,
            style="Large.TButton",
        )
        self.encrypt_btn.grid(row=0, column=0, padx=5)

        self.decrypt_btn = ttk.Button(
            button_frame,
            textvariable=self.decrypt_btn_text,
            command=self.decrypt,
            width=20,
            style="Large.TButton",
        )
        self.decrypt_btn.grid(row=0, column=1, padx=5)

    def select_input_file(self) -> None:
        files = self.select_files(
            multiple=False,
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if files:
            self.input_file = files[0]
            self.input_label.config(text=os.path.basename(self.input_file))

    def select_output(self) -> None:
        file = self.select_output_file(title="Select Output File")
        if file:
            self.output_file = file
            self.output_label.config(
                text=os.path.basename(self.output_file) or "No output file selected"
            )

    def encrypt(self) -> None:
        if not self.input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        if not self.output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return

        if not self.password.get():
            messagebox.showerror("Error", "Please enter a password.")
            return

        # Check if the PDF is already encrypted
        if pdf_is_encrypted(self.input_file):
            messagebox.showerror("Error", "The selected PDF is already encrypted.")
            return

        # Disable buttons and start loading animation
        self.encrypt_btn.config(state="disabled")
        self.decrypt_btn.config(state="disabled")
        self.animation = Animation(
            self, self.encrypt_btn_text, "Encrypting", interval=500
        )
        self.animation.start()

        # Perform encryption in a separate thread
        encrypt_thread = threading.Thread(target=self.perform_encryption)
        encrypt_thread.start()

    def decrypt(self) -> None:
        if not self.input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        if not self.output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return

        if not self.password.get():
            messagebox.showerror("Error", "Please enter a password.")
            return

        # Check if the PDF is encrypted
        if not pdf_is_encrypted(self.input_file):
            messagebox.showerror("Error", "The selected PDF is not encrypted.")
            return

        # Disable buttons and start loading animation
        self.decrypt_btn.config(state="disabled")
        self.encrypt_btn.config(state="disabled")
        self.animation = Animation(
            self, self.decrypt_btn_text, "Decrypting", interval=500
        )
        self.animation.start()

        # Perform decryption in a separate thread
        decrypt_thread = threading.Thread(target=self.perform_decryption)
        decrypt_thread.start()

    def perform_encryption(self) -> None:
        try:
            self.encrypt_pdf(self.input_file, self.output_file, self.password.get())
            self.after(0, self.encryption_completed)
        except Exception as e:
            self.after(0, lambda e=e: self.encryption_failed(e))

    def perform_decryption(self) -> None:
        try:
            self.decrypt_pdf(self.input_file, self.output_file, self.password.get())
            self.after(0, self.decryption_completed)
        except Exception as e:
            self.after(0, lambda e=e: self.decryption_failed(e))

    def encrypt_pdf(self, input_file: str, output_file: str, password: str) -> None:
        """
        Encrypt a PDF file with a user password using PyMuPDF (fitz).
        """
        # Open the PDF normally (not encrypted)
        with fitz.open(input_file) as doc:
            doc.save(
                output_file,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                owner_pw=password,
                user_pw=password,
            )

    def decrypt_pdf(self, input_file: str, output_file: str, password: str) -> None:
        """
        Decrypt a PDF file with a password using PyMuPDF (fitz).
        """
        # If the file is encrypted, you must open it with the correct password
        with fitz.open(input_file, filetype="pdf") as doc:
            # Authenticate with the password
            if not doc.authenticate(password):
                raise ValueError("Incorrect password provided for PDF decryption.")
            # Save with no encryption
            doc.save(output_file)

    #
    #   CALLBACKS
    #
    def encryption_completed(self) -> None:
        messagebox.showinfo(
            "Success", f"PDF has been encrypted and saved as:\n{self.output_file}"
        )
        self.animation.stop("Encrypt PDF")
        self.ask_to_open_or_close(
            "Open Encrypted PDF",
            "Do you want to open the encrypted PDF file?",
            self.output_file,
        )
        self.encrypt_btn.config(state="normal")
        self.decrypt_btn.config(state="normal")

    def encryption_failed(self, e: Exception) -> None:
        self.on_failed(e, "An error occurred during encryption:")
        self.animation.stop("Encrypt PDF")
        self.encrypt_btn.config(state="normal")
        self.decrypt_btn.config(state="normal")

    def decryption_completed(self) -> None:
        messagebox.showinfo(
            "Success", f"PDF has been decrypted and saved as:\n{self.output_file}"
        )
        self.animation.stop("Decrypt PDF")
        self.ask_to_open_or_close(
            "Open Decrypted PDF",
            "Do you want to open the decrypted PDF file?",
            self.output_file,
        )
        self.decrypt_btn.config(state="normal")
        self.encrypt_btn.config(state="normal")

    def decryption_failed(self, e: Exception) -> None:
        self.on_failed(e, "An error occurred during decryption:")
        self.animation.stop("Decrypt PDF")
        self.decrypt_btn.config(state="normal")
        self.encrypt_btn.config(state="normal")

    def toggle_password_visibility(self) -> None:
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
