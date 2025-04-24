"""
Monitor tab for the keylogger application
Displays the keylogger output
"""

import tkinter as tk
from tkinter import scrolledtext
from gui.utils.styles import COLORS, BUTTON_STYLES, FRAME_STYLES, LABEL_STYLES, TEXT_STYLES

class MonitorTab:
    def __init__(self, parent, app):
        """
        Initialize the monitor tab
        
        Args:
            parent: Parent frame
            app: Main application instance
        """
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=COLORS["bg_light"])
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the tab widgets"""
        # Title
        title_label = tk.Label(self.frame, text="Keystroke Monitoring", **LABEL_STYLES["title"])
        title_label.pack(pady=10)
        
        # Top controls section
        controls_section = tk.Frame(self.frame, bg=COLORS["bg_light"])
        controls_section.pack(fill=tk.X, pady=5)
        
        # Left side - Monitoring controls
        monitoring_frame = tk.LabelFrame(controls_section, text="Monitoring Controls", 
                                      bg=COLORS["bg_light"], fg=COLORS["primary"])
        monitoring_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        controls_frame = tk.Frame(monitoring_frame, bg=COLORS["bg_light"])
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start/Stop button
        self.toggle_button = tk.Button(controls_frame, text="Start Monitoring", 
                                      command=self.app.toggle_logging, 
                                      **BUTTON_STYLES["success"])
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        self.save_button = tk.Button(controls_frame, text="Save Log", 
                                    command=self.app.save_log,
                                    **BUTTON_STYLES["secondary"])
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.save_button.config(state=tk.DISABLED)
        
        # Clear button
        self.clear_button = tk.Button(controls_frame, text="Clear Log", 
                                     command=self.app.clear_log,
                                     **BUTTON_STYLES["danger"])
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Right side - Status information
        status_frame = tk.LabelFrame(controls_section, text="Status Information", 
                                   bg=COLORS["bg_light"], fg=COLORS["primary"])
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        status_inner_frame = tk.Frame(status_frame, bg=COLORS["bg_light"])
        status_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Status labels
        self.status_label = tk.Label(status_inner_frame, text="Status: Idle", 
                                   **LABEL_STYLES["status_inactive"])
        self.status_label.pack(fill=tk.X, pady=2)
        
        self.window_label = tk.Label(status_inner_frame, text="Current Window: None", 
                                   **LABEL_STYLES["normal"])
        self.window_label.pack(fill=tk.X, pady=2)
        
        # Log section
        log_section = tk.LabelFrame(self.frame, text="Keystroke Log", 
                                  bg=COLORS["bg_light"], fg=COLORS["primary"])
        log_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(log_section, wrap=tk.WORD, **TEXT_STYLES["log"])
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_display.config(state=tk.DISABLED)
        
        # Footer with information
        footer_frame = tk.Frame(self.frame, bg=COLORS["bg_light"])
        footer_frame.pack(fill=tk.X, pady=5)
        
        footer_text = tk.Label(footer_frame, 
                             text="For educational and authorized monitoring purposes only.",
                             **LABEL_STYLES["footer"])
        footer_text.pack(side=tk.LEFT, padx=5)
        
    def show(self):
        """Show the tab"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide the tab"""
        self.frame.pack_forget()
        
    def update_status(self, active):
        """
        Update the monitoring status
        
        Args:
            active: True if monitoring is active, False otherwise
        """
        if active:
            self.toggle_button.configure(text="Stop Monitoring", **BUTTON_STYLES["danger"])
            self.status_label.configure(text="Status: Monitoring Active", **LABEL_STYLES["status_active"])
            self.save_button.config(state=tk.NORMAL)
        else:
            self.toggle_button.configure(text="Start Monitoring", **BUTTON_STYLES["success"])
            self.status_label.configure(text="Status: Monitoring Stopped", **LABEL_STYLES["status_inactive"])
            
    def update_window_info(self, title, process):
        """
        Update the current window information
        
        Args:
            title: Window title
            process: Process name
        """
        display_title = title if len(title) < 40 else title[:37] + "..."
        self.window_label.config(text=f"Current Window: {display_title} ({process})")
        
    def update_display(self, keys):
        """
        Update the log display
        
        Args:
            keys: List of captured keys
        """
        if not keys:
            self.log_display.config(state=tk.NORMAL)
            self.log_display.delete(1.0, tk.END)
            self.log_display.config(state=tk.DISABLED)
            return
            
        self.log_display.config(state=tk.NORMAL)
        self.log_display.delete(1.0, tk.END)
        self.log_display.insert(tk.END, "".join(keys))
        self.log_display.see(tk.END)  # Scroll to the end
        self.log_display.config(state=tk.DISABLED)