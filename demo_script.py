#!/usr/bin/env python3
"""
ZeroTrace Demo Script
Automated demo flow for presentations
"""

import time
import webbrowser
import subprocess
import sys
from pathlib import Path

def print_step(step_num, title, description=""):
    """Print a demo step"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {title}")
    print(f"{'='*60}")
    if description:
        print(description)
    print()

def wait_for_user(message="Press Enter to continue..."):
    """Wait for user input"""
    input(f"\n⏸️  {message}")

def open_browser(url):
    """Open URL in browser"""
    try:
        webbrowser.open(url)
        print(f"🌐 Opened {url}")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")

def main():
    """Main demo script"""
    print("🎬 ZeroTrace Demo Script")
    print("This script will guide you through the ZeroTrace demonstration")
    print("Make sure ZeroTrace is running (python run.py)")
    print()
    
    wait_for_user("Press Enter to start the demo...")
    
    # Step 1: Introduction
    print_step(1, "Introduction", 
               "Welcome to ZeroTrace - A comprehensive secure data wiping tool\n"
               "Key Features:\n"
               "• NIST 800-88 compliant wiping\n"
               "• DoD 5220.22-M standard\n"
               "• Cryptographic erasure for SSDs\n"
               "• Real-time progress tracking\n"
               "• Tamper-proof certificates\n"
               "• Cross-platform support")
    
    open_browser("http://localhost:5173")
    wait_for_user("Show the home page and explain the features")
    
    # Step 2: Device Detection
    print_step(2, "Device Detection",
               "ZeroTrace automatically detects all connected storage devices\n"
               "• Shows device type, size, and model\n"
               "• Prevents system drive selection\n"
               "• Supports HDD, SSD, USB, and NVMe drives")
    
    print("Navigate to the Devices tab")
    wait_for_user("Show device detection and explain safety features")
    
    # Step 3: Method Selection
    print_step(3, "Wipe Method Selection",
               "Multiple secure wipe methods available:\n"
               "• NIST 800-88: Industry standard\n"
               "• DoD 5220.22-M: Military grade\n"
               "• Cryptographic Erasure: Fastest for SSDs\n"
               "• Gutmann Method: Maximum security\n"
               "• ATA Sanitize: Hardware-level\n"
               "• NVMe Format: Modern SSD support")
    
    print("Select a device and show method options")
    wait_for_user("Explain different methods and their use cases")
    
    # Step 4: Security Confirmation
    print_step(4, "Security Confirmation",
               "Multiple safety measures:\n"
               "• Clear warnings about data destruction\n"
               "• Multiple confirmation steps\n"
               "• Backup reminders\n"
               "• Device verification")
    
    print("Show the confirmation dialogs")
    wait_for_user("Highlight safety features and warnings")
    
    # Step 5: Progress Tracking
    print_step(5, "Real-time Progress Tracking",
               "Live progress monitoring:\n"
               "• Progress bar with percentage\n"
               "• Current pass and total passes\n"
               "• Bytes processed and total bytes\n"
               "• Time estimates and elapsed time\n"
               "• Status messages and updates")
    
    print("Start a wipe operation (use USB drive for safety)")
    wait_for_user("Show progress tracking and explain transparency")
    
    # Step 6: Certificate Generation
    print_step(6, "Certificate Generation",
               "Tamper-proof certificates:\n"
               "• PDF and JSON formats\n"
               "• Digital signatures\n"
               "• Device information\n"
               "• Wipe operation details\n"
               "• Verification data\n"
               "• Compliance standards")
    
    print("Navigate to Certificates tab")
    wait_for_user("Show certificate generation and features")
    
    # Step 7: Certificate Viewer
    print_step(7, "Certificate Viewer",
               "Comprehensive certificate details:\n"
               "• Formatted and raw JSON views\n"
               "• Digital signature verification\n"
               "• Device and operation information\n"
               "• Compliance badges\n"
               "• Download options")
    
    print("Open a certificate in the viewer")
    wait_for_user("Show certificate details and verification")
    
    # Step 8: API Documentation
    print_step(8, "API Documentation",
               "RESTful API for integration:\n"
               "• Device detection endpoints\n"
               "• Wipe operation endpoints\n"
               "• Progress tracking endpoints\n"
               "• Certificate endpoints\n"
               "• Verification endpoints")
    
    open_browser("http://localhost:8000/docs")
    wait_for_user("Show API documentation and explain integration")
    
    # Step 9: Technical Deep Dive
    print_step(9, "Technical Implementation",
               "Technical highlights:\n"
               "• Cross-platform device detection\n"
               "• Native OS tools integration\n"
               "• Cryptographic key management\n"
               "• Real-time progress updates\n"
               "• Database logging and audit trails\n"
               "• Modern web interface")
    
    print("Show the backend code structure")
    wait_for_user("Explain technical implementation and architecture")
    
    # Step 10: Conclusion
    print_step(10, "Conclusion",
               "ZeroTrace provides:\n"
               "• Industry-standard security\n"
               "• Tamper-proof documentation\n"
               "• Enterprise-ready features\n"
               "• Cross-platform compatibility\n"
               "• Professional interface\n"
               "• Compliance certification")
    
    print("Demo completed successfully!")
    print("\n🎉 Thank you for watching the ZeroTrace demonstration!")
    print("\nKey Takeaways:")
    print("• Comprehensive secure data wiping solution")
    print("• Meets NIST 800-88 and DoD 5220.22-M standards")
    print("• Generates tamper-proof certificates")
    print("• Suitable for enterprise IT asset recycling")
    print("• Modern, professional interface")

if __name__ == "__main__":
    main()
