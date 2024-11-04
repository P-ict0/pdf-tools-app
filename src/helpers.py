import os
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Optional


def go_back(current_window: tk.Toplevel, root_window: Optional[tk.Tk]) -> None:
    """
    Close the current window and show the root window if it exists.

    :param current_window: The window to close.
    :param root_window: The main application window to show.
    """
    current_window.destroy()
    if root_window:
        root_window.deiconify()


def select_files(multiple: bool, title: str, filetypes: List[tuple]) -> List[str]:
    """
    Open a file dialog to select one or multiple files.

    :param multiple: Whether to allow multiple file selections.
    :param title: The title of the file dialog.
    :param filetypes: A list of tuples specifying the file types.
    :return: A list of selected file paths.
    """
    if multiple:
        return list(filedialog.askopenfilenames(title=title, filetypes=filetypes))
    else:
        file = filedialog.askopenfilename(title=title, filetypes=filetypes)
        return [file] if file else []


def select_output_file(
    title: str, defaultextension: str = ".pdf", filetypes=None
) -> str:
    """
    Open a save as dialog to select the output file path.

    :param title: The title of the save dialog.
    :param defaultextension: The default file extension.
    :param filetypes: A list of tuples specifying the file types.
    :return: The selected output file path.
    """
    if filetypes is None:
        filetypes = [("PDF Files", "*.pdf")]
    if not filetypes:
        filetypes = [("PDF Files", "*.pdf")]

    return filedialog.asksaveasfilename(
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes,
    )


def on_failed(e: Exception, message: str = "An error occurred:") -> None:
    """
    Display an error message to the user.

    :param e: The exception that was raised.
    :param message: The custom message to display.
    """
    messagebox.showerror("Error", f"{message}\n{e}")


class Animation:
    """
    A class to handle loading animations for buttons.
    """

    def __init__(
        self, window: tk.Tk, text_var: tk.StringVar, base_text: str, interval: int = 500
    ):
        """
        Initialize the Animation.

        :param window: The Tkinter window instance.
        :param text_var: The StringVar associated with the button text.
        :param base_text: The base text to display on the button.
        :param interval: Time interval for the animation in milliseconds.
        """
        self.window = window
        self.text_var = text_var
        self.base_text = base_text
        self.interval = interval
        self.is_animating = False

    def animate_loading(self) -> None:
        """
        Update the button text to show a loading animation.
        """
        if not self.is_animating:
            return

        current_text = self.text_var.get()
        if current_text.endswith("..."):
            self.text_var.set(f"{self.base_text}.")
        else:
            self.text_var.set(current_text + ".")

        self.window.after(self.interval, self.animate_loading)

    def start(self) -> None:
        """
        Start the loading animation.
        """
        self.is_animating = True
        self.text_var.set(f"{self.base_text}.")
        self.animate_loading()

    def stop(self, reset_text: str) -> None:
        """
        Stop the loading animation and reset the button text.

        :param reset_text: The text to reset the button to.
        """
        self.is_animating = False
        self.text_var.set(reset_text)


def ask_to_open_or_close(title: str, message: str, file_path: str) -> None:
    """
    Prompt the user to open the file or not.

    :param title: The title of the prompt.
    :param message: The message to display.
    :param file_path: The path of the file to open if the user agrees.
    """
    response = messagebox.askquestion(title, message)
    if response == "yes":
        open_file(file_path)


def open_file(filepath: str) -> None:
    """
    Open a file using the default application based on the operating system.

    :param filepath: The path to the file to open.
    """
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", filepath])
        else:  # Linux and other OSes
            subprocess.call(["xdg-open", filepath])
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open file:\n{e}")
