import os
import threading
import tkinter as tk
from tkinter import ttk
from PyPDF2 import PdfMerger
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


def merge_pdfs(file_paths: list[str], output_path: str) -> None:
    """
    Merge multiple PDF files into a single PDF file.

    :param file_paths: List of PDF file paths.
    :param output_path: Output PDF file path.
    """
    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def main(root_window: Optional[tk.Tk] = None) -> None:
    """
    Main function to run the PDF Merger application.

    :param root_window: Root window to hide when the PDF Merger is opened.
    """

    # Hide the root window if provided
    if root_window:
        root_window.withdraw()

    # Create a new window for the PDF Merger
    merger_window = tk.Toplevel()
    merger_window.title("PDF Merger")
    merger_window.geometry("900x600")
    merger_window.resizable(True, True)

    # Set up styles
    style = ttk.Style()
    styles.set_theme(style)

    merger_window.configure(bg=styles.BG_COLOR)

    # Variables
    selected_files: list[str] = []
    output_file = ""
    total_size_mb = 0.0

    # Functions
    def select_files_func() -> None:
        nonlocal selected_files
        files = select_files(
            multiple=True,
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")],
        )
        for file in files:
            if file not in selected_files:
                selected_files.append(file)
        update_file_list()

    def update_file_list() -> None:
        file_list.delete(0, tk.END)
        total_size = 0
        for idx, file in enumerate(selected_files):
            size = os.path.getsize(file)
            total_size += size
            size_mb = size / (1024 * 1024)
            file_list.insert(
                tk.END, f"{idx + 1}. {os.path.basename(file)} ({size_mb:.2f} MB)"
            )
        nonlocal total_size_mb
        total_size_mb = total_size / (1024 * 1024)
        total_size_label.config(text=f"Total size: {total_size_mb:.2f} MB")

    def select_output() -> None:
        nonlocal output_file
        file = select_output_file(title="Select Output File")
        if file:
            output_file = file
            output_label.config(text=output_file or "No output file selected")

    def merge() -> None:
        if not output_file:
            tk.messagebox.showerror("Error", "Please select an output file.")
            return

        if not selected_files:
            tk.messagebox.showerror("Error", "Please select files to merge.")
            return

        # Disable button and start loading animation
        merge_btn.config(state="disabled")
        animation.start()

        # Perform merging in a separate thread
        merge_thread = threading.Thread(target=perform_merge)
        merge_thread.start()

    def perform_merge() -> None:
        try:
            merge_pdfs(selected_files, output_file)
            merged_size = os.path.getsize(output_file)
            merged_size_mb = merged_size / (1024 * 1024)
            # Schedule the success callback in the main thread
            merger_window.after(
                0,
                lambda: merge_completed(merged_size_mb),
            )
        except Exception as e:
            # Schedule the failure callback in the main thread
            merger_window.after(0, lambda: merge_failed(e))

    def merge_completed(merged_size_mb: float) -> None:
        tk.messagebox.showinfo(
            "Success",
            f"PDFs have been merged into:\n{output_file}\nTotal size: {merged_size_mb:.2f} MB",
        )
        animation.stop("Merge PDFs")
        ask_to_open_or_close("Open Merged PDF", "Do you want to open the merged PDF file?", output_file)
        merge_btn.config(state="normal")

    def merge_failed(e: Exception) -> None:
        on_failed(e, "An error occurred during merging:")
        animation.stop("Merge PDFs")
        merge_btn.config(state="normal")

    def move_up() -> None:
        selected_index = file_list.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if index > 0:
            selected_files[index], selected_files[index - 1] = (
                selected_files[index - 1],
                selected_files[index],
            )
            update_file_list()
            file_list.select_set(index - 1)

    def move_down() -> None:
        selected_index = file_list.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if index < len(selected_files) - 1:
            selected_files[index], selected_files[index + 1] = (
                selected_files[index + 1],
                selected_files[index],
            )
            update_file_list()
            file_list.select_set(index + 1)

    def delete_selected_file() -> None:
        selected_index = file_list.curselection()
        if not selected_index:
            tk.messagebox.showwarning("Warning", "No PDF selected to delete.")
            return
        index = selected_index[0]
        selected_files.pop(index)  # Remove from list
        update_file_list()  # Refresh Listbox

    def delete_all_files() -> None:
        if not selected_files:
            tk.messagebox.showwarning("Warning", "No PDFs to delete.")
            return
        if tk.messagebox.askyesno(
            "Delete All", "Are you sure you want to delete all selected PDFs?"
        ):
            selected_files.clear()
            update_file_list()

    # GUI Layout
    frame = ttk.Frame(merger_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Back Button
    back_btn = ttk.Button(frame, text="← Back", command=lambda: go_back(merger_window, root_window))
    back_btn.grid(row=0, column=0, sticky="w", pady=5)

    # Make rows and columns in the frame resizable
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(4, weight=1)

    # Add PDF button
    file_btn = ttk.Button(frame, text="Add PDFs", command=select_files_func, width=20)
    file_btn.grid(row=1, column=0, pady=5, sticky="w")

    # Select Output button
    output_btn = ttk.Button(
        frame, text="Select Output File", command=select_output, width=20
    )
    output_btn.grid(row=2, column=0, pady=5, sticky="w")

    # Output path label
    output_label = ttk.Label(frame, text="No output file selected")
    output_label.grid(row=2, column=1, padx=5, sticky="w")

    # Selected PDFs label
    file_list_label = ttk.Label(frame, text="Selected PDFs:")
    file_list_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

    # Listbox with updated colors
    file_list = tk.Listbox(
        frame,
        selectmode=tk.SINGLE,
        bg=styles.BG_COLOR,
        fg=styles.FG_COLOR,
        font=("Helvetica", 12),
        highlightbackground=styles.HIGHLIGHT_COLOR,
        selectbackground=styles.HIGHLIGHT_COLOR,
        selectforeground=styles.BG_COLOR,
    )
    file_list.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    # Total size label
    total_size_label = ttk.Label(frame, text="Total size: 0.00 MB")
    total_size_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)

    # Move Up and Move Down buttons
    move_up_btn = ttk.Button(frame, text="Move ↑", command=move_up, width=20)
    move_up_btn.grid(row=4, column=2, padx=5, pady=(5, 0), sticky="n")

    move_down_btn = ttk.Button(frame, text="Move ↓", command=move_down, width=20)
    move_down_btn.grid(row=4, column=2, padx=5, pady=(60, 5), sticky="n")

    # Delete PDF button
    delete_btn = ttk.Button(
        frame, text="Delete PDF", command=delete_selected_file, width=20
    )
    delete_btn.grid(row=4, column=2, padx=5, pady=(115, 5), sticky="n")

    # Delete All button
    delete_all_btn = ttk.Button(
        frame, text="Delete All", command=delete_all_files, width=20
    )
    delete_all_btn.grid(row=4, column=2, padx=5, pady=(170, 5), sticky="n")

    # Merge PDFs Button
    merge_btn_text = tk.StringVar(value="Merge PDFs")
    merge_btn = ttk.Button(
        frame,
        textvariable=merge_btn_text,
        command=merge,
        width=25,
        style="Large.TButton",  # Use the large button style
    )
    merge_btn.grid(row=6, column=0, columnspan=3, pady=20)

    # Initialize Animation
    animation = Animation(merger_window, merge_btn_text, "Merging")

    # Handle the close event
    def on_merger_window_close():
        go_back(merger_window, root_window)

    merger_window.protocol("WM_DELETE_WINDOW", on_merger_window_close)

    merger_window.mainloop()


if __name__ == "__main__":
    main()
