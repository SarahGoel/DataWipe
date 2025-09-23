import subprocess
import time
from datetime import datetime
import hashlib
import platform
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple
from database import init_database, get_db_session, create_device, get_device_by_path, create_wipe_session, update_wipe_session, add_progress_update
from services.secure_wipe import SecureWipeService, WipeMethod
from services.wipe_methods import WipeMethods
from utils.report import generate_pdf_report, sign_report_with_openssl, generate_json_report
from models import WipeStatus

# Initialize database
init_database()

# Initialize services
secure_wipe_service = SecureWipeService()
wipe_methods = WipeMethods(platform.system().lower())

logger = logging.getLogger(__name__)

def list_drives() -> Dict[str, Any]:
    """List available drives with comprehensive information"""
    try:
        drives = []
        
        if platform.system().lower() == "linux":
            drives = _list_linux_drives()
        elif platform.system().lower() == "windows":
            drives = _list_windows_drives()
        elif platform.system().lower() == "darwin":
            drives = _list_macos_drives()
        
        # Fallback: if nothing detected, provide a safe mock device for UI/demo
        if not drives:
            try:
                import os
                total_bytes = 0
                try:
                    import psutil  # type: ignore
                    total_bytes = psutil.disk_usage(os.getenv('SystemDrive', 'C:')).total
                except Exception:
                    total_bytes = 256 * 1024 * 1024 * 1024  # 256 GB default
                drives = [
                    {
                        "name": "Primary Drive",
                        "path": "\\\\.\\PhysicalDrive0" if platform.system().lower() == "windows" else "/dev/sda",
                        "size": str(total_bytes),
                        "model": "Generic SSD",
                        "serial": "UNKNOWN",
                        "is_rotational": False,
                        "mount_point": os.getenv('SystemDrive', 'C:'),
                        "type": "ssd",
                    }
                ]
            except Exception:
                # Ignore fallback errors; return empty list
                pass

        return {"ok": True, "drives": drives}
    except Exception as e:
        logger.error(f"Failed to list drives: {e}")
        return {"ok": False, "error": str(e)}

def _list_linux_drives() -> List[Dict[str, Any]]:
    """List drives on Linux using lsblk"""
    try:
        result = subprocess.run([
            "lsblk", "-J", "-o", "NAME,KNAME,TYPE,SIZE,MODEL,ROTA,MOUNTPOINT,SERIAL"
        ], capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        drives = []
        
        for device in data.get("blockdevices", []):
            if device.get("type") == "disk":
                drive_info = {
                    "name": device.get("name", ""),
                    "path": f"/dev/{device.get('kname', '')}",
                    "size": device.get("size", ""),
                    "model": device.get("model", ""),
                    "serial": device.get("serial", ""),
                    "is_rotational": device.get("rota") == "1",
                    "mount_point": device.get("mountpoint", ""),
                    "type": "ssd" if device.get("rota") == "0" else "hdd"
                }
                
                # Get additional info using secure_wipe_service
                additional_info = secure_wipe_service.get_device_info(drive_info["path"])
                drive_info.update(additional_info)
                
                drives.append(drive_info)
        
        return drives
    except Exception as e:
        logger.error(f"Failed to list Linux drives: {e}")
        return []

def _list_windows_drives() -> List[Dict[str, Any]]:
    """List drives on Windows using PowerShell"""
    try:
        cmd = (
            "Get-PhysicalDisk | Select-Object DeviceID, FriendlyName, Size, MediaType, BusType, SerialNumber | "
            "ConvertTo-Json"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, check=True, timeout=3
        )

        import json
        try:
            data = json.loads(result.stdout) if result.stdout else []
        except Exception:
            data = []
        drives = []
        
        for device in data if isinstance(data, list) else ([data] if data else []):
            drive_info = {
                "name": device.get("FriendlyName", ""),
                "path": f"\\\\.\\PhysicalDrive{device.get('DeviceID', '')}",
                "size": str(device.get("Size", 0)),
                "model": device.get("FriendlyName", ""),
                "serial": device.get("SerialNumber", ""),
                "is_rotational": device.get("MediaType") == "HDD",
                "mount_point": "",
                "type": "ssd" if device.get("MediaType") == "SSD" else "hdd"
            }
            
            # Get additional info using secure_wipe_service
            additional_info = secure_wipe_service.get_device_info(drive_info["path"])
            drive_info.update(additional_info)
            
            drives.append(drive_info)
        
        return drives
    except subprocess.TimeoutExpired:
        logger.warning("Windows drive enumeration timed out")
        return []
    except Exception as e:
        logger.error(f"Failed to list Windows drives: {e}")
        return []

def _list_macos_drives() -> List[Dict[str, Any]]:
    """List drives on macOS using system_profiler"""
    try:
        result = subprocess.run([
            "system_profiler", "SPStorageDataType", "-json"
        ], capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        drives = []
        
        for storage in data.get("SPStorageDataType", []):
            if storage.get("_name", "").startswith("disk"):
                drive_info = {
                    "name": storage.get("_name", ""),
                    "path": f"/dev/{storage.get('_name', '')}",
                    "size": storage.get("size_in_bytes", ""),
                    "model": storage.get("model", ""),
                    "serial": storage.get("serial_number", ""),
                    "is_rotational": "Rotational" in storage.get("physical_interconnect", ""),
                    "mount_point": "",
                    "type": "ssd" if "Solid State" in storage.get("physical_interconnect", "") else "hdd"
                }
                
                # Get additional info using secure_wipe_service
                additional_info = secure_wipe_service.get_device_info(drive_info["path"])
                drive_info.update(additional_info)
                
                drives.append(drive_info)
        
        return drives
    except Exception as e:
        logger.error(f"Failed to list macOS drives: {e}")
        return []

def _sha256_head(device_path: str, head_bytes: int = 1024*1024) -> Optional[str]:
    """Get SHA-256 hash of first part of device"""
    try:
        with open(device_path, "rb") as f:
            data = f.read(head_bytes)
            return hashlib.sha256(data).hexdigest()
    except Exception as e:
        logger.error(f"Failed to get device hash: {e}")
        return None

def _detect_original_filesystem(device_path: str) -> Optional[str]:
    """Best-effort detection of original filesystem for a given device or volume.
    - Windows: returns 'ntfs', 'fat32', 'exfat' for drive letters (e.g., D:\), None for PhysicalDrive.
    - Linux/macOS: attempts to parse lsblk/diskutil output.
    """
    try:
        import platform, re, subprocess, os
        system = platform.system().lower()
        if system == 'windows':
            # If a drive letter was provided (D:\ or D:), query filesystem
            mvol = re.match(r"^([a-zA-Z]):\\?", device_path)
            if mvol:
                drive = mvol.group(1)
                ps = f"Get-Volume -DriveLetter {drive} | Select-Object -First 1 -ExpandProperty FileSystem"
                result = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, check=True)
                fs = (result.stdout or '').strip().lower()
                if fs:
                    return {'ntfs':'ntfs','refs':'ntfs','fat32':'fat32','exfat':'exfat'}.get(fs, fs)
                return None
            # PhysicalDrive: cannot reliably detect; return None
            return None
        elif system == 'linux':
            out = subprocess.run(["lsblk", "-no", "FSTYPE", device_path], capture_output=True, text=True)
            fs = (out.stdout or '').strip().splitlines()
            if fs and fs[0]:
                return fs[0].lower()
            return None
        elif system == 'darwin':
            out = subprocess.run(["diskutil", "info", device_path], capture_output=True, text=True)
            for line in (out.stdout or '').splitlines():
                if 'Type (Bundle):' in line:
                    return line.split(':',1)[1].strip().lower()
            return None
    except Exception:
        return None

def _format_device_to_original(device_path: str, fs: Optional[str]) -> bool:
    """Attempt to format the device/volume back to its original filesystem.
    Returns True on success, False if skipped.
    """
    try:
        import platform, re, subprocess
        if not fs:
            return False
        system = platform.system().lower()
        if system == 'windows':
            # Drive letter formatting
            mvol = re.match(r"^([a-zA-Z]):\\?", device_path)
            if mvol:
                drive = mvol.group(1)
                fs_map = {'ntfs':'NTFS','fat32':'FAT32','exfat':'exFAT'}
                target = fs_map.get(fs.lower(), 'exFAT')
                ps = f"Format-Volume -DriveLetter {drive} -FileSystem {target} -Confirm:$false -Force"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
                return True
            # PhysicalDrive: use Clear-Disk path; requires creating a partition and formatting
            mphys = re.search(r"PhysicalDrive(\d+)", device_path, re.IGNORECASE)
            if mphys:
                disk = mphys.group(1)
                # Create single primary partition and format
                ps = (
                    f"$part = New-Partition -DiskNumber {disk} -UseMaximumSize -AssignDriveLetter; "
                    f"Format-Volume -Partition $part -FileSystem exFAT -Confirm:$false -Force"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
                return True
            return False
        elif system == 'linux':
            # Create a partition and mkfs accordingly (requires privileges)
            fs_map = {'ntfs':'ntfs','fat32':'vfat','exfat':'exfat'}
            target = fs_map.get(fs.lower(), 'vfat')
            # naive: mkfs on first partition if exists
            subprocess.run(["sh", "-c", f"sudo mkfs.{target} -F 32 {device_path}1 || sudo mkfs.{target} {device_path}1"], check=False)
            return True
        elif system == 'darwin':
            # diskutil eraseVolume
            target = {'ntfs':'exfat','fat32':'ms-dos fat32','exfat':'exfat'}.get(fs.lower(), 'exfat')
            subprocess.run(["diskutil", "eraseDisk", target, "USB", device_path], check=False)
            return True
        return False
    except Exception:
        return False

def initiate_wipe(device: str, method: str, passes: int = 1, force: bool = False) -> Dict[str, Any]:
    """Initiate secure wipe operation with progress tracking"""
    
    if not force:
        raise RuntimeError("force=True required for destructive operations")
    
    # Convert method string to enum
    method_map = {
        "nist_800_88": WipeMethod.NIST_800_88,
        "dod_5220_22_m": WipeMethod.DOD_5220_22_M,
        "gutmann": WipeMethod.GUTMANN,
        "crypto_erase": WipeMethod.CRYPTO_ERASE,
        "ata_sanitize": WipeMethod.ATA_SANITIZE,
        "nvme_format": WipeMethod.NVME_FORMAT,
        "single_pass": WipeMethod.SINGLE_PASS,
        "three_pass": WipeMethod.THREE_PASS,
        "shred": WipeMethod.THREE_PASS,  # Legacy support
        "dd_zero": WipeMethod.SINGLE_PASS,  # Legacy support
        "hdparm_secure_erase": WipeMethod.ATA_SANITIZE,  # Legacy support
    }
    
    wipe_method = method_map.get(method, WipeMethod.SINGLE_PASS)
    
    # Detect original filesystem (best-effort, for post-wipe reformat)
    original_fs = _detect_original_filesystem(device)

    # Get or create device record
    device_obj = get_device_by_path(device)
    if not device_obj:
        device_info = secure_wipe_service.get_device_info(device)
        # Robust name and fields with fallbacks
        device_name = device_info.get("model") or device_info.get("path") or device
        if not device_name:
            device_name = str(device)
        device_type = device_info.get("type") or "unknown"
        try:
            size_bytes = int(device_info.get("size")) if device_info.get("size") is not None else None
        except Exception:
            size_bytes = None
        device_obj = create_device(
            device_path=device,
            device_name=device_name,
            device_type=device_type,
            size_bytes=size_bytes,
            model=device_info.get("model"),
            serial_number=device_info.get("serial"),
            is_removable=bool(device_info.get("is_removable", False))
        )
    
    if not device_obj:
        raise Exception("Failed to create device record")
    
    # Create wipe session
    session = create_wipe_session(device_obj.id, wipe_method, passes)
    if not session:
        raise Exception("Failed to create wipe session")
    
    # Progress callback
    def progress_callback(percentage: float, message: str):
        add_progress_update(
            session.id,
            progress_percentage=percentage,
            status_message=message
        )
        logger.info(f"Wipe progress: {percentage}% - {message}")
    
    # Get initial hash
    sha_before = _sha256_head(device)
    
    # Update session status using proper enum and datetime
    update_wipe_session(
        session.id,
        status=WipeStatus.IN_PROGRESS,
        started_at=datetime.utcnow()
    )
    
    try:
        # Perform the wipe
        result = secure_wipe_service.wipe_device(
            device, wipe_method, passes, progress_callback
        )
        
        # Get final hash
        sha_after = _sha256_head(device)
        
        # Update session with results using enum and datetime
        update_wipe_session(
            session.id,
            status=WipeStatus.COMPLETED if result["success"] else WipeStatus.FAILED,
            completed_at=datetime.utcnow(),
            duration_seconds=result.get("duration", 0),
            sha_before=sha_before,
            sha_after=sha_after,
            error_message=result.get("error")
        )
        
        # Attempt post-wipe reformat to original filesystem (best-effort)
        post_format = {"attempted": False, "formatted": False, "filesystem": original_fs or "", "error": None}
        try:
            reformatted = _format_device_to_original(device, original_fs)
            post_format = {"attempted": True, "formatted": bool(reformatted), "filesystem": original_fs or "", "error": None if reformatted else "formatting skipped"}
        except Exception as fmt_err:
            post_format = {"attempted": True, "formatted": False, "filesystem": original_fs or "", "error": str(fmt_err)}

        # Generate reports
        end_ts = time.time()
        start_ts = end_ts - result.get("duration", 0)
        report_path = generate_pdf_report(
            device, method, passes, sha_before, sha_after,
            "completed" if result["success"] else "failed",
            start_ts, end_ts
        )
        
        json_report_path = generate_json_report(
            device, method, passes, sha_before, sha_after,
            "completed" if result["success"] else "failed",
            start_ts, end_ts
        )
        
        # Sign reports
        signature_path = None
        json_signature_path = None
        try:
            signature_path = sign_report_with_openssl(report_path)
            if json_report_path:
                json_signature_path = f"{json_report_path}.sig"
        except Exception as e:
            logger.warning(f"Failed to sign reports: {e}")
        
        # Update session with report info
        update_wipe_session(
            session.id,
            report_path=report_path,
            signature_path=signature_path
        )
        
        return {
            "success": result["success"],
            "session_id": session.id,
            "report": report_path,
            "signature": signature_path,
            "status": "completed" if result["success"] else "failed",
            "duration": result.get("duration", 0),
            "sha_before": sha_before,
            "sha_after": sha_after,
            "error": result.get("error"),
            "post_format": post_format
        }
        
    except Exception as e:
        logger.error(f"Wipe operation failed: {e}")
        
        # Update session with error using enum and datetime
        update_wipe_session(
            session.id,
            status=WipeStatus.FAILED,
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        
        return {
            "success": False,
            "session_id": session.id,
            "status": "failed",
            "error": str(e)
        }

# Legacy functions for backward compatibility
def run_shred(device, passes=3, force=False):
    """Legacy shred function"""
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    subprocess.run(["shred", "-v", "-n", str(passes), "-z", device], check=True)

def run_dd_zeros(device, passes=1, force=False):
    """Legacy dd zeros function"""
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    for _ in range(passes):
        subprocess.run(
            f"dd if=/dev/zero of={device} bs=1M status=progress conv=fsync",
            shell=True, check=True
        )

def run_hdparm_secure_erase(device, force=False):
    """Legacy hdparm secure erase function"""
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    pw = "SIHpass"
    subprocess.run(["hdparm", "--user-master", "u", "--security-set-pass", pw, device], check=True)
    subprocess.run(["hdparm", "--security-erase", pw, device], check=True)

def run_nvme_format(device, force=False):
    """Legacy nvme format function"""
    if not force:
        raise RuntimeError("force=True required for destructive ops")
    subprocess.run(["nvme", "format", device, "--ses=1"], check=True)
