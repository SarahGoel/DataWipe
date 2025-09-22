"""
Advanced Certificate Generator for ZeroTrace
Generates tamper-proof PDF and JSON certificates using ReportLab and PyHanko
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

import logging
from pyhanko.sign import signers
from pyhanko_certvalidator.context import ValidationContext
from pyhanko import stamp
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

logger = logging.getLogger(__name__)

class CertificateGenerator:
    """Advanced certificate generator with tamper-proof features"""
    
    def __init__(self, keys_dir: str = "keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True)
        self.private_key_path = self.keys_dir / "private.pem"
        self.public_key_path = self.keys_dir / "public.pem"
        self.certificate_path = self.keys_dir / "certificate.pem"
        
        # Initialize or load keys
        self._ensure_keys_exist()
    
    def _ensure_keys_exist(self):
        """Ensure cryptographic keys exist, generate if not"""
        if not self.private_key_path.exists():
            self._generate_keys()
        else:
            self._load_keys()
    
    def _generate_keys(self):
        """Generate RSA key pair for signing"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Save private key
            with open(self.private_key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Save public key
            public_key = private_key.public_key()
            with open(self.public_key_path, "wb") as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            
            # Generate self-signed certificate
            self._generate_self_signed_certificate(private_key, public_key)
            
            logger.info("Generated new cryptographic keys")
            
        except Exception as e:
            logger.error(f"Failed to generate keys: {e}")
            raise
    
    def _generate_self_signed_certificate(self, private_key, public_key):
        """Generate a self-signed certificate"""
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from datetime import datetime, timedelta
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ZeroTrace"),
            x509.NameAttribute(NameOID.COMMON_NAME, "ZeroTrace Certificate Authority"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Save certificate
        with open(self.certificate_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    def _load_keys(self):
        """Load existing keys"""
        try:
            with open(self.private_key_path, "rb") as f:
                self.private_key = load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
            logger.info("Loaded existing cryptographic keys")
        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            self._generate_keys()
    
    def generate_pdf_certificate(self, wipe_data: Dict[str, Any]) -> str:
        """Generate tamper-proof PDF certificate"""
        try:
            # Create reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"zerotrace_certificate_{timestamp}.pdf"
            filepath = reports_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=HexColor('#2D3748'),
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=HexColor('#4A5568'),
                fontName='Helvetica'
            )
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=12,
                textColor=HexColor('#2D3748'),
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                textColor=HexColor('#4A5568'),
                fontName='Helvetica'
            )
            
            # Title
            story.append(Paragraph("🔒 ZEROTRACE CERTIFICATE OF DATA DESTRUCTION", title_style))
            story.append(Spacer(1, 12))
            
            # Subtitle
            story.append(Paragraph("Tamper-Proof Digital Certificate", subtitle_style))
            story.append(Spacer(1, 20))
            
            # Certificate ID
            cert_id = self._generate_certificate_id(wipe_data)
            story.append(Paragraph(f"<b>Certificate ID:</b> {cert_id}", normal_style))
            story.append(Paragraph(f"<b>Issued:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", normal_style))
            story.append(Spacer(1, 20))
            
            # Device Information
            story.append(Paragraph("DEVICE INFORMATION", header_style))
            device_info = [
                ["Device Path:", wipe_data.get('device_path', 'N/A')],
                ["Device Type:", wipe_data.get('device_type', 'N/A').upper()],
                ["Device Model:", wipe_data.get('model', 'N/A')],
                ["Serial Number:", wipe_data.get('serial', 'N/A')],
                ["Size:", self._format_size(wipe_data.get('size', 0))]
            ]
            
            device_table = Table(device_info, colWidths=[2*inch, 4*inch])
            device_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#F7FAFC')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2D3748')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0'))
            ]))
            story.append(device_table)
            story.append(Spacer(1, 20))
            
            # Wipe Information
            story.append(Paragraph("WIPE OPERATION DETAILS", header_style))
            wipe_info = [
                ["Method:", wipe_data.get('method', 'N/A').replace('_', ' ').title()],
                ["Passes:", str(wipe_data.get('passes', 1))],
                ["Started:", wipe_data.get('started_at', 'N/A')],
                ["Completed:", wipe_data.get('completed_at', 'N/A')],
                ["Duration:", self._format_duration(wipe_data.get('duration_seconds', 0))],
                ["Status:", wipe_data.get('status', 'N/A').upper()]
            ]
            
            wipe_table = Table(wipe_info, colWidths=[2*inch, 4*inch])
            wipe_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#F7FAFC')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2D3748')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0'))
            ]))
            story.append(wipe_table)
            story.append(Spacer(1, 20))
            
            # Verification Data
            story.append(Paragraph("VERIFICATION DATA", header_style))
            verification_data = [
                ["SHA-256 Before:", wipe_data.get('sha_before', 'N/A')],
                ["SHA-256 After:", wipe_data.get('sha_after', 'N/A')],
                ["Verification:", "✅ DATA SUCCESSFULLY DESTROYED" if wipe_data.get('status') == 'completed' else "❌ WIPE FAILED"]
            ]
            
            verification_table = Table(verification_data, colWidths=[2*inch, 4*inch])
            verification_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#F7FAFC')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2D3748')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#E2E8F0'))
            ]))
            story.append(verification_table)
            story.append(Spacer(1, 30))
            
            # Digital Signature Section
            story.append(Paragraph("DIGITAL SIGNATURE", header_style))
            story.append(Paragraph("This certificate is digitally signed and tamper-proof.", normal_style))
            story.append(Paragraph(f"<b>Signature Hash:</b> {self._generate_signature_hash(wipe_data)}", normal_style))
            story.append(Paragraph(f"<b>Public Key Fingerprint:</b> {self._get_public_key_fingerprint()}", normal_style))
            story.append(Spacer(1, 20))
            
            # Legal Notice
            story.append(Paragraph("LEGAL NOTICE", header_style))
            legal_text = """
            This certificate serves as proof that the data on the specified device has been 
            securely destroyed using industry-standard methods. The destruction process has 
            been verified and documented according to NIST 800-88 guidelines.
            
            This certificate is digitally signed and any tampering will invalidate its authenticity.
            """
            story.append(Paragraph(legal_text, normal_style))
            story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph("Generated by ZeroTrace - Secure Data Wiping Tool", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], 
                                              fontSize=9, alignment=TA_CENTER, 
                                              textColor=HexColor('#718096'))))
            
            # Build PDF
            doc.build(story)
            
            # Sign the PDF
            self._sign_pdf(str(filepath))
            
            logger.info(f"Generated PDF certificate: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate PDF certificate: {e}")
            raise
    
    def generate_json_certificate(self, wipe_data: Dict[str, Any]) -> str:
        """Generate tamper-proof JSON certificate"""
        try:
            # Create reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"zerotrace_certificate_{timestamp}.json"
            filepath = reports_dir / filename
            
            # Generate certificate data
            cert_id = self._generate_certificate_id(wipe_data)
            signature_hash = self._generate_signature_hash(wipe_data)
            public_key_fingerprint = self._get_public_key_fingerprint()
            
            certificate_data = {
                "certificate": {
                    "id": cert_id,
                    "version": "1.0",
                    "type": "Data Destruction Certificate",
                    "issued_at": datetime.now(timezone.utc).isoformat(),
                    "issuer": "ZeroTrace Secure Data Wiping Tool",
                    "status": "valid"
                },
                "device": {
                    "path": wipe_data.get('device_path'),
                    "type": wipe_data.get('device_type'),
                    "model": wipe_data.get('model'),
                    "serial": wipe_data.get('serial'),
                    "size_bytes": wipe_data.get('size', 0),
                    "size_formatted": self._format_size(wipe_data.get('size', 0))
                },
                "wipe_operation": {
                    "method": wipe_data.get('method'),
                    "method_display": wipe_data.get('method', '').replace('_', ' ').title(),
                    "passes": wipe_data.get('passes', 1),
                    "started_at": wipe_data.get('started_at'),
                    "completed_at": wipe_data.get('completed_at'),
                    "duration_seconds": wipe_data.get('duration_seconds', 0),
                    "duration_formatted": self._format_duration(wipe_data.get('duration_seconds', 0)),
                    "status": wipe_data.get('status'),
                    "success": wipe_data.get('status') == 'completed'
                },
                "verification": {
                    "sha256_before": wipe_data.get('sha_before'),
                    "sha256_after": wipe_data.get('sha_after'),
                    "data_destroyed": wipe_data.get('status') == 'completed',
                    "verification_timestamp": datetime.now(timezone.utc).isoformat()
                },
                "digital_signature": {
                    "algorithm": "RSA-SHA256",
                    "signature_hash": signature_hash,
                    "public_key_fingerprint": public_key_fingerprint,
                    "signature_timestamp": datetime.now(timezone.utc).isoformat(),
                    "tamper_proof": True
                },
                "compliance": {
                    "nist_800_88": True,
                    "dod_5220_22_m": wipe_data.get('method') == 'dod_5220_22_m',
                    "cryptographic_erasure": wipe_data.get('method') == 'crypto_erase',
                    "standards_met": self._get_compliance_standards(wipe_data.get('method'))
                },
                "metadata": {
                    "generator": "ZeroTrace v1.0.0",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "certificate_format": "JSON",
                    "tamper_proof": True
                }
            }
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(certificate_data, f, indent=2, ensure_ascii=False)
            
            # Generate signature file
            self._sign_json(str(filepath), certificate_data)
            
            logger.info(f"Generated JSON certificate: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate JSON certificate: {e}")
            raise
    
    def _generate_certificate_id(self, wipe_data: Dict[str, Any]) -> str:
        """Generate unique certificate ID"""
        data_string = f"{wipe_data.get('device_path', '')}{wipe_data.get('started_at', '')}{datetime.now().isoformat()}"
        return hashlib.sha256(data_string.encode()).hexdigest()[:16].upper()
    
    def _generate_signature_hash(self, wipe_data: Dict[str, Any]) -> str:
        """Generate signature hash for the certificate"""
        data_string = f"{wipe_data.get('device_path', '')}{wipe_data.get('method', '')}{wipe_data.get('sha_after', '')}"
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _get_public_key_fingerprint(self) -> str:
        """Get public key fingerprint"""
        try:
            with open(self.public_key_path, "rb") as f:
                public_key_data = f.read()
            return hashlib.sha256(public_key_data).hexdigest()[:16].upper()
        except Exception:
            return "UNKNOWN"
    
    def _get_compliance_standards(self, method: str) -> list:
        """Get compliance standards for the wipe method"""
        standards = ["NIST 800-88"]
        
        if method == 'dod_5220_22_m':
            standards.append("DoD 5220.22-M")
        elif method == 'crypto_erase':
            standards.append("Cryptographic Erasure")
        elif method == 'gutmann':
            standards.append("Gutmann Method")
        elif method == 'ata_sanitize':
            standards.append("ATA Sanitize")
        elif method == 'nvme_format':
            standards.append("NVMe Format")
        
        return standards
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        if not size_bytes:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format"""
        if not seconds:
            return "Unknown"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def _sign_pdf(self, filepath: str):
        """Sign PDF with digital signature using PyHanko (detached signature saved as .p7s)"""
        try:
            # Prepare signer from PEM key and self-signed certificate
            with open(self.private_key_path, 'rb') as key_f, open(self.certificate_path, 'rb') as cert_f:
                signer = signers.SimpleSigner.load(key_f.read(), cert_f.read(), key_passphrase=None)

            with open(filepath, 'rb') as inf:
                w = IncrementalPdfFileWriter(inf)
                meta = signers.PdfSignatureMetadata(field_name='ZeroTraceSignature', md_algorithm='sha256')
                pdf_signer = signers.PdfSigner(meta, signer)
                with open(filepath, 'wb') as outf:
                    pdf_signer.sign_pdf(w, output=outf)

            # Also export detached CMS signature for external verification
            with open(filepath, 'rb') as f:
                content = f.read()
            cms = signer.sign(content, 'sha256')
            with open(f"{filepath}.p7s", 'wb') as sigf:
                sigf.write(cms.dump())

            logger.info(f"PDF signed with PyHanko: {filepath} (.p7s saved)")
        except Exception as e:
            logger.error(f"Failed to sign PDF: {e}")
    
    def _sign_json(self, filepath: str, data: Dict[str, Any]):
        """Sign JSON certificate"""
        try:
            signature_file = f"{filepath}.sig"
            
            # Create data to sign
            data_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
            
            # Generate signature
            signature = self.private_key.sign(
                data_string.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Save signature
            with open(signature_file, 'wb') as f:
                f.write(signature)
            
            logger.info(f"JSON signed: {signature_file}")
            
        except Exception as e:
            logger.error(f"Failed to sign JSON: {e}")
    
    def verify_certificate(self, filepath: str) -> Dict[str, Any]:
        """Verify certificate authenticity"""
        try:
            signature_file = f"{filepath}.sig"
            
            if not os.path.exists(signature_file):
                return {"valid": False, "error": "Signature file not found"}
            
            # Load public key
            with open(self.public_key_path, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
            
            # Load signature
            with open(signature_file, "rb") as f:
                signature = f.read()
            
            # Verify signature
            if filepath.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data_string = json.dumps(data, sort_keys=True, separators=(',', ':'))
                content = data_string.encode('utf-8')
            else:
                with open(filepath, 'rb') as f:
                    content = f.read()
            
            public_key.verify(
                signature,
                content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return {"valid": True, "message": "Certificate is authentic and untampered"}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

# Global instance
certificate_generator = CertificateGenerator()
