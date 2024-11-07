import os
import threading
import tkinter as tk
from tkinter import ttk
from PyPDF2 import PdfMerger
from typing import Optional

import styles
from .tool_window import ToolWindow, Animation


class Merger(ToolWindow):
    def __init__(self, root_window: Optional[tk.Tk] = None):
        self.selected_files: list[str] = []
        self.output_file = ""
        self.total_size_mb = 0.0
        super().__init__(root_window)

    def build_gui(self):
        self.title("PDF Merger")
        self.geometry("900x600")
        self.resizable(True, True)
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
        frame.rowconfigure(4, weight=1)

        # Add PDF button
        file_btn = ttk.Button(
            frame, text="Add PDFs", command=self.select_files_func, width=20
        )
        file_btn.grid(row=1, column=0, pady=5, sticky="w")

        # Select Output button
        output_btn = ttk.Button(
            frame, text="Select Output File", command=self.select_output, width=20
        )
        output_btn.grid(row=2, column=0, pady=5, sticky="w")

        # Output path label
        self.output_label = ttk.Label(frame, text="No output file selected")
        self.output_label.grid(row=2, column=1, padx=5, sticky="w")

        # Selected PDFs label
        file_list_label = ttk.Label(frame, text="Selected PDFs:")
        file_list_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        # Listbox with updated colors
        self.file_list = tk.Listbox(
            frame,
            selectmode=tk.SINGLE,
            bg=styles.BG_COLOR,
            fg=styles.FG_COLOR,
            font=("Helvetica", 12),
            highlightbackground=styles.HIGHLIGHT_COLOR,
            selectbackground=styles.HIGHLIGHT_COLOR,
            selectforeground=styles.BG_COLOR,
        )
        self.file_list.grid(
            row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew"
        )

        # Total size label
        self.total_size_label = ttk.Label(frame, text="Total size: 0.00 MB")
        self.total_size_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)

        # Move Up and Move Down buttons
        move_up_btn = ttk.Button(frame, text="Move ↑", command=self.move_up, width=20)
        move_up_btn.grid(row=4, column=2, padx=5, pady=(5, 0), sticky="n")

        move_down_btn = ttk.Button(
            frame, text="Move ↓", command=self.move_down, width=20
        )
        move_down_btn.grid(row=4, column=2, padx=5, pady=(60, 5), sticky="n")

        # Delete PDF button
        delete_btn = ttk.Button(
            frame, text="Delete PDF", command=self.delete_selected_file, width=20
        )
        delete_btn.grid(row=4, column=2, padx=5, pady=(115, 5), sticky="n")

        # Delete All button
        delete_all_btn = ttk.Button(
            frame, text="Delete All", command=self.delete_all_files, width=20
        )
        delete_all_btn.grid(row=4, column=2, padx=5, pady=(170, 5), sticky="n")

        # Merge PDFs Button
        self.merge_btn_text = tk.StringVar(value="Merge PDFs")
        self.merge_btn = ttk.Button(
            frame,
            textvariable=self.merge_btn_text,
            command=self.merge,
            width=25,
            style="Large.TButton",
        )
        self.merge_btn.grid(row=6, column=0, columnspan=3, pady=20)

        # Initialize Animation
        self.animation = Animation(self, self.merge_btn_text, "Merging")

    def select_files_func(self) -> None:
        files = self.select_files(
            multiple=True,
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")],
        )
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
        self.update_file_list()

    def update_file_list(self) -> None:
        self.file_list.delete(0, tk.END)
        total_size = 0
        for idx, file in enumerate(self.selected_files):
            size = os.path.getsize(file)
            total_size += size
            size_mb = size / (1024 * 1024)
            self.file_list.insert(
                tk.END, f"{idx + 1}. {os.path.basename(file)} ({size_mb:.2f} MB)"
            )
        self.total_size_mb = total_size / (1024 * 1024)
        self.total_size_label.config(text=f"Total size: {self.total_size_mb:.2f} MB")

    def select_output(self) -> None:
        file = self.select_output_file(title="Select Output File")
        if file:
            self.output_file = file
            self.output_label.config(text=self.output_file or "No output file selected")

    def merge(self) -> None:
        if not self.output_file:
            tk.messagebox.showerror("Error", "Please select an output file.")
            return

        if not self.selected_files:
            tk.messagebox.showerror("Error", "Please select files to merge.")
            return

        # Disable button and start loading animation
        self.merge_btn.config(state="disabled")
        self.animation.start()

        # Perform merging in a separate thread
        merge_thread = threading.Thread(target=self.perform_merge)
        merge_thread.start()

    def perform_merge(self) -> None:
        try:
            self.merge_pdfs(self.selected_files, self.output_file)
            merged_size = os.path.getsize(self.output_file)
            merged_size_mb = merged_size / (1024 * 1024)
            # Schedule the success callback in the main thread
            self.after(
                0,
                lambda: self.merge_completed(merged_size_mb),
            )
        except Exception as e:
            # Schedule the failure callback in the main thread
            self.after(0, lambda e=e: self.merge_failed(e))

    def merge_pdfs(self, file_paths: list[str], output_path: str) -> None:
        """
        Merge multiple PDF files into a single PDF file.
        """
        merger = PdfMerger()
        for pdf in file_paths:
            merger.append(pdf)
        merger.write(output_path)
        merger.close()

    def merge_completed(self, merged_size_mb: float) -> None:
        tk.messagebox.showinfo(
            "Success",
            f"PDFs have been merged into:\n{self.output_file}\nTotal size: {merged_size_mb:.2f} MB",
        )
        self.animation.stop("Merge PDFs")
        self.ask_to_open_or_close(
            "Open Merged PDF",
            "Do you want to open the merged PDF file?",
            self.output_file,
        )
        self.merge_btn.config(state="normal")

    def merge_failed(self, e: Exception) -> None:
        self.on_failed(e, "An error occurred during merging:")
        self.animation.stop("Merge PDFs")
        self.merge_btn.config(state="normal")

    def move_up(self) -> None:
        selected_index = self.file_list.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if index > 0:
            self.selected_files[index], self.selected_files[index - 1] = (
                self.selected_files[index - 1],
                self.selected_files[index],
            )
            self.update_file_list()
            self.file_list.select_set(index - 1)

    def move_down(self) -> None:
        selected_index = self.file_list.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if index < len(self.selected_files) - 1:
            self.selected_files[index], self.selected_files[index + 1] = (
                self.selected_files[index + 1],
                self.selected_files[index],
            )
            self.update_file_list()
            self.file_list.select_set(index + 1)

    def delete_selected_file(self) -> None:
        selected_index = self.file_list.curselection()
        if not selected_index:
            tk.messagebox.showwarning("Warning", "No PDF selected to delete.")
            return
        index = selected_index[0]
        self.selected_files.pop(index)
        self.update_file_list()

    def delete_all_files(self) -> None:
        if not self.selected_files:
            tk.messagebox.showwarning("Warning", "No PDFs to delete.")
            return
        if tk.messagebox.askyesno(
            "Delete All", "Are you sure you want to delete all selected PDFs?"
        ):
            self.selected_files.clear()
            self.update_file_list()
