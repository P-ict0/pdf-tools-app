# Colors (Nord Theme)
BG_COLOR = "#2E3440"
FG_COLOR = "#D8DEE9"
BUTTON_BG = "#4C566A"
BUTTON_FG = "#ECEFF4"
HIGHLIGHT_COLOR = "#88C0D0"
ACTIVE_BG = "#5E81AC"

# Fonts
FONT_DEFAULT = ("Helvetica", 12)
FONT_BOLD = ("Helvetica", 12, "bold")
FONT_LARGE_BOLD = ("Helvetica", 16, "bold")
FONT_XLARGE_BOLD = ("Helvetica", 18, "bold")


def set_theme(style):
    style.theme_use("clam")
    style.configure("TFrame", background=BG_COLOR)
    style.configure(
        "TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT_DEFAULT
    )
    style.configure(
        "TButton",
        background=BUTTON_BG,
        foreground=BUTTON_FG,
        font=FONT_BOLD,
        borderwidth=0,
    )
    style.map("TButton", background=[("active", ACTIVE_BG)])
    # Large button style
    style.configure("Large.TButton", font=FONT_LARGE_BOLD, padding=10)
