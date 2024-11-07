import os
import threading
import tkinter as tk
from tkinter import ttk
from PyPDF2 import PdfReader, PdfWriter
from typing import Optional

import styles
from .tool_window import ToolWindow, Animation


class Compressor(ToolWindow):
    def __init__(self, root_window: Optional[tk.Tk] = None):
        self.input_file = ""
        self.output_file = ""
        self.original_size_mb = 0.0
        super().__init__(root_window)

    def build_gui(self):
        self.title("PDF Compressor")
        self.geometry("600x480")
        self.resizable(False, False)
        self.configure(bg=styles.BG_COLOR)

        # Set up styles
        style = ttk.Style()
        styles.set_theme(style)

        # GUI Layout
        frame = ttk.Frame(self, padding=10)
        frame.pack(expand=True, fill=tk.BOTH)

        # Back Button
        back_btn = ttk.Button(frame, text="← Back", command=self.go_back)
        back_btn.grid(row=0, column=0, sticky="w", pady=5)

        # Make rows and columns in the frame resizable
        frame.columnconfigure(1, weight=1)

        # Input File Selection
        input_btn = ttk.Button(
            frame,
            text="Select PDF to Compress",
            command=self.select_input_file,
            width=25,
        )
        input_btn.grid(row=1, column=0, pady=10, sticky="w")

        self.input_label = ttk.Label(frame, text="No input file selected")
        self.input_label.grid(row=1, column=1, padx=10, sticky="w")

        # Original Size Label
        self.input_size_label = ttk.Label(frame, text="Original Size: N/A")
        self.input_size_label.grid(row=2, column=1, padx=10, sticky="w")

        # Output File Selection
        output_btn = ttk.Button(
            frame, text="Select Output File", command=self.select_output, width=25
        )
        output_btn.grid(row=3, column=0, pady=10, sticky="w")

        self.output_label = ttk.Label(frame, text="No output file selected")
        self.output_label.grid(row=3, column=1, padx=10, sticky="w")

        # Compression Information Label
        self.compression_info_label = ttk.Label(frame, text="")
        self.compression_info_label.grid(
            row=4, column=0, columnspan=2, pady=10, sticky="w"
        )

        # Compress Button
        self.compress_btn_text = tk.StringVar(value="Compress PDF")
        self.compress_btn = ttk.Button(
            frame,
            textvariable=self.compress_btn_text,
            command=self.compress,
            width=30,
            style="Large.TButton",
        )
        self.compress_btn.grid(row=5, column=0, columnspan=2, pady=20)

        # Initialize Animation
        self.animation = Animation(self, self.compress_btn_text, "Compressing")

        # Warning Label
        warning_label = ttk.Label(
            frame,
            text="⚠️ Note: Compression effectiveness varies depending on the PDF content.",
            foreground="red",
            wraplength=580,
            justify="center",
            font=("Helvetica", 10, "italic"),
        )
        warning_label.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="nsew")

    def select_input_file(self) -> None:
        files = self.select_files(
            multiple=False,
            title="Select PDF File to Compress",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if files:
            self.input_file = files[0]
            self.input_label.config(text=os.path.basename(self.input_file))
            self.original_size_mb = os.path.getsize(self.input_file) / (1024 * 1024)
            self.input_size_label.config(
                text=f"Original Size: {self.original_size_mb:.2f} MB"
            )

    def select_output(self) -> None:
        file = self.select_output_file(title="Select Output File")
        if file:
            self.output_file = file
            self.output_label.config(text=os.path.basename(self.output_file))

    def compress(self) -> None:
        if not self.input_file:
            tk.messagebox.showerror("Error", "Please select an input file.")
            return

        if not self.output_file:
            tk.messagebox.showerror("Error", "Please select an output file.")
            return

        # Disable button and start loading animation
        self.compress_btn.config(state="disabled")
        self.animation.start()

        # Perform compression in a separate thread
        compress_thread = threading.Thread(target=self.perform_compression)
        compress_thread.start()

    def perform_compression(self) -> None:
        try:
            self.compress_pdf(self.input_file, self.output_file)
            compressed_size = os.path.getsize(self.output_file)
            compressed_size_mb = compressed_size / (1024 * 1024)
            compression_percentage = (
                ((self.original_size_mb - compressed_size_mb) / self.original_size_mb)
                * 100
                if self.original_size_mb > 0
                else 0
            )
            # Schedule the success callback in the main thread
            self.after(
                0,
                lambda: self.compression_completed(
                    compressed_size_mb, compression_percentage
                ),
            )
        except Exception as e:
            # Schedule the failure callback in the main thread
            self.after(0, lambda e=e: self.compression_failed(e))

    def compress_pdf(self, input_file: str, output_file: str) -> None:
        """
        Compress a PDF file by rewriting it with potentially optimized settings.
        """
        reader = PdfReader(input_file)
        writer = PdfWriter()

        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)

        writer.add_metadata(reader.metadata)

        with open(output_file, "wb") as fp:
            writer.write(fp)

    def compression_completed(
        self, compressed_size_mb: float, compression_percentage: float
    ) -> None:
        tk.messagebox.showinfo(
            "Success",
            f"PDF has been compressed and saved to:\n{self.output_file}\n"
            f"Original Size: {self.original_size_mb:.2f} MB\n"
            f"Compressed Size: {compressed_size_mb:.2f} MB\n"
            f"Compression: {compression_percentage:.2f}%",
        )
        self.animation.stop("Compress PDF")
        self.update_compression_info(compressed_size_mb, compression_percentage)
        self.ask_to_open_or_close(
            "Open Compressed PDF",
            "Do you want to open the compressed PDF file?",
            self.output_file,
        )
        self.compress_btn.config(state="normal")

    def compression_failed(self, e: Exception) -> None:
        self.on_failed(e, "An error occurred during compression:")
        self.animation.stop("Compress PDF")
        self.compress_btn.config(state="normal")

    def update_compression_info(
        self, new_size_mb: float, compression_percentage: float
    ) -> None:
        self.compression_info_label.config(
            text=f"Compressed Size: {new_size_mb:.2f} MB ({compression_percentage:.2f}% reduction)"
        )
