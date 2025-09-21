#!/usr/bin/env python3
"""
ZeroTrace - Secure Data Wiping Tool
Startup script for both backend and frontend
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🔒 ZeroTrace v1.0.0 🔒                    ║
    ║              Secure Data Wiping Tool - SIH25070              ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  • NIST 800-88 compliant wiping                             ║
    ║  • DoD 5220.22-M standard                                   ║
    ║  • Cryptographic erasure for SSDs                           ║
    ║  • Real-time progress tracking                              ║
    ║  • Digital certificates and reports                         ║
    ║  • Cross-platform support                                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import cryptography
        import reportlab
        print("✅ Backend dependencies: OK")
    except ImportError as e:
        print(f"❌ Missing backend dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting ZeroTrace Backend...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
        sys.exit(1)

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting ZeroTrace Frontend...")
    
    # Change to frontend web directory
    frontend_dir = Path(__file__).parent / "frontend" / "web"
    os.chdir(frontend_dir)
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            sys.exit(1)
    
    # Start the development server
    try:
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")
        sys.exit(1)

def start_both():
    """Start both backend and frontend concurrently"""
    print("🚀 Starting ZeroTrace (Backend + Frontend)...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 ZeroTrace stopped by user")
        sys.exit(0)

def main():
    """Main entry point"""
    print_banner()
    
    # Check system requirements
    check_python_version()
    check_dependencies()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "both"
    
    if mode == "backend":
        start_backend()
    elif mode == "frontend":
        start_frontend()
    elif mode == "both":
        start_both()
    else:
        print("Usage: python run.py [backend|frontend|both]")
        print("  backend  - Start only the backend API server")
        print("  frontend - Start only the frontend development server")
        print("  both     - Start both backend and frontend (default)")
        sys.exit(1)

if __name__ == "__main__":
    main()
