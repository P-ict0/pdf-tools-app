import os
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfMerger
import subprocess
import sys

import styles


def merge_pdfs(file_paths: list[str], output_path: str) -> None:
    """
    Merge multiple PDF files into a single PDF file.

    :param file_paths: List of PDF file paths
    :param output_path: Output PDF file path
    """
    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def main(root_window=None) -> None:
    """
    Main function to run the PDF Merger application.

    :param root_window: Root window to hide when the PDF Merger is opened
    """

    def go_back():
        """
        Go back to the main window and close the PDF Merger window.
        """
        merger_window.destroy()
        if root_window:
            root_window.deiconify()

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
    selected_files = []
    output_file = ""
    is_animating = False

    # Functions
    def select_file() -> None:
        """
        Select PDF files to merge and update the list of selected files.
        """
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")],
        )
        for file in files:
            if file not in selected_files:
                selected_files.append(file)
        update_file_list()

    def update_file_list() -> None:
        """
        Update the list of selected files in the Listbox.
        """
        file_list.delete(0, tk.END)
        total_size = 0
        for idx, file in enumerate(selected_files):
            size = os.path.getsize(file)
            total_size += size
            size_mb = size / (1024 * 1024)
            file_list.insert(
                tk.END, f"{idx + 1}. {os.path.basename(file)} ({size_mb:.2f} MB)"
            )
        total_size_mb = total_size / (1024 * 1024)
        total_size_label.config(text=f"Total size: {total_size_mb:.2f} MB")

    def select_output_file() -> None:
        """
        Select the output file path for the merged PDF.
        """
        nonlocal output_file
        file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Select Output File",
        )
        output_file = file
        output_label.config(text=output_file or "No output file selected")

    def merge() -> None:
        """
        Check if the selected files and output file are valid and start the merging process.
        """
        if not output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return

        if not selected_files:
            messagebox.showerror("Error", "Please select files to merge.")
            return

        # Disable button and start loading animation
        merge_btn.config(state="disabled")
        start_loading_animation()

        # Perform merging in a separate thread
        merge_thread = threading.Thread(target=perform_merge)
        merge_thread.start()

    def perform_merge() -> None:
        """
        Perform the merging process in a separate thread.
        """
        try:
            merge_pdfs(selected_files, output_file)
            merged_size = os.path.getsize(output_file)
            merged_size_mb = merged_size / (1024 * 1024)
            # Schedule the messagebox and other GUI updates in the main thread
            merger_window.after(0, merge_completed, merged_size_mb)
        except Exception as e:
            # Schedule the error message in the main thread
            merger_window.after(0, merge_failed, e)

    def merge_completed(merged_size_mb: float) -> None:
        """
        Show a success message after the merging process is completed.
        """
        messagebox.showinfo(
            "Success",
            f"PDFs have been merged into:\n{output_file}\nTotal size: {merged_size_mb:.2f} MB",
        )
        stop_loading_animation()
        ask_to_open_or_close()

    def merge_failed(e: Exception) -> None:
        """
        Show an error message if the merging process fails.
        """
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        stop_loading_animation()

    def start_loading_animation() -> None:
        """
        Start the loading animation on the Merge PDFs button.
        """
        nonlocal is_animating
        is_animating = True
        merge_btn_text.set("Merging.")
        animate_loading()

    def animate_loading() -> None:
        """
        Animate the loading text on the Merge PDFs button.
        """
        if not is_animating:
            return
        current_text = merge_btn_text.get()
        if current_text.endswith("..."):
            merge_btn_text.set("Merging.")
        else:
            merge_btn_text.set(current_text + ".")
        merger_window.after(500, animate_loading)  # Repeat animation every 500 ms

    def stop_loading_animation() -> None:
        """
        Stop the loading animation on the Merge PDFs button.
        """
        nonlocal is_animating
        is_animating = False
        merge_btn_text.set("Merge PDFs")
        merge_btn.config(state="normal")

    def ask_to_open_or_close() -> None:
        """
        Ask the user if they want to open the merged PDF file.
        """
        response = messagebox.askquestion(
            "Open Merged PDF",
            "Do you want to open the merged PDF file?",
        )
        if response == "yes":
            open_file(output_file)
        # Do not quit the application here; allow the user to continue using it if needed

    def open_file(filepath: str) -> None:
        """
        Open the merged PDF file using the default application based on the platform.

        :param filepath: Path to the merged PDF file
        """
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])

    def move_up() -> None:
        """
        Move the selected PDF file up in the list.
        """
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
        """
        Move the selected PDF file down in the list.
        """
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
        """
        Delete the selected PDF file from the list.
        """
        selected_index = file_list.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "No PDF selected to delete.")
            return
        index = selected_index[0]
        selected_files.pop(index)  # Remove from list
        update_file_list()  # Refresh Listbox

    def delete_all_files() -> None:
        """
        Delete all selected PDF files from the list.
        """
        if not selected_files:
            messagebox.showwarning("Warning", "No PDFs to delete.")
            return
        if messagebox.askyesno(
            "Delete All", "Are you sure you want to delete all selected PDFs?"
        ):
            selected_files.clear()
            update_file_list()

    # GUI Layout
    frame = ttk.Frame(merger_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Back Button
    back_btn = ttk.Button(frame, text="← Back", command=go_back)
    back_btn.grid(row=0, column=0, sticky="w", pady=5)

    # Make rows and columns in the frame resizable
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(4, weight=1)

    # Add PDF button
    file_btn = ttk.Button(frame, text="Add PDFs", command=select_file, width=20)
    file_btn.grid(row=1, column=0, pady=5, sticky="w")

    # Select Output button
    output_btn = ttk.Button(
        frame, text="Select Output File", command=select_output_file, width=20
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

    # Handle the close event
    def on_merger_window_close():
        """
        Handle the close event by destroying the PDF Merger window and showing the root window.
        """
        merger_window.destroy()
        if root_window:
            root_window.destroy()
        sys.exit(0)

    merger_window.protocol("WM_DELETE_WINDOW", on_merger_window_close)

    merger_window.mainloop()


if __name__ == "__main__":
    main()
