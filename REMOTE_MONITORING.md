# Remote Monitoring Feature

This document explains how to set up and use the remote monitoring feature in the Advanced Keystroke Monitor application.

## Overview

The remote monitoring feature allows you to:

- Monitor keylogging activity from a different computer or device
- Receive real-time notifications of flagged commands
- View screenshots remotely
- Access logs from multiple monitored devices in one interface

## Components

The remote monitoring system consists of two main components:

1. **Client** - The keylogger application with remote monitoring enabled
2. **Server** - A Flask-based web server that receives and displays the monitoring data

## Server Setup

### Requirements

The server requires Python with the following packages:
- Flask
- Flask-SocketIO
- Werkzeug

You can install them with:

```bash
pip install flask flask-socketio werkzeug
```

### Running the Server

1. Copy the `remote_server.py` file to the computer that will act as the server
2. Create a `templates` folder in the same directory (the server will generate default templates)
3. Run the server:

```bash
python remote_server.py
```

4. The server will start on port 5000. You can access it at:
   - http://localhost:5000 (on the same computer)
   - http://SERVER_IP:5000 (from other computers)

### Server Security

**Warning**: The default server has minimal security:
- Default login: `admin` / `admin123`
- Default API key: `test_key`

For production use, you should:
1. Change the default login credentials in the `users` dictionary
2. Change the default API key in the `api_keys` dictionary
3. Set up HTTPS using a proper SSL certificate
4. Configure a firewall to restrict access

## Client Configuration

To enable remote monitoring on the keylogger client:

1. Open the keylogger application
2. Go to the "Remote Monitoring" tab
3. Enter the server URL (e.g., http://SERVER_IP:5000)
4. Enter the API key (default: `test_key`)
5. Set the desired sync interval (how often data is sent)
6. Check "Enable Remote Monitoring"
7. Click "Apply Settings"
8. Click "Test Connection" to verify connectivity

## Web Interface

The web interface provides:

1. **Dashboard** - Overview of connected devices, recent flags, and activity
2. **Devices** - List of all connected monitoring devices
3. **Logs** - Keystroke logs from all devices
4. **Flags** - Commands that triggered detection rules
5. **Screenshots** - Screenshots captured from monitored devices

## Data Privacy and Security Considerations

The remote monitoring system transmits sensitive data:
- Keystrokes and input events
- Window title information
- Flagged commands
- System information (hostname, IP address)

Always ensure:
1. You have proper authorization to monitor the devices
2. The server is properly secured
3. Communication is encrypted (use HTTPS in production)
4. Access to the web interface is restricted

## Troubleshooting

If you encounter issues with remote monitoring:

1. **Connection problems**:
   - Check that the server is running
   - Verify the server URL is correct
   - Ensure the API key matches
   - Check firewall settings

2. **Data not appearing**:
   - Verify monitoring is active on the client
   - Check the server logs for errors
   - Ensure sync interval isn't too long

3. **Performance issues**:
   - Increase the sync interval to reduce network traffic
   - Reduce the amount of data stored on the server
   - Consider using a more powerful server for multiple devices