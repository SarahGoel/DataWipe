"""
Secure Wipe Service - NIST 800-88 Compliant Data Erasure
"""

import os
import time
import hashlib
import subprocess
import platform
import secrets
from typing import Optional, Dict, Any, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WipeMethod(Enum):
    NIST_800_88 = "nist_800_88"
    DOD_5220_22_M = "dod_5220_22_m"
    GUTMANN = "gutmann"
    CRYPTO_ERASE = "crypto_erase"
    ATA_SANITIZE = "ata_sanitize"
    NVME_FORMAT = "nvme_format"
    SINGLE_PASS = "single_pass"
    THREE_PASS = "three_pass"

class SecureWipeService:
    """Main service for secure data wiping operations"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_linux = self.system == "linux"
        self.is_macos = self.system == "darwin"
        
    def detect_device_type(self, device_path: str) -> str:
        """Detect device type (HDD, SSD, NVMe, USB)"""
        try:
            if self.is_linux:
                return self._detect_linux_device_type(device_path)
            elif self.is_windows:
                return self._detect_windows_device_type(device_path)
            elif self.is_macos:
                return self._detect_macos_device_type(device_path)
        except Exception as e:
            logger.error(f"Failed to detect device type: {e}")
        return "unknown"
    
    def _detect_linux_device_type(self, device_path: str) -> str:
        """Detect device type on Linux"""
        try:
            if "nvme" in device_path:
                return "nvme"
            
            result = subprocess.run(
                ["lsblk", "-d", "-o", "NAME,ROTA", device_path],
                capture_output=True, text=True, check=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    rota = lines[1].split()[-1]
                    return "ssd" if rota == "0" else "hdd"
            
            return "unknown"
        except Exception as e:
            logger.error(f"Linux device type detection failed: {e}")
            return "unknown"
    
    def _detect_windows_device_type(self, device_path: str) -> str:
        """Detect device type on Windows"""
        try:
            device_id = device_path.split('\\')[-1]
            cmd = f"""
            Get-PhysicalDisk | Where-Object {{ $_.DeviceID -eq '{device_id}' }} | 
            Select-Object MediaType, BusType
            """
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True, text=True, check=True
            )
            
            if "SSD" in result.stdout:
                return "ssd"
            elif "HDD" in result.stdout:
                return "hdd"
            elif "NVMe" in result.stdout:
                return "nvme"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"Windows device type detection failed: {e}")
            return "unknown"
    
    def _detect_macos_device_type(self, device_path: str) -> str:
        """Detect device type on macOS"""
        try:
            result = subprocess.run(
                ["system_profiler", "SPStorageDataType"],
                capture_output=True, text=True, check=True
            )
            
            if "Solid State" in result.stdout:
                return "ssd"
            elif "Rotational" in result.stdout:
                return "hdd"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"macOS device type detection failed: {e}")
            return "unknown"
    
    def get_device_info(self, device_path: str) -> Dict[str, Any]:
        """Get comprehensive device information"""
        info = {
            "path": device_path,
            "type": self.detect_device_type(device_path),
            "size": self._get_device_size(device_path),
            "model": self._get_device_model(device_path),
            "serial": self._get_device_serial(device_path),
            "is_removable": self._is_removable_device(device_path)
        }
        return info
    
    def _get_device_size(self, device_path: str) -> Optional[int]:
        """Get device size in bytes"""
        try:
            if self.is_linux:
                result = subprocess.run(
                    ["blockdev", "--getsize64", device_path],
                    capture_output=True, text=True, check=True
                )
                return int(result.stdout.strip())
            elif self.is_windows:
                # Windows implementation
                pass
        except Exception as e:
            logger.error(f"Failed to get device size: {e}")
        return None
    
    def _get_device_model(self, device_path: str) -> Optional[str]:
        """Get device model"""
        try:
            if self.is_linux:
                result = subprocess.run(
                    ["lsblk", "-d", "-o", "MODEL", device_path],
                    capture_output=True, text=True, check=True
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
        except Exception as e:
            logger.error(f"Failed to get device model: {e}")
        return None
    
    def _get_device_serial(self, device_path: str) -> Optional[str]:
        """Get device serial number"""
        try:
            if self.is_linux:
                result = subprocess.run(
                    ["lsblk", "-d", "-o", "SERIAL", device_path],
                    capture_output=True, text=True, check=True
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
        except Exception as e:
            logger.error(f"Failed to get device serial: {e}")
        return None
    
    def _is_removable_device(self, device_path: str) -> bool:
        """Check if device is removable"""
        try:
            if self.is_linux:
                result = subprocess.run(
                    ["lsblk", "-d", "-o", "RM", device_path],
                    capture_output=True, text=True, check=True
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip() == "1"
        except Exception as e:
            logger.error(f"Failed to check if device is removable: {e}")
        return False
    
    def wipe_device(self, device_path: str, method: WipeMethod, 
                   passes: int = 1, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Main method to wipe a device using specified method"""
        
        if not os.path.exists(device_path):
            raise FileNotFoundError(f"Device {device_path} not found")
        
        device_type = self.detect_device_type(device_path)
        logger.info(f"Starting wipe of {device_path} using {method.value} method")
        
        # Get initial hash
        sha_before = self._get_device_hash(device_path)
        
        start_time = time.time()
        
        try:
            if method == WipeMethod.CRYPTO_ERASE:
                result = self._crypto_erase(device_path, device_type, progress_callback)
            elif method == WipeMethod.ATA_SANITIZE:
                result = self._ata_sanitize(device_path, progress_callback)
            elif method == WipeMethod.NVME_FORMAT:
                result = self._nvme_format(device_path, progress_callback)
            elif method == WipeMethod.NIST_800_88:
                result = self._nist_800_88_wipe(device_path, passes, progress_callback)
            elif method == WipeMethod.DOD_5220_22_M:
                result = self._dod_5220_22_m_wipe(device_path, passes, progress_callback)
            elif method == WipeMethod.GUTMANN:
                result = self._gutmann_wipe(device_path, progress_callback)
            elif method == WipeMethod.SINGLE_PASS:
                result = self._single_pass_wipe(device_path, progress_callback)
            elif method == WipeMethod.THREE_PASS:
                result = self._three_pass_wipe(device_path, progress_callback)
            else:
                raise ValueError(f"Unsupported wipe method: {method}")
            
            end_time = time.time()
            sha_after = self._get_device_hash(device_path)
            
            return {
                "success": True,
                "method": method.value,
                "device_path": device_path,
                "device_type": device_type,
                "passes": passes,
                "duration": end_time - start_time,
                "sha_before": sha_before,
                "sha_after": sha_after,
                "result": result
            }
            
        except Exception as e:
            end_time = time.time()
            logger.error(f"Wipe failed: {e}")
            return {
                "success": False,
                "method": method.value,
                "device_path": device_path,
                "device_type": device_type,
                "passes": passes,
                "duration": end_time - start_time,
                "sha_before": sha_before,
                "sha_after": None,
                "error": str(e)
            }
    
    def _get_device_hash(self, device_path: str, size: int = 1024 * 1024) -> Optional[str]:
        """Get SHA-256 hash of device (first 1MB)"""
        try:
            hash_obj = hashlib.sha256()
            with open(device_path, "rb") as f:
                data = f.read(size)
                hash_obj.update(data)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to get device hash: {e}")
            return None

# Global instance
secure_wipe_service = SecureWipeService()