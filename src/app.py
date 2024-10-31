import os
import sys
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfMerger
import subprocess


def get_version():
    try:
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        version_path = os.path.join(base_path, "..", "VERSION")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


__version__ = get_version()


def merge_pdfs(file_paths, output_path):
    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()


def main():
    print(f"PDF Merger version {__version__}")
    root = tk.Tk()
    root.title("PDF Merger")
    root.geometry("900x600")
    root.resizable(True, True)

    # Set up ttk style with custom theme colors
    style = ttk.Style()
    style.theme_use("clam")

    # Colors
    root.configure(bg="#282C34")
    style.configure("TFrame", background="#282C34")
    style.configure("TButton", font=("Helvetica", 10, "bold"), padding=5)
    style.configure(
        "TLabel", background="#282C34", foreground="white", font=("Helvetica", 10)
    )
    style.map(
        "TButton",
        background=[("active", "#61AFEF"), ("!active", "#98C379")],
        foreground=[("!disabled", "black")],
    )

    selected_files = []
    output_file = ""

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
        for idx, file in enumerate(selected_files):
            file_list.insert(tk.END, f"{idx + 1}. {os.path.basename(file)}")

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

        # Perform merging after a short delay to allow animation to start
        root.after(100, perform_merge)

    def perform_merge():
        try:
            merge_pdfs(selected_files, output_file)
            messagebox.showinfo(
                "Success", f"PDFs have been merged into:\n{output_file}"
            )
            ask_to_open_or_close()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            stop_loading_animation()

    def start_loading_animation():
        merge_btn_text.set("Merging.")
        animate_loading()

    def animate_loading():
        current_text = merge_btn_text.get()
        if current_text.endswith("..."):
            merge_btn_text.set("Merging.")
        else:
            merge_btn_text.set(current_text + ".")
        root.after(500, animate_loading)  # Repeat animation every 500 ms

    def stop_loading_animation():
        merge_btn_text.set("Merge PDFs")
        merge_btn.config(state="normal")

    def ask_to_open_or_close():
        response = messagebox.askquestion(
            "Open or Close",
            "Do you want to open the merged PDF file?",
        )
        if response == "yes":
            open_file(output_file)
        root.quit()  # Close the application

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
    frame = ttk.Frame(root, padding=10)
    frame.pack(expand=True, fill=tk.BOTH)

    # Make rows and columns in the frame resizable
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    # Add PDF button
    file_btn = ttk.Button(frame, text="Add PDFs", command=select_file, width=20)
    file_btn.grid(row=0, column=0, pady=5, sticky="w")

    # Select Output button
    output_btn = ttk.Button(
        frame, text="Select Output File", command=select_output_file, width=20
    )
    output_btn.grid(row=1, column=0, pady=5, sticky="w")

    # Output path label
    output_label = ttk.Label(frame, text="No output file selected")
    output_label.grid(row=1, column=1, padx=5, sticky="w")

    # Selected PDFs label
    file_list_label = ttk.Label(frame, text="Selected PDFs:")
    file_list_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

    # Listbox with updated colors
    file_list = tk.Listbox(
        frame,
        selectmode=tk.SINGLE,
        bg="#3E4451",
        fg="white",
        font=("Helvetica", 12),
        highlightbackground="#98C379",
        selectbackground="#61AFEF",
        selectforeground="black",
    )
    file_list.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    # Move Up and Move Down buttons
    move_up_btn = ttk.Button(frame, text="Move ↑", command=move_up, width=20)
    move_up_btn.grid(row=3, column=2, padx=5, pady=(5, 0), sticky="n")

    move_down_btn = ttk.Button(frame, text="Move ↓", command=move_down, width=20)
    move_down_btn.grid(row=3, column=2, padx=5, pady=(50, 5), sticky="n")

    # Delete PDF button
    delete_btn = ttk.Button(
        frame, text="Delete pdf", command=delete_selected_file, width=20
    )
    delete_btn.grid(row=3, column=2, padx=5, pady=(100, 5), sticky="n")

    # Merge PDFs button with animation
    merge_btn_text = tk.StringVar(value="Merge PDFs")
    merge_btn = ttk.Button(frame, textvariable=merge_btn_text, command=merge, width=20)
    merge_btn.grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
