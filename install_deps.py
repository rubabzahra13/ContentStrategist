#!/usr/bin/env python3
"""
Quick dependency installer for Replit
Run this script in Replit Shell if requirements.txt doesn't auto-install
"""

import subprocess
import sys

def install_dependencies():
    """Install all required dependencies"""
    print("🔧 Installing dependencies for ContentStrategist...")
    
    # Core dependencies that are essential
    essential_deps = [
        "flask==2.3.3",
        "openai==1.3.0", 
        "requests==2.31.0",
        "pandas==2.1.0",
        "openpyxl==3.1.2",
        "python-dotenv==1.0.0",
        "rapidfuzz==3.4.0"
    ]
    
    for dep in essential_deps:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
    
    print("\n🎉 Dependencies installation complete!")
    print("Now you can run: python main.py")

if __name__ == "__main__":
    install_dependencies()