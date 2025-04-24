"""
Advanced Keylogger with Command Line Detection
Main entry point for the application
"""

import tkinter as tk
from gui.app import KeyloggerApp

def main():
    """Initialize and run the keylogger application"""
    root = tk.Tk()
    app = KeyloggerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    