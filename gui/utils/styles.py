"""
Styles and theme definitions for the keylogger GUI
"""

# Color scheme
COLORS = {
    "primary": "#2c3e50",      # Dark blue-gray
    "secondary": "#3498db",    # Blue
    "accent": "#e74c3c",       # Red
    "success": "#2ecc71",      # Green
    "warning": "#f39c12",      # Orange
    "light": "#ecf0f1",        # Light gray
    "dark": "#34495e",         # Darker blue-gray
    "bg_light": "#f5f5f5",     # Very light gray
    "bg_dark": "#2c3e50",      # Dark blue-gray
    "text_light": "#ecf0f1",   # Light gray for text
    "text_dark": "#2c3e50",    # Dark blue-gray for text
    "highlight": "#ffff99",    # Yellow highlight
}

# Font definitions
FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 14, "bold"),
    "heading": ("Segoe UI", 12, "bold"),
    "normal": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "monospace": ("Consolas", 10),
    "monospace_small": ("Consolas", 9),
}

# Button styles
BUTTON_STYLES = {
    "primary": {
        "bg": COLORS["primary"],
        "fg": COLORS["text_light"],
        "activebackground": COLORS["dark"],
        "activeforeground": COLORS["text_light"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
    },
    "secondary": {
        "bg": COLORS["secondary"],
        "fg": COLORS["text_light"],
        "activebackground": "#2980b9",  # Darker blue
        "activeforeground": COLORS["text_light"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
    },
    "success": {
        "bg": COLORS["success"],
        "fg": COLORS["text_light"],
        "activebackground": "#27ae60",  # Darker green
        "activeforeground": COLORS["text_light"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
    },
    "danger": {
        "bg": COLORS["accent"],
        "fg": COLORS["text_light"],
        "activebackground": "#c0392b",  # Darker red
        "activeforeground": COLORS["text_light"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
    },
    "warning": {
        "bg": COLORS["warning"],
        "fg": COLORS["text_dark"],
        "activebackground": "#e67e22",  # Darker orange
        "activeforeground": COLORS["text_dark"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 10,
        "pady": 5,
    },
    "tab": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["text_dark"],
        "activebackground": COLORS["secondary"],
        "activeforeground": COLORS["text_light"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
    },
    "tab_active": {
        "bg": COLORS["secondary"],
        "fg": COLORS["text_light"],
        "activebackground": COLORS["secondary"],
        "activeforeground": COLORS["text_light"],
        "font": FONTS["normal"],
        "borderwidth": 0,
        "padx": 15,
        "pady": 8,
    },
}

# Frame styles
FRAME_STYLES = {
    "main": {
        "bg": COLORS["bg_light"],
        "padx": 10,
        "pady": 10,
    },
    "content": {
        "bg": COLORS["bg_light"],
        "padx": 5,
        "pady": 5,
        "borderwidth": 1,
        "relief": "solid",
    },
    "header": {
        "bg": COLORS["primary"],
        "padx": 10,
        "pady": 5,
    },
    "footer": {
        "bg": COLORS["bg_light"],
        "padx": 10,
        "pady": 5,
    },
}

# Text styles for scrolledtext widgets
TEXT_STYLES = {
    "log": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["text_dark"],
        "font": FONTS["monospace"],
        "padx": 5,
        "pady": 5,
        "relief": "solid",
        "borderwidth": 1,
    },
    "flags": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["text_dark"],
        "font": FONTS["monospace"],
        "padx": 5,
        "pady": 5,
        "relief": "solid",
        "borderwidth": 1,
    },
}

# Label styles
LABEL_STYLES = {
    "title": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["primary"],
        "font": FONTS["title"],
        "pady": 5,
    },
    "subtitle": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["primary"],
        "font": FONTS["subtitle"],
        "pady": 3,
    },
    "heading": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["dark"],
        "font": FONTS["heading"],
        "pady": 2,
    },
    "normal": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["text_dark"],
        "font": FONTS["normal"],
    },
    "status": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["text_dark"],
        "font": FONTS["normal"],
        "pady": 3,
    },
    "status_active": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["success"],
        "font": FONTS["normal"],
        "pady": 3,
    },
    "status_inactive": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["accent"],
        "font": FONTS["normal"],
        "pady": 3,
    },
    "header": {
        "bg": COLORS["primary"],
        "fg": COLORS["text_light"],
        "font": FONTS["heading"],
        "pady": 5,
    },
    "footer": {
        "bg": COLORS["bg_light"],
        "fg": COLORS["text_dark"],
        "font": FONTS["small"],
    },
}

def apply_styles():
    """
    Function to apply global styles to tkinter widgets.
    Can be expanded for more sophisticated styling in the future.
    """
    pass