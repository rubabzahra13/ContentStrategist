# For Replit compatibility - redirects to Flask app
import socket
from app import app

def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except socket.error:
            return False

if __name__ == '__main__':
    # Find an available port
    port = 5000
    if not is_port_available(port):
        port = 5001
    
    print(f"🚀 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)