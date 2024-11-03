import os
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfMerger
import subprocess


def merge_pdfs(file_paths, output_path):
    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def pdf_merger_main(root_window=None):
    def go_back():
        # Close the current window and show the main window
        merger_window.destroy()
        if root_window:
            root_window.deiconify()

    # Create a new window for the PDF Merger
    merger_window = tk.Toplevel()
    merger_window.title("PDF Merger")
    merger_window.geometry("900x600")
    merger_window.resizable(True, True)

    # Set up modern style
    style = ttk.Style()
    style.theme_use("clam")

    # Colors (Nord Theme)
    bg_color = "#2E3440"
    fg_color = "#D8DEE9"
    button_bg = "#4C566A"
    button_fg = "#ECEFF4"
    highlight_color = "#88C0D0"
    active_bg = "#5E81AC"

    merger_window.configure(bg=bg_color)
    style.configure("TFrame", background=bg_color)
    style.configure(
        "TButton",
        background=button_bg,
        foreground=button_fg,
        font=("Helvetica", 12),
        borderwidth=0,
        focusthickness=0,
        focuscolor=bg_color,
    )
    style.map("TButton", background=[("active", active_bg)])

    style.configure(
        "TLabel",
        background=bg_color,
        foreground=fg_color,
        font=("Helvetica", 12),
    )

    selected_files = []
    output_file = ""
    is_animating = False  # For loading animation control

    # Functions
    def select_file():
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")],
        )
        for file in files:
            if file not in selected_files:
                selected_files.append(file)
        update_file_list()

    def update_file_list():
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

    def select_output_file():
        nonlocal output_file
        file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Select Output File",
        )
        output_file = file
        output_label.config(text=output_file or "No output file selected")

    def merge():
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

    def perform_merge():
        try:
            merge_pdfs(selected_files, output_file)
            merged_size = os.path.getsize(output_file)
            merged_size_mb = merged_size / (1024 * 1024)
            # Schedule the messagebox and other GUI updates in the main thread
            merger_window.after(0, merge_completed, merged_size_mb)
        except Exception as e:
            # Schedule the error message in the main thread
            merger_window.after(0, merge_failed, e)

    def merge_completed(merged_size_mb):
        messagebox.showinfo(
            "Success",
            f"PDFs have been merged into:\n{output_file}\nTotal size: {merged_size_mb:.2f} MB",
        )
        stop_loading_animation()
        ask_to_open_or_close()

    def merge_failed(e):
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        stop_loading_animation()

    def start_loading_animation():
        nonlocal is_animating
        is_animating = True
        merge_btn_text.set("Merging.")
        animate_loading()

    def animate_loading():
        if not is_animating:
            return
        current_text = merge_btn_text.get()
        if current_text.endswith("..."):
            merge_btn_text.set("Merging.")
        else:
            merge_btn_text.set(current_text + ".")
        merger_window.after(500, animate_loading)  # Repeat animation every 500 ms

    def stop_loading_animation():
        nonlocal is_animating
        is_animating = False
        merge_btn_text.set("Merge PDFs")
        merge_btn.config(state="normal")

    def ask_to_open_or_close():
        response = messagebox.askquestion(
            "Open Merged PDF",
            "Do you want to open the merged PDF file?",
        )
        if response == "yes":
            open_file(output_file)
        # Do not quit the application here; allow the user to continue using it if needed

    def open_file(filepath):
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux
            subprocess.call(["xdg-open", filepath])

    def move_up():
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

    def move_down():
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

    def delete_selected_file():
        selected_index = file_list.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "No PDF selected to delete.")
            return
        index = selected_index[0]
        selected_files.pop(index)  # Remove from list
        update_file_list()  # Refresh Listbox

    # GUI Layout
    frame = ttk.Frame(merger_window, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Add a Back button to return to the main menu
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
        bg=button_bg,
        fg=fg_color,
        font=("Helvetica", 12),
        highlightbackground=highlight_color,
        selectbackground=highlight_color,
        selectforeground=bg_color,
    )
    file_list.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    # Total size label
    total_size_label = ttk.Label(frame, text="Total size: 0.00 MB")
    total_size_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)

    # Move Up and Move Down buttons
    move_up_btn = ttk.Button(frame, text="Move ↑", command=move_up, width=20)
    move_up_btn.grid(row=4, column=2, padx=5, pady=(5, 0), sticky="n")

    move_down_btn = ttk.Button(frame, text="Move ↓", command=move_down, width=20)
    move_down_btn.grid(row=4, column=2, padx=5, pady=(50, 5), sticky="n")

    # Delete PDF button
    delete_btn = ttk.Button(
        frame, text="Delete PDF", command=delete_selected_file, width=20
    )
    delete_btn.grid(row=4, column=2, padx=5, pady=(100, 5), sticky="n")

    # Merge PDFs button
    merge_btn_text = tk.StringVar(value="Merge PDFs")
    merge_btn = ttk.Button(
        frame,
        textvariable=merge_btn_text,
        command=merge,
        width=20,
    )
    merge_btn.grid(row=6, column=0, columnspan=2, pady=10)

    merger_window.mainloop()


if __name__ == "__main__":
    pdf_merger_main()
