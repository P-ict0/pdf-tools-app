import os
import platform
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter

import styles  # Ensure this module is available in your project


def compress_pdf(input_file: str, output_file: str) -> None:
    """
    Compress a PDF file by rewriting it with potentially optimized settings.

    :param input_file: Path to the input PDF file
    :param output_file: Path to save the compressed PDF file
    """
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()  # CPU intensive!
        writer.add_page(page)

    writer.add_metadata(reader.metadata)

    with open(output_file, "wb") as fp:
        writer.write(fp)


def main(root_window=None) -> None:
    """
    Main function to run the PDF Compressor application.

    :param root_window: Root window to hide when the PDF Compressor is opened
    """

    def go_back():
        """
        Go back to the main window and close the PDF Compressor window.
        """
        compressor_window.destroy()
        if root_window:
            root_window.deiconify()

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
    is_animating = False
    original_size_mb = 0.0

    # Functions
    def select_input_file() -> None:
        """
        Select the input PDF file to compress and update the input file label.
        """
        nonlocal input_file, original_size_mb
        file = filedialog.askopenfilename(
            title="Select PDF File to Compress",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if file:
            input_file = file
            input_label.config(text=os.path.basename(input_file))
            original_size_mb = os.path.getsize(input_file) / (1024 * 1024)
            input_size_label.config(text=f"Original Size: {original_size_mb:.2f} MB")

    def select_output_file() -> None:
        """
        Select the output file path for the compressed PDF.
        """
        nonlocal output_file
        file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Select Output File",
        )
        if file:
            output_file = file
            output_label.config(text=os.path.basename(output_file))

    def compress() -> None:
        """
        Check if the selected files are valid and start the compression process.
        """
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        if not output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return

        # Disable button and start loading animation
        compress_btn.config(state="disabled")
        start_loading_animation()

        # Perform compression in a separate thread
        compress_thread = threading.Thread(target=perform_compression)
        compress_thread.start()

    def perform_compression() -> None:
        """
        Perform the compression process in a separate thread.
        """
        try:
            compress_pdf(input_file, output_file)
            compressed_size = os.path.getsize(output_file)
            compressed_size_mb = compressed_size / (1024 * 1024)
            compression_percentage = (
                ((original_size_mb - compressed_size_mb) / original_size_mb) * 100
                if original_size_mb > 0
                else 0
            )
            # Schedule the messagebox and other GUI updates in the main thread
            compressor_window.after(
                0,
                compression_completed,
                compressed_size_mb,
                compression_percentage,
            )
        except Exception as e:
            # Schedule the error message in the main thread
            compressor_window.after(0, compression_failed, e)

    def compression_completed(compressed_size_mb: float, compression_percentage: float) -> None:
        """
        Show a success message after the compression process is completed.
        """
        messagebox.showinfo(
            "Success",
            f"PDF has been compressed and saved to:\n{output_file}\n"
            f"Original Size: {original_size_mb:.2f} MB\n"
            f"Compressed Size: {compressed_size_mb:.2f} MB\n"
            f"Compression: {compression_percentage:.2f}%"
        )
        stop_loading_animation()
        update_compression_info(compressed_size_mb, compression_percentage)
        ask_to_open_or_close()

    def compression_failed(e: Exception) -> None:
        """
        Show an error message if the compression process fails.
        """
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        stop_loading_animation()

    def start_loading_animation() -> None:
        """
        Start the loading animation on the Compress button.
        """
        nonlocal is_animating
        is_animating = True
        compress_btn_text.set("Compressing.")
        animate_loading()

    def animate_loading() -> None:
        """
        Animate the loading text on the Compress button.
        """
        if not is_animating:
            return
        current_text = compress_btn_text.get()
        if current_text.endswith("..."):
            compress_btn_text.set("Compressing.")
        else:
            compress_btn_text.set(current_text + ".")
        compressor_window.after(500, animate_loading)  # Repeat animation every 500 ms

    def stop_loading_animation() -> None:
        """
        Stop the loading animation on the Compress button.
        """
        nonlocal is_animating
        is_animating = False
        compress_btn_text.set("Compress PDF")
        compress_btn.config(state="normal")

    def ask_to_open_or_close() -> None:
        """
        Ask the user if they want to open the compressed PDF file.
        """
        response = messagebox.askquestion(
            "Open Compressed PDF",
            "Do you want to open the compressed PDF file?",
        )
        if response == "yes":
            open_file(output_file)
        # Do not quit the application here; allow the user to continue using it if needed

    def open_file(filepath: str) -> None:
        """
        Open the compressed PDF file using the default application based on the platform.

        :param filepath: Path to the compressed PDF file
        """
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", filepath])
            else:  # Linux
                subprocess.call(["xdg-open", filepath])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file:\n{e}")

    def update_compression_info(new_size_mb: float, compression_percentage: float) -> None:
        """
        Update the GUI with compression information.

        :param new_size_mb: Size of the compressed PDF in MB
        :param compression_percentage: Percentage of compression achieved
        """
        compression_info_label.config(
            text=f"Compressed Size: {new_size_mb:.2f} MB ({compression_percentage:.2f}% reduction)"
        )

    # GUI Layout
    frame = ttk.Frame(compressor_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Back Button
    back_btn = ttk.Button(frame, text="← Back", command=go_back)
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
        frame, text="Select Output File", command=select_output_file, width=25
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
        """
        Handle the close event by destroying the PDF Compressor window and showing the root window.
        """
        compressor_window.destroy()
        if root_window:
            root_window.destroy()
        sys.exit(0)

    compressor_window.protocol("WM_DELETE_WINDOW", on_compressor_window_close)

    compressor_window.mainloop()


if __name__ == "__main__":
    main()
