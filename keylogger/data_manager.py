"""
Data manager module for keylogger
Handles saving and loading data with severity level support
"""

import os
import datetime

class DataManager:
    def __init__(self):
        """Initialize the data manager"""
        # Default save directory
        self.save_dir = os.path.join(os.path.expanduser("~"), "Documents")
        
    def save_log(self, keys, file_path=None):
        """
        Save the keylog to a file
        
        Args:
            keys: List of captured keys
            file_path: Path to save the file (optional)
            
        Returns:
            tuple: (success, message)
        """
        if not keys:
            return (False, "No data to save")
            
        if not file_path:
            # Generate default file path
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.save_dir, f"keylog_{timestamp}.txt")
            
        try:
            with open(file_path, "w") as f:
                f.write("".join(keys))
            return (True, f"Log saved to {file_path}")
        except Exception as e:
            return (False, f"Could not save file: {e}")
            
    def save_flags(self, flags, file_path=None):
        """
        Save the flagged commands to a file with severity information
        
        Args:
            flags: List of flagged commands
            file_path: Path to save the file (optional)
            
        Returns:
            tuple: (success, message)
        """
        if not flags:
            return (False, "No flags to save")
            
        if not file_path:
            # Generate default file path
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.save_dir, f"flagged_commands_{timestamp}.txt")
            
        try:
            with open(file_path, "w") as f:
                # Write header
                f.write("FLAGGED COMMANDS REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                # Calculate severity statistics
                severity_stats = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
                for flag in flags:
                    severity_stats[flag["severity"]] += 1
                
                # Write summary
                f.write("SEVERITY SUMMARY:\n")
                f.write("-" * 20 + "\n")
                for severity, count in severity_stats.items():
                    f.write(f"{severity}: {count} commands\n")
                f.write("\n" + "=" * 50 + "\n\n")
                
                # Write flagged commands grouped by severity
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    severity_flags = [flag for flag in flags if flag["severity"] == severity]
                    if severity_flags:
                        f.write(f"\n{severity} SEVERITY COMMANDS ({len(severity_flags)} total):\n")
                        f.write("-" * 50 + "\n")
                        
                        for flag in severity_flags:
                            f.write(f"Timestamp: {flag['timestamp']}\n")
                            f.write(f"Window: {flag['window_title']}\n")
                            f.write(f"Command: {flag['command']}\n")
                            f.write(f"Description: {flag['description']}\n")
                            f.write(f"Severity Description: {flag['severity_description']}\n")
                            f.write("-" * 30 + "\n")
                
            return (True, f"Flags saved to {file_path}")
        except Exception as e:
            return (False, f"Could not save file: {e}")
            
    def set_save_directory(self, directory):
        """Set the default save directory"""
        if os.path.isdir(directory):
            self.save_dir = directory
            return True
        return False