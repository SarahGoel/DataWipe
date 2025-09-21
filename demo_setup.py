#!/usr/bin/env python3
"""
ZeroTrace Demo Setup Script
Quick setup for presentations and demonstrations
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🔒 ZeroTrace - Secure Data Wiping Tool")
    print("   Demo Setup for Smart India Hackathon 2025")
    print("=" * 60)
    print()

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ required. Current version:", f"{python_version.major}.{python_version.minor}")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js 16+")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    frontend_dir = Path("frontend/web")
    if frontend_dir.exists():
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            print("✅ Node.js dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Node.js dependencies: {e}")
            return False
    else:
        print("❌ Frontend directory not found")
        return False
    
    return True

def create_demo_data():
    """Create demo data and directories"""
    print("\n📁 Setting up demo environment...")
    
    # Create necessary directories
    directories = [
        "data",
        "reports", 
        "keys",
        "certificates/logs",
        "certificates/tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create demo README
    demo_readme = """# ZeroTrace Demo Environment

This directory contains the ZeroTrace demo environment.

## Quick Start
1. Run `python run.py` to start both backend and frontend
2. Open http://localhost:5173 in your browser
3. Use a USB drive for safe testing

## Safety Notes
- Never test on system drives
- Always backup important data
- Use external USB drives only

## Demo Features
- Device detection and selection
- Multiple wipe methods (NIST, DoD, Crypto)
- Real-time progress tracking
- Tamper-proof certificate generation
- Digital signature verification

## API Documentation
- Backend API: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health
"""
    
    with open("DEMO_README.md", "w") as f:
        f.write(demo_readme)
    
    print("✅ Demo environment ready")

def start_application():
    """Start the ZeroTrace application"""
    print("\n🚀 Starting ZeroTrace...")
    print("This will start both the backend and frontend servers.")
    print("Press Ctrl+C to stop the application.")
    print()
    
    try:
        # Start the application
        subprocess.run([sys.executable, 'run.py'])
    except KeyboardInterrupt:
        print("\n\n👋 ZeroTrace stopped. Thank you for the demo!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nYou can start manually with: python run.py")

def show_access_info():
    """Show access information"""
    print("\n🌐 Access Information:")
    print("   Frontend: http://localhost:5173")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/api/health")
    print()

def main():
    """Main demo setup function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing dependencies.")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        return
    
    # Create demo data
    create_demo_data()
    
    # Show access information
    show_access_info()
    
    # Ask if user wants to start the application
    response = input("🚀 Start ZeroTrace now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        start_application()
    else:
        print("\n📝 To start ZeroTrace later, run: python run.py")
        print("📖 See PRESENTATION_GUIDE.md for demo instructions")

if __name__ == "__main__":
    main()
