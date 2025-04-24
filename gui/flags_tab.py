"""
Flags tab for the keylogger application
Displays flagged command line activity with severity levels
"""

import tkinter as tk
from tkinter import scrolledtext
from gui.utils.styles import COLORS, BUTTON_STYLES, FRAME_STYLES, LABEL_STYLES, TEXT_STYLES

class FlagsTab:
    def __init__(self, parent, app):
        """
        Initialize the flags tab
        
        Args:
            parent: Parent frame
            app: Main application instance
        """
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=COLORS["bg_light"])
        self.flag_count = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the tab widgets"""
        # Title
        title_label = tk.Label(self.frame, text="Command Line Monitoring", **LABEL_STYLES["title"])
        title_label.pack(pady=10)
        
        # Top controls section
        controls_section = tk.Frame(self.frame, bg=COLORS["bg_light"])
        controls_section.pack(fill=tk.X, pady=5)
        
        # Left side - Flag controls
        flag_controls_frame = tk.LabelFrame(controls_section, text="Flag Controls", 
                                         bg=COLORS["bg_light"], fg=COLORS["primary"])
        flag_controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        controls_frame = tk.Frame(flag_controls_frame, bg=COLORS["bg_light"])
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Clear flags button
        self.clear_flags_button = tk.Button(controls_frame, text="Clear Flags", 
                                          command=self.app.clear_flags,
                                          **BUTTON_STYLES["danger"])
        self.clear_flags_button.pack(side=tk.LEFT, padx=5)
        
        # Save flags button
        self.save_flags_button = tk.Button(controls_frame, text="Save Flags", 
                                         command=self.app.save_flags,
                                         **BUTTON_STYLES["secondary"])
        self.save_flags_button.pack(side=tk.LEFT, padx=5)
        
        # Right side - Status information
        status_frame = tk.LabelFrame(controls_section, text="Flag Statistics", 
                                   bg=COLORS["bg_light"], fg=COLORS["primary"])
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        status_inner_frame = tk.Frame(status_frame, bg=COLORS["bg_light"])
        status_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Severity counters
        self.severity_labels = {}
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            severity_frame = tk.Frame(status_inner_frame, bg=COLORS["bg_light"])
            severity_frame.pack(side=tk.LEFT, padx=10)
            
            severity_label = tk.Label(severity_frame, text=f"{severity}:", 
                                    bg=COLORS["bg_light"], font=("Helvetica", 9, "bold"))
            severity_label.pack(side=tk.LEFT)
            
            count_label = tk.Label(severity_frame, text="0", 
                                 bg=COLORS["bg_light"], font=("Helvetica", 9))
            count_label.pack(side=tk.LEFT, padx=5)
            
            self.severity_labels[severity] = count_label
        
        # Flag counter
        self.flag_counter = tk.Label(status_inner_frame, text="Total Flags: 0", 
                                   **LABEL_STYLES["heading"])
        self.flag_counter.pack(side=tk.RIGHT, padx=10)
        
        # Severity legend
        legend_frame = tk.LabelFrame(self.frame, text="Severity Legend", 
                                   bg=COLORS["bg_light"], fg=COLORS["primary"])
        legend_frame.pack(fill=tk.X, padx=10, pady=5)
        
        legend_inner = tk.Frame(legend_frame, bg=COLORS["bg_light"])
        legend_inner.pack(fill=tk.X, padx=10, pady=10)
        
        severity_data = {
            "CRITICAL": {"color": "#dc3545", "description": "Extremely dangerous - System/Security modification"},
            "HIGH": {"color": "#fd7e14", "description": "High risk - System information exposure"},
            "MEDIUM": {"color": "#ffc107", "description": "Moderate risk - File/Network operations"},
            "LOW": {"color": "#28a745", "description": "Low risk - Information gathering"}
        }
        
        for severity, info in severity_data.items():
            legend_item = tk.Frame(legend_inner, bg=COLORS["bg_light"])
            legend_item.pack(fill=tk.X, pady=2)
            
            color_box = tk.Label(legend_item, text="  ", bg=info["color"], width=3)
            color_box.pack(side=tk.LEFT, padx=5)
            
            severity_text = tk.Label(legend_item, text=f"{severity}: {info['description']}", 
                                   bg=COLORS["bg_light"], font=("Helvetica", 9))
            severity_text.pack(side=tk.LEFT)
        
        # Flags section
        flags_section = tk.LabelFrame(self.frame, text="Flagged Command Activity", 
                                    bg=COLORS["bg_light"], fg=COLORS["primary"])
        flags_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Flags display
        self.flags_display = scrolledtext.ScrolledText(flags_section, wrap=tk.WORD, **TEXT_STYLES["flags"])
        self.flags_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.flags_display.config(state=tk.DISABLED)
        
        # Configure tags for highlighting
        self.flags_display.tag_configure("timestamp", foreground=COLORS["secondary"])
        self.flags_display.tag_configure("command", foreground=COLORS["accent"], font=("Consolas", 10, "bold"))
        self.flags_display.tag_configure("window", foreground=COLORS["dark"])
        self.flags_display.tag_configure("critical_tag", background="#dc3545", foreground="white")
        self.flags_display.tag_configure("high_tag", background="#fd7e14", foreground="white")
        self.flags_display.tag_configure("medium_tag", background="#ffc107", foreground="black")
        self.flags_display.tag_configure("low_tag", background="#28a745", foreground="white")
        self.flags_display.tag_configure("description", foreground=COLORS["text_dark"], font=("Helvetica", 9, "italic"))
        
    def show(self):
        """Show the tab"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide the tab"""
        self.frame.pack_forget()
        
    def add_flag(self, flag):
        """
        Add a flagged command to the display
        
        Args:
            flag: Flag information dictionary
        """
        # Create display text with timestamps and highlighting
        timestamp_text = f"[{flag['timestamp']}] "
        severity_text = f"[{flag['severity']}] "
        window_text = f"FLAGGED COMMAND in {flag['window_title']}:\n"
        command_text = f"    {flag['command']}\n"
        description_text = f"    Description: {flag['description']}\n\n"
        
        # Add to display with tags for styling
        self.flags_display.config(state=tk.NORMAL)
        
        # Insert timestamp
        self.flags_display.insert(tk.END, timestamp_text, "timestamp")
        
        # Insert severity with appropriate tag
        severity_tag = f"{flag['severity'].lower()}_tag"
        self.flags_display.insert(tk.END, severity_text, severity_tag)
        
        # Insert window information
        self.flags_display.insert(tk.END, window_text, "window")
        
        # Insert command
        self.flags_display.insert(tk.END, command_text, "command")
        
        # Insert description
        self.flags_display.insert(tk.END, description_text, "description")
        
        # Scroll to see the new entry
        self.flags_display.see(tk.END)
        self.flags_display.config(state=tk.DISABLED)
        
        # Update counters
        self.flag_count += 1
        self.flag_counter.config(text=f"Total Flags: {self.flag_count}")
        
        # Update severity counters
        if self.app.command_detector:
            stats = self.app.command_detector.get_severity_stats()
            for severity, count in stats.items():
                self.severity_labels[severity].config(text=str(count))
        
    def clear_flags(self):
        """Clear the flagged commands display"""
        self.flags_display.config(state=tk.NORMAL)
        self.flags_display.delete(1.0, tk.END)
        self.flags_display.config(state=tk.DISABLED)
        
        self.flag_count = 0
        self.flag_counter.config(text="Total Flags: 0")
        
        # Reset severity counters
        for label in self.severity_labels.values():
            label.config(text="0")