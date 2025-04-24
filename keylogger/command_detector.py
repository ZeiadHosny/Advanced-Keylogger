"""
Command detector module for keylogger
Detects command line interfaces and flags suspicious commands with severity levels
"""

import re
import datetime

class CommandDetector:
    def __init__(self):
        """Initialize the command detector with patterns for commands and terminals"""
        # Patterns to identify command-line interfaces by process name
        self.command_patterns = [
            r"cmd\.exe",               # Command Prompt
            r"powershell\.exe",         # PowerShell
            r"WindowsTerminal\.exe",    # Windows Terminal
            r"bash\.exe",              # Git Bash
            r"wsl\.exe"                # Windows Subsystem for Linux
        ]
        
        # Keywords in window titles that indicate command-line interfaces
        self.cmd_window_keywords = [
            "Command Prompt", 
            "Windows PowerShell", 
            "Windows Terminal", 
            "Git Bash", 
            "WSL", 
            "Terminal",
            "cmd",
            "powershell"
        ]
        
        # Severity levels
        self.SEVERITY_LEVELS = {
            "CRITICAL": {"color": "#dc3545", "description": "Extremely dangerous - System/Security modification"},
            "HIGH": {"color": "#fd7e14", "description": "High risk - System information exposure"},
            "MEDIUM": {"color": "#ffc107", "description": "Moderate risk - File/Network operations"},
            "LOW": {"color": "#28a745", "description": "Low risk - Information gathering"}
        }
        
        # Patterns for potentially suspicious commands to flag with severity levels
        self.flagged_commands = {
            # CRITICAL severity
            r"net\s+user\s+\w+\s+\*": {"pattern": r"net\s+user\s+\w+\s+\*", "severity": "CRITICAL", "description": "Password change attempt"},
            r"net\s+user\s+\w+\s+/add": {"pattern": r"net\s+user\s+\w+\s+/add", "severity": "CRITICAL", "description": "User account creation"},
            r"net\s+localgroup\s+administrators": {"pattern": r"net\s+localgroup\s+administrators", "severity": "CRITICAL", "description": "Administrator group modification"},
            r"reg\s+add": {"pattern": r"reg\s+add", "severity": "CRITICAL", "description": "Registry modification - adding keys"},
            r"reg\s+delete": {"pattern": r"reg\s+delete", "severity": "CRITICAL", "description": "Registry modification - deleting keys"},
            r"format\s+": {"pattern": r"format\s+", "severity": "CRITICAL", "description": "Disk formatting attempt"},
            r"cipher\s+/w": {"pattern": r"cipher\s+/w", "severity": "CRITICAL", "description": "Secure file deletion"},
            r"powershell\s+-e": {"pattern": r"powershell\s+-e", "severity": "CRITICAL", "description": "Encoded PowerShell command (often malicious)"},
            r"powershell.*-ExecutionPolicy\s+Bypass": {"pattern": r"powershell.*-ExecutionPolicy\s+Bypass", "severity": "CRITICAL", "description": "PowerShell security bypass"},
            
            # HIGH severity
            r"taskkill": {"pattern": r"taskkill", "severity": "HIGH", "description": "Process termination"},
            r"shutdown": {"pattern": r"shutdown", "severity": "HIGH", "description": "System shutdown/restart"},
            r"sc\s+stop": {"pattern": r"sc\s+stop", "severity": "HIGH", "description": "Service stopping"},
            r"sc\s+delete": {"pattern": r"sc\s+delete", "severity": "HIGH", "description": "Service deletion"},
            r"runas": {"pattern": r"runas", "severity": "HIGH", "description": "Running as different user"},
            r"net\s+user": {"pattern": r"net\s+user", "severity": "HIGH", "description": "User account management"},
            r"schtasks.*\/create": {"pattern": r"schtasks.*\/create", "severity": "HIGH", "description": "Creating scheduled task"},
            r"reg\s+query.*sam": {"pattern": r"reg\s+query.*sam", "severity": "HIGH", "description": "SAM database query"},
            r"net\s+share": {"pattern": r"net\s+share", "severity": "HIGH", "description": "Network share manipulation"},
            
            # MEDIUM severity
            r"rmdir|del|rm\s+": {"pattern": r"rmdir|del|rm\s+", "severity": "MEDIUM", "description": "File/directory deletion"},
            r"copy|xcopy|robocopy": {"pattern": r"copy|xcopy|robocopy", "severity": "MEDIUM", "description": "File copying operations"},
            r"netstat\s+-an": {"pattern": r"netstat\s+-an", "severity": "MEDIUM", "description": "Active connections listing"},
            r"attrib\s+": {"pattern": r"attrib\s+", "severity": "MEDIUM", "description": "File attribute modification"},
            r"ftp\s+": {"pattern": r"ftp\s+", "severity": "MEDIUM", "description": "FTP connection"},
            r"telnet\s+": {"pattern": r"telnet\s+", "severity": "MEDIUM", "description": "Telnet connection"},
            r"curl\s+|wget\s+|Invoke-WebRequest": {"pattern": r"curl\s+|wget\s+|Invoke-WebRequest", "severity": "MEDIUM", "description": "Web request/download"},
            
            # LOW severity
            r"ipconfig": {"pattern": r"ipconfig", "severity": "LOW", "description": "Network configuration display"},
            r"systeminfo": {"pattern": r"systeminfo", "severity": "LOW", "description": "System information display"},
            r"tasklist": {"pattern": r"tasklist", "severity": "LOW", "description": "Process listing"},
            r"whoami": {"pattern": r"whoami", "severity": "LOW", "description": "Current user information"},
            r"ping\s+": {"pattern": r"ping\s+", "severity": "LOW", "description": "Network connectivity test"},
            r"tracert": {"pattern": r"tracert", "severity": "LOW", "description": "Network route tracing"},
            r"nslookup": {"pattern": r"nslookup", "severity": "LOW", "description": "DNS lookup"},
            r"dir\s+": {"pattern": r"dir\s+", "severity": "LOW", "description": "Directory listing"},
            r"type\s+": {"pattern": r"type\s+", "severity": "LOW", "description": "File content display"},
            r"findstr": {"pattern": r"findstr", "severity": "LOW", "description": "String search"},
        }
        
        # Storage for flagged commands
        self.flags = []
    
    def is_command_window(self, window_title, process_name):
        """
        Check if the current window is a command-line interface
        
        Args:
            window_title: Title of the window
            process_name: Name of the process
            
        Returns:
            bool: True if it's a command window, False otherwise
        """
        # Case insensitive checks
        window_title = window_title.lower()
        process_name = process_name.lower() if process_name else ""
        
        # Check based on window title
        for keyword in self.cmd_window_keywords:
            if keyword.lower() in window_title:
                return True
                
        # Check by process name
        for pattern in self.command_patterns:
            if re.search(pattern, process_name, re.IGNORECASE):
                return True
        
        # Additional checks for specific window characteristics
        if "console" in window_title or "terminal" in window_title:
            return True
                
        return False
        
    def check_for_flagged_commands(self, input_text, window_info):
        """
        Check if the input contains any flagged commands
        
        Args:
            input_text: Text to check for flagged commands
            window_info: Information about the current window
            
        Returns:
            dict or None: Flag information if a command was flagged, None otherwise
        """
        if not input_text or not input_text.strip():
            return None
        
        # Clean up the input text
        input_text = input_text.strip()
        
        # Check for flagged commands
        for cmd_key, cmd_info in self.flagged_commands.items():
            pattern = cmd_info["pattern"]
            if re.search(r"^" + pattern, input_text, re.IGNORECASE):
                # Create flag entry
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                flag = {
                    "timestamp": timestamp,
                    "window_title": window_info["title"],
                    "process": window_info["process"],
                    "command": input_text,
                    "severity": cmd_info["severity"],
                    "description": cmd_info["description"],
                    "severity_color": self.SEVERITY_LEVELS[cmd_info["severity"]]["color"],
                    "severity_description": self.SEVERITY_LEVELS[cmd_info["severity"]]["description"]
                }
                
                # Check if this exact command is already flagged
                for existing_flag in self.flags:
                    if existing_flag["command"] == input_text and existing_flag["timestamp"] == timestamp:
                        # Command already flagged, don't add a duplicate
                        return None
                
                # Store the flag
                self.flags.append(flag)
                
                return flag
                
        return None
        
    def get_flags(self):
        """Get all flagged commands"""
        return self.flags
        
    def clear_flags(self):
        """Clear all flagged commands"""
        self.flags = []
        
    def get_flag_count(self):
        """Get the number of flagged commands"""
        return len(self.flags)
    
    def get_severity_stats(self):
        """Get statistics about flagged commands by severity"""
        stats = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for flag in self.flags:
            stats[flag["severity"]] += 1
        return stats