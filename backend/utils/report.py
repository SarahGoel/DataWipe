import os
import time
import logging
from datetime import datetime
from typing import Dict, Any
from .certificate_generator import certificate_generator

logger = logging.getLogger(__name__)

def generate_pdf_report(device, method, passes, sha_before, sha_after, status, start_ts, end_ts):
    """Generate PDF report using the advanced certificate generator"""
    try:
        # Prepare wipe data
        wipe_data = {
            'device_path': device,
            'method': method,
            'passes': passes,
            'sha_before': sha_before,
            'sha_after': sha_after,
            'status': status,
            'started_at': datetime.fromtimestamp(start_ts).isoformat(),
            'completed_at': datetime.fromtimestamp(end_ts).isoformat(),
            'duration_seconds': end_ts - start_ts,
            'device_type': 'unknown',  # Will be updated by the wipe engine
            'model': 'Unknown',
            'serial': 'Unknown',
            'size': 0
        }
        
        # Generate PDF certificate
        pdf_path = certificate_generator.generate_pdf_certificate(wipe_data)
        logger.info(f"Generated PDF report: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {e}")
        # Fallback to simple report
        return _generate_simple_pdf_report(device, method, passes, sha_before, sha_after, status, start_ts, end_ts)

def generate_json_report(device, method, passes, sha_before, sha_after, status, start_ts, end_ts):
    """Generate JSON report using the advanced certificate generator"""
    try:
        # Prepare wipe data
        wipe_data = {
            'device_path': device,
            'method': method,
            'passes': passes,
            'sha_before': sha_before,
            'sha_after': sha_after,
            'status': status,
            'started_at': datetime.fromtimestamp(start_ts).isoformat(),
            'completed_at': datetime.fromtimestamp(end_ts).isoformat(),
            'duration_seconds': end_ts - start_ts,
            'device_type': 'unknown',  # Will be updated by the wipe engine
            'model': 'Unknown',
            'serial': 'Unknown',
            'size': 0
        }
        
        # Generate JSON certificate
        json_path = certificate_generator.generate_json_certificate(wipe_data)
        logger.info(f"Generated JSON report: {json_path}")
        return json_path
        
    except Exception as e:
        logger.error(f"Failed to generate JSON report: {e}")
        return None

def _generate_simple_pdf_report(device, method, passes, sha_before, sha_after, status, start_ts, end_ts):
    """Fallback simple PDF report generation"""
    try:
        os.makedirs("reports", exist_ok=True)
        ts = int(start_ts)
        path = f"reports/wipe_report_{ts}.pdf"
        
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        c = canvas.Canvas(path, pagesize=A4)
        c.drawString(50, 800, "ZeroTrace - Secure Wipe Report")
        c.drawString(50, 780, f"Device: {device}")
        c.drawString(50, 760, f"Method: {method} (passes={passes})")
        c.drawString(50, 740, f"Start: {time.ctime(start_ts)}")
        c.drawString(50, 720, f"End: {time.ctime(end_ts)}")
        c.drawString(50, 700, f"Status: {status}")
        c.drawString(50, 680, f"SHA before: {sha_before}")
        c.drawString(50, 660, f"SHA after: {sha_after}")
        c.save()
        return path
    except Exception as e:
        logger.error(f"Failed to generate simple PDF report: {e}")
        return None

def sign_report_with_openssl(pdf_path, private_key="keys/private.pem"):
    """Legacy function for backward compatibility"""
    try:
        # Use the new certificate generator for signing
        certificate_generator._sign_pdf(pdf_path)
        # Prefer .p7s created by _sign_pdf
        p7s_path = f"{pdf_path}.p7s"
        if os.path.exists(p7s_path):
            return p7s_path
        # Fallback: if a .sig exists, return it
        sig_path = f"{pdf_path}.sig"
        if os.path.exists(sig_path):
            return sig_path
        return None
    except Exception as e:
        logger.error(f"Failed to sign report: {e}")
        return None

def verify_certificate(filepath: str) -> Dict[str, Any]:
    """Verify certificate authenticity"""
    return certificate_generator.verify_certificate(filepath)
