from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import logging

from services.wipe_engine import list_drives, initiate_wipe
from database import get_db_session, get_wipe_history, get_session_progress, log_audit_event
from models import WipeMethod, WipeStatus, WipeSession
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

class WipeRequest(BaseModel):
    device: str
    method: str
    passes: int = 1
    force: bool = False

class FileWipeRequest(BaseModel):
    path: str
    passes: int = 1
    force: bool = False

class ProgressResponse(BaseModel):
    session_id: int
    progress_percentage: float
    status_message: str
    current_pass: int
    total_passes: int
    bytes_processed: int
    total_bytes: int
    estimated_time_remaining: Optional[float]

class WipeSessionResponse(BaseModel):
    id: int
    device_id: int
    method: str
    passes: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    sha_before: Optional[str]
    sha_after: Optional[str]
    error_message: Optional[str]
    report_path: Optional[str]
    signature_path: Optional[str]

class VerifyRequest(BaseModel):
    file_path: str
    embedded_pdf: bool = False
    # Optional: allow providing a third-party verification result payload
    third_party_tool: Optional[str] = None
    third_party_result: Optional[Dict[str, Any]] = None

@router.get("/drives")
def api_list_drives():
    """List all available drives"""
    try:
        result = list_drives()
        if result["ok"]:
            log_audit_event("list_drives", "system", "all")
        return result
    except Exception as e:
        logger.error(f"Failed to list drives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/wipe")
def api_wipe(req: WipeRequest, background_tasks: BackgroundTasks):
    """Initiate a wipe operation"""
    if not req.device or not req.method:
        raise HTTPException(status_code=400, detail="device and method required")
    
    if not req.force:
        raise HTTPException(status_code=400, detail="force=True required for destructive operations")
    
    try:
        # Log the wipe request
        log_audit_event("wipe_initiated", "device", req.device, 
                       details=f"method={req.method}, passes={req.passes}")
        
        # Start wipe operation
        result = initiate_wipe(req.device, req.method, req.passes, req.force)
        
        # Log completion
        log_audit_event("wipe_completed", "device", req.device, 
                       details=f"status={result.get('status', 'unknown')}")
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Wipe operation failed: {e}")
        log_audit_event("wipe_failed", "device", req.device, 
                       details=f"error={str(e)}")
        # Return a structured error that the frontend can display
        return {"result": {"success": False, "error": str(e)}}

@router.post("/wipe-file")
def api_wipe_file(req: FileWipeRequest):
    """Securely wipe a single file using NIST Clear (overwrite+delete) and generate certificates"""
    if not req.force:
        raise HTTPException(status_code=400, detail="force=True required for destructive operations")
    if not os.path.exists(req.path) or not os.path.isfile(req.path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        from services.wipe_methods import WipeMethods
        from utils.report import generate_pdf_report, generate_json_report
        import time

        methods = WipeMethods(os.name)
        start_ts = time.time()
        sha_before = None
        # Head hash before wipe
        try:
            with open(req.path, 'rb') as f:
                sha_before = __import__('hashlib').sha256(f.read(1024 * 1024)).hexdigest()
        except Exception:
            sha_before = None

        result = {"success": False}
        def progress(pct, msg):
            logger.info(f"File wipe progress: {pct}% - {msg}")
        methods.wipe_file_clear(req.path, max(1, min(req.passes, 3)), progress)
        success = True
        end_ts = time.time()

        # After wipe, file is deleted; sha_after is None
        sha_after = None
        pdf = generate_pdf_report("file:" + req.path, "nist_800_88", max(1, min(req.passes, 3)), sha_before, sha_after, "completed" if success else "failed", start_ts, end_ts)
        _ = generate_json_report("file:" + req.path, "nist_800_88", max(1, min(req.passes, 3)), sha_before, sha_after, "completed" if success else "failed", start_ts, end_ts)

        return {"success": success, "report": pdf}
    except Exception as e:
        logger.error(f"File wipe failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wipe/{session_id}/progress")
def api_get_progress(session_id: int):
    """Get progress for a specific wipe session"""
    try:
        progress = get_session_progress(session_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ProgressResponse(
            session_id=session_id,
            progress_percentage=progress.progress_percentage,
            status_message=progress.status_message or "",
            current_pass=progress.current_pass,
            total_passes=progress.total_passes,
            bytes_processed=progress.bytes_processed,
            total_bytes=progress.total_bytes,
            estimated_time_remaining=progress.estimated_time_remaining
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wipe/sessions")
def api_get_wipe_sessions(limit: int = 50):
    """Get wipe session history"""
    try:
        sessions = get_wipe_history(limit)
        return [WipeSessionResponse(
            id=session.id,
            device_id=session.device_id,
            method=session.method.value,
            passes=session.passes,
            status=session.status.value,
            started_at=session.started_at,
            completed_at=session.completed_at,
            duration_seconds=session.duration_seconds,
            sha_before=session.sha_before,
            sha_after=session.sha_after,
            error_message=session.error_message,
            report_path=session.report_path,
            signature_path=session.signature_path
        ) for session in sessions]
    except Exception as e:
        logger.error(f"Failed to get wipe sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wipe/methods")
def api_get_wipe_methods():
    """Get available wipe methods"""
    return {
        "methods": [
            {
                "id": method.value,
                "name": method.value.replace("_", " ").title(),
                "description": _get_method_description(method)
            }
            for method in WipeMethod
        ]
    }

def _get_method_description(method: WipeMethod) -> str:
    """Get description for wipe method"""
    descriptions = {
        WipeMethod.NIST_800_88: "NIST 800-88 compliant secure erase (Clear + Verify + Purge)",
        WipeMethod.DOD_5220_22_M: "DoD 5220.22-M 3-pass secure erase (0s, 1s, random)",
        WipeMethod.GUTMANN: "Gutmann 35-pass secure erase (maximum security)",
        WipeMethod.CRYPTO_ERASE: "Cryptographic erasure (preferred for SSDs)",
        WipeMethod.ATA_SANITIZE: "ATA sanitize command",
        WipeMethod.NVME_FORMAT: "NVMe format with crypto erase",
        WipeMethod.SINGLE_PASS: "Single pass with zeros",
        WipeMethod.THREE_PASS: "Three pass (zeros, ones, random)"
    }
    return descriptions.get(method, "Unknown method")

@router.get("/reports/{session_id}")
def api_download_report(session_id: int):
    """Download wipe report for a session"""
    try:
        db = get_db_session()
        session = db.query(WipeSession).filter(WipeSession.id == session_id).first()
        db.close()
        
        if not session or not session.report_path:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if not os.path.exists(session.report_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        return FileResponse(
            session.report_path,
            media_type="application/pdf",
            filename=f"wipe_report_{session_id}.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{session_id}/signature")
def api_download_signature(session_id: int):
    """Download wipe report signature for a session"""
    try:
        db = get_db_session()
        session = db.query(WipeSession).filter(WipeSession.id == session_id).first()
        db.close()
        
        if not session or not session.signature_path:
            raise HTTPException(status_code=404, detail="Signature not found")
        
        if not os.path.exists(session.signature_path):
            raise HTTPException(status_code=404, detail="Signature file not found")
        
        return FileResponse(
            session.signature_path,
            media_type="application/octet-stream",
            filename=f"wipe_report_{session_id}.pdf.sig"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download signature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{session_id}/json")
def api_download_json_report(session_id: int):
    """Download JSON certificate for a session"""
    try:
        db = get_db_session()
        session = db.query(WipeSession).filter(WipeSession.id == session_id).first()
        db.close()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Look for JSON report in reports directory
        reports_dir = Path("reports")
        json_files = list(reports_dir.glob(f"*session_{session_id}*.json"))
        
        if not json_files:
            # Generate JSON report if not exists
            from utils.report import generate_json_report
            json_path = generate_json_report(
                session.device.device_path if session.device else "unknown",
                session.method.value,
                session.passes,
                session.sha_before or "",
                session.sha_after or "",
                session.status.value,
                session.started_at.timestamp() if session.started_at else 0,
                session.completed_at.timestamp() if session.completed_at else 0
            )
            if not json_path or not os.path.exists(json_path):
                raise HTTPException(status_code=404, detail="JSON report not found")
        else:
            json_path = str(json_files[0])
        
        return FileResponse(
            json_path,
            media_type="application/json",
            filename=f"wipe_certificate_{session_id}.json"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download JSON report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/verify")
def api_verify_certificate(req: VerifyRequest):
    """Verify certificate authenticity"""
    try:
        from utils.report import verify_certificate
        from pyhanko.sign.validation import validate_pdf_signature
        from pyhanko_certvalidator.context import ValidationContext
        
        file_path = req.file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # If PDF, try verifying embedded signature first
        if req.embedded_pdf and file_path.lower().endswith('.pdf'):
            try:
                vc = ValidationContext(allow_fetching=True)
                with open(file_path, 'rb') as f:
                    from pyhanko.sign.general import load_pdf
                    pdf = load_pdf(f)
                # Validate all signature fields; succeed if any is valid
                from pyhanko.sign.fields import enumerate_sig_fields
                fields = list(enumerate_sig_fields(pdf))
                results = []
                for field_name, _ in fields:
                    vr = validate_pdf_signature(pdf, field_name, validation_context=vc)
                    results.append({
                        'field': field_name,
                        'intact': vr.modification_level.value == 'UNMODIFIED',
                        'trusted': vr.trust_established,
                    })
                if results:
                    any_valid = any(r['intact'] and r['trusted'] for r in results)
                    return {"valid": any_valid, "details": results}
            except Exception as e:
                logger.warning(f"Embedded PDF signature validation failed: {e}")

        # Fallback: detached .sig/.p7s JSON/PDF verification
        result = verify_certificate(file_path)

        # If third-party verification payload is provided, include it in the response
        if req.third_party_tool and req.third_party_result is not None:
            result["third_party"] = {
                "tool": req.third_party_tool,
                "result": req.third_party_result
            }
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/certificates")
def api_list_certificates():
    """List all available certificates"""
    try:
        reports_dir = Path("reports")
        if not reports_dir.exists():
            return {"certificates": []}
        
        certificates = []
        for file_path in reports_dir.glob("*.pdf"):
            stat = file_path.stat()
            certificates.append({
                "filename": file_path.name,
                "path": str(file_path),
                "type": "PDF",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "download_url": f"/reports/{file_path.name}"
            })
        
        for file_path in reports_dir.glob("*.json"):
            stat = file_path.stat()
            certificates.append({
                "filename": file_path.name,
                "path": str(file_path),
                "type": "JSON",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "download_url": f"/reports/{file_path.name}"
            })
        
        # Sort by creation time (newest first)
        certificates.sort(key=lambda x: x["created"], reverse=True)
        
        return {"certificates": certificates}
    except Exception as e:
        logger.error(f"Failed to list certificates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def api_health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
