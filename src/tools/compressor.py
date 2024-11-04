import os
import threading
import tkinter as tk
from tkinter import ttk
from PyPDF2 import PdfReader, PdfWriter
from typing import Optional

import styles
from helpers import (
    go_back,
    select_files,
    select_output_file,
    on_failed,
    Animation,
    ask_to_open_or_close,
    open_file,
)


def compress_pdf(input_file: str, output_file: str) -> None:
    """
    Compress a PDF file by rewriting it with potentially optimized settings.

    :param input_file: Path to the input PDF file.
    :param output_file: Path to save the compressed PDF file.
    """
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()  # CPU intensive!
        writer.add_page(page)

    writer.add_metadata(reader.metadata)

    with open(output_file, "wb") as fp:
        writer.write(fp)


def main(root_window: Optional[tk.Tk] = None) -> None:
    """
    Main function to run the PDF Compressor application.

    :param root_window: Root window to hide when the PDF Compressor is opened.
    """

    # Hide the root window if provided
    if root_window:
        root_window.withdraw()

    # Create a new window for the PDF Compressor
    compressor_window = tk.Toplevel()
    compressor_window.title("PDF Compressor")
    compressor_window.geometry("600x480")  # Increased height to accommodate new warning
    compressor_window.resizable(False, False)

    # Set up styles
    style = ttk.Style()
    styles.set_theme(style)

    compressor_window.configure(bg=styles.BG_COLOR)

    # Variables
    input_file = ""
    output_file = ""
    original_size_mb = 0.0

    # Functions
    def select_input_file() -> None:
        nonlocal input_file, original_size_mb
        files = select_files(
            multiple=False,
            title="Select PDF File to Compress",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if files:
            input_file = files[0]
            input_label.config(text=os.path.basename(input_file))
            original_size_mb = os.path.getsize(input_file) / (1024 * 1024)
            input_size_label.config(text=f"Original Size: {original_size_mb:.2f} MB")

    def select_output() -> None:
        nonlocal output_file
        file = select_output_file(title="Select Output File")
        if file:
            output_file = file
            output_label.config(text=os.path.basename(output_file))

    def compress() -> None:
        if not input_file:
            tk.messagebox.showerror("Error", "Please select an input file.")
            return

        if not output_file:
            tk.messagebox.showerror("Error", "Please select an output file.")
            return

        # Disable button and start loading animation
        compress_btn.config(state="disabled")
        animation.start()

        # Perform compression in a separate thread
        compress_thread = threading.Thread(target=perform_compression)
        compress_thread.start()

    def perform_compression() -> None:
        try:
            compress_pdf(input_file, output_file)
            compressed_size = os.path.getsize(output_file)
            compressed_size_mb = compressed_size / (1024 * 1024)
            compression_percentage = (
                ((original_size_mb - compressed_size_mb) / original_size_mb) * 100
                if original_size_mb > 0
                else 0
            )
            # Schedule the success callback in the main thread
            compressor_window.after(
                0,
                lambda: compression_completed(
                    compressed_size_mb, compression_percentage
                ),
            )
        except Exception as e:
            # Schedule the failure callback in the main thread
            compressor_window.after(0, lambda: compression_failed(e))

    def compression_completed(
        compressed_size_mb: float, compression_percentage: float
    ) -> None:
        tk.messagebox.showinfo(
            "Success",
            f"PDF has been compressed and saved to:\n{output_file}\n"
            f"Original Size: {original_size_mb:.2f} MB\n"
            f"Compressed Size: {compressed_size_mb:.2f} MB\n"
            f"Compression: {compression_percentage:.2f}%",
        )
        animation.stop("Compress PDF")
        update_compression_info(compressed_size_mb, compression_percentage)
        ask_to_open_or_close(
            "Open Compressed PDF",
            "Do you want to open the compressed PDF file?",
            output_file,
        )
        compress_btn.config(state="normal")

    def compression_failed(e: Exception) -> None:
        on_failed(e, "An error occurred during compression:")
        animation.stop("Compress PDF")
        compress_btn.config(state="normal")

    def update_compression_info(
        new_size_mb: float, compression_percentage: float
    ) -> None:
        compression_info_label.config(
            text=f"Compressed Size: {new_size_mb:.2f} MB ({compression_percentage:.2f}% reduction)"
        )

    # GUI Layout
    frame = ttk.Frame(compressor_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Back Button
    back_btn = ttk.Button(
        frame, text="← Back", command=lambda: go_back(compressor_window, root_window)
    )
    back_btn.grid(row=0, column=0, sticky="w", pady=5)

    # Make rows and columns in the frame resizable
    frame.columnconfigure(1, weight=1)

    # Input File Selection
    input_btn = ttk.Button(
        frame, text="Select PDF to Compress", command=select_input_file, width=25
    )
    input_btn.grid(row=1, column=0, pady=10, sticky="w")

    input_label = ttk.Label(frame, text="No input file selected")
    input_label.grid(row=1, column=1, padx=10, sticky="w")

    # Original Size Label
    input_size_label = ttk.Label(frame, text="Original Size: N/A")
    input_size_label.grid(row=2, column=1, padx=10, sticky="w")

    # Output File Selection
    output_btn = ttk.Button(
        frame, text="Select Output File", command=select_output, width=25
    )
    output_btn.grid(row=3, column=0, pady=10, sticky="w")

    output_label = ttk.Label(frame, text="No output file selected")
    output_label.grid(row=3, column=1, padx=10, sticky="w")

    # Compression Information Label (Initially hidden)
    compression_info_label = ttk.Label(frame, text="")
    compression_info_label.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")

    # Compress Button
    compress_btn_text = tk.StringVar(value="Compress PDF")
    compress_btn = ttk.Button(
        frame,
        textvariable=compress_btn_text,
        command=compress,
        width=30,
        style="Large.TButton",  # Ensure this style is defined in your styles module
    )
    compress_btn.grid(row=5, column=0, columnspan=2, pady=20)

    # Initialize Animation
    animation = Animation(compressor_window, compress_btn_text, "Compressing")

    # Warning Label
    warning_label = ttk.Label(
        frame,
        text="⚠️ Note: Compression effectiveness varies depending on the PDF content.",
        foreground="red",
        wraplength=580,  # Adjust wrap length as needed
        justify="center",
        font=("Helvetica", 10, "italic"),
    )
    warning_label.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="nsew")

    # Handle the close event
    def on_compressor_window_close():
        go_back(compressor_window, root_window)

    compressor_window.protocol("WM_DELETE_WINDOW", on_compressor_window_close)

    compressor_window.mainloop()


if __name__ == "__main__":
    main()
