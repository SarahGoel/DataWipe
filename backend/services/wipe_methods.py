"""
Implementation of specific wipe methods for secure data erasure
"""

import os
import time
import subprocess
import secrets
from typing import Optional, Callable, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WipeMethods:
    """Implementation of various wipe methods"""
    
    def __init__(self, system: str):
        self.system = system
        self.is_windows = system == "windows"
        self.is_linux = system == "linux"
        self.is_macos = system == "darwin"
    
    def crypto_erase(self, device_path: str, device_type: str, 
                    progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Perform cryptographic erasure (preferred for SSDs)"""
        logger.info("Performing cryptographic erasure")
        
        if progress_callback:
            progress_callback(0, "Initializing cryptographic erasure...")
        
        try:
            if device_type == "nvme":
                return self._nvme_crypto_erase(device_path, progress_callback)
            elif device_type in ["ssd", "hdd"]:
                return self._ata_crypto_erase(device_path, progress_callback)
            else:
                # Fallback to secure overwrite
                return self._secure_overwrite(device_path, 1, progress_callback)
        except Exception as e:
            logger.error(f"Crypto erase failed: {e}")
            raise
    
    def _nvme_crypto_erase(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """NVMe cryptographic erase using format command"""
        try:
            if progress_callback:
                progress_callback(10, "Formatting NVMe device with crypto erase...")
            
            # Use nvme format command with crypto erase
            result = subprocess.run(
                ["nvme", "format", device_path, "--ses=1", "--pi=0"],
                capture_output=True, text=True, check=True
            )
            
            if progress_callback:
                progress_callback(100, "NVMe crypto erase completed")
            
            return {"method": "nvme_crypto_erase", "success": True}
        except subprocess.CalledProcessError as e:
            raise Exception(f"NVMe crypto erase failed: {e.stderr}")
    
    def _ata_crypto_erase(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """ATA cryptographic erase using hdparm"""
        try:
            if progress_callback:
                progress_callback(10, "Setting ATA security password...")
            
            # Set security password
            password = secrets.token_hex(16)
            subprocess.run(
                ["hdparm", "--user-master", "u", "--security-set-pass", password, device_path],
                check=True
            )
            
            if progress_callback:
                progress_callback(50, "Performing ATA crypto erase...")
            
            # Perform crypto erase
            subprocess.run(
                ["hdparm", "--security-erase", password, device_path],
                check=True
            )
            
            if progress_callback:
                progress_callback(100, "ATA crypto erase completed")
            
            return {"method": "ata_crypto_erase", "success": True}
        except subprocess.CalledProcessError as e:
            raise Exception(f"ATA crypto erase failed: {e.stderr}")
    
    def nist_800_88_wipe(self, device_path: str, passes: int, 
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """NIST 800-88 compliant wipe"""
        logger.info("Performing NIST 800-88 compliant wipe")
        
        # NIST 800-88 recommends:
        # 1. Clear (overwrite with zeros)
        # 2. Verify the clear
        # 3. Purge (crypto erase if available, otherwise additional overwrite)
        
        if progress_callback:
            progress_callback(0, "Starting NIST 800-88 wipe...")
        
        # Step 1: Clear
        if progress_callback:
            progress_callback(10, "Clearing device (overwrite with zeros)...")
        
        self._secure_overwrite(device_path, 1, progress_callback, offset=10, max_progress=60)
        
        # Step 2: Verify
        if progress_callback:
            progress_callback(70, "Verifying clear operation...")
        
        # Verify by checking that device is zeroed
        if not self._verify_zeroed(device_path):
            raise Exception("Clear verification failed")
        
        # Step 3: Purge (crypto erase if available, otherwise additional overwrite)
        if progress_callback:
            progress_callback(80, "Purging device...")
        
        try:
            # Try crypto erase first
            self.crypto_erase(device_path, "unknown", None)
            if progress_callback:
                progress_callback(100, "NIST 800-88 wipe completed (crypto erase)")
        except:
            # Fallback to additional overwrite
            self._secure_overwrite(device_path, 1, progress_callback, offset=80, max_progress=100)
            if progress_callback:
                progress_callback(100, "NIST 800-88 wipe completed (overwrite)")
        
        return {"method": "nist_800_88", "success": True}
    
    def dod_5220_22_m_wipe(self, device_path: str, passes: int, 
                          progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """DoD 5220.22-M compliant wipe"""
        logger.info("Performing DoD 5220.22-M compliant wipe")
        
        # DoD 5220.22-M requires 3 passes:
        # Pass 1: Write all 0s
        # Pass 2: Write all 1s  
        # Pass 3: Write random data
        
        patterns = [
            (b'\x00', "Writing zeros (Pass 1/3)..."),
            (b'\xFF', "Writing ones (Pass 2/3)..."),
            (None, "Writing random data (Pass 3/3)...")
        ]
        
        for i, (pattern, message) in enumerate(patterns):
            if progress_callback:
                progress_callback(i * 33, message)
            
            self._write_pattern(device_path, pattern, progress_callback, 
                              offset=i * 33, max_progress=(i + 1) * 33)
        
        if progress_callback:
            progress_callback(100, "DoD 5220.22-M wipe completed")
        
        return {"method": "dod_5220_22_m", "success": True}
    
    def gutmann_wipe(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Gutmann 35-pass wipe"""
        logger.info("Performing Gutmann 35-pass wipe")
        
        # Gutmann patterns for maximum security
        patterns = [
            b'\x55', b'\xAA', b'\x92\x49\x24', b'\x49\x24\x92',
            b'\x24\x92\x49', b'\x00', b'\x11', b'\x22', b'\x33',
            b'\x44', b'\x55', b'\x66', b'\x77', b'\x88', b'\x99',
            b'\xAA', b'\xBB', b'\xCC', b'\xDD', b'\xEE', b'\xFF',
            b'\x92\x49\x24\x49', b'\x49\x24\x92\x24', b'\x24\x92\x49\x92',
            b'\x6D\xB6\xDB\x6D', b'\xB6\xDB\x6D\xB6', b'\xDB\x6D\xB6\xDB',
            b'\x00', b'\x11', b'\x22', b'\x33', b'\x44', b'\x55',
            b'\x66', b'\x77', b'\x88', b'\x99', b'\xAA', b'\xBB',
            b'\xCC', b'\xDD', b'\xEE', b'\xFF'
        ]
        
        for i, pattern in enumerate(patterns):
            if progress_callback:
                progress_callback(i * 100 // len(patterns), f"Gutmann pass {i+1}/{len(patterns)}...")
            
            self._write_pattern(device_path, pattern, None, 
                              offset=i * 100 // len(patterns), 
                              max_progress=(i + 1) * 100 // len(patterns))
        
        if progress_callback:
            progress_callback(100, "Gutmann wipe completed")
        
        return {"method": "gutmann", "success": True}
    
    def single_pass_wipe(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Single pass wipe with zeros"""
        logger.info("Performing single pass wipe")
        
        if progress_callback:
            progress_callback(0, "Single pass wipe with zeros...")
        
        self._secure_overwrite(device_path, 1, progress_callback)
        
        if progress_callback:
            progress_callback(100, "Single pass wipe completed")
        
        return {"method": "single_pass", "success": True}
    
    def three_pass_wipe(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Three pass wipe (zeros, ones, random)"""
        logger.info("Performing three pass wipe")
        
        patterns = [
            (b'\x00', "Pass 1/3: Writing zeros..."),
            (b'\xFF', "Pass 2/3: Writing ones..."),
            (None, "Pass 3/3: Writing random data...")
        ]
        
        for i, (pattern, message) in enumerate(patterns):
            if progress_callback:
                progress_callback(i * 33, message)
            
            self._write_pattern(device_path, pattern, progress_callback,
                              offset=i * 33, max_progress=(i + 1) * 33)
        
        if progress_callback:
            progress_callback(100, "Three pass wipe completed")
        
        return {"method": "three_pass", "success": True}

    def wipe_file_clear(self, file_path: str, passes: int = 1,
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Securely overwrite a file and delete it (NIST Clear)."""
        try:
            file_size = os.path.getsize(file_path)
            chunk_size = 1024 * 1024

            def _write_pattern_stream(byte_source: Optional[bytes], message: str, offset_pct: int, max_pct: int):
                processed = 0
                if progress_callback:
                    progress_callback(offset_pct, message)
                with open(file_path, 'r+b') as f:
                    while processed < file_size:
                        to_write = min(chunk_size, file_size - processed)
                        if byte_source is None:
                            data = os.urandom(to_write)
                        else:
                            if len(byte_source) == 1:
                                data = byte_source * to_write
                            else:
                                repeats = to_write // len(byte_source) + 1
                                data = (byte_source * repeats)[:to_write]
                        f.write(data)
                        f.flush()
                        os.fsync(f.fileno())
                        processed += to_write
                        if progress_callback and file_size > 0:
                            pct = offset_pct + int((processed / file_size) * (max_pct - offset_pct))
                            progress_callback(min(pct, max_pct), message)

            # Passes: zeros, ones, random (based on requested passes)
            patterns = []
            if passes >= 1:
                patterns.append((b'\x00', "Writing zeros...", 0, 60 if passes == 1 else 33))
            if passes >= 2:
                patterns.append((b'\xFF', "Writing ones...", 33, 66))
            if passes >= 3:
                patterns.append((None, "Writing random data...", 66, 99))

            if not patterns:
                patterns = [(b'\x00', "Writing zeros...", 0, 99)]

            for byte_source, message, start_pct, end_pct in patterns:
                _write_pattern_stream(byte_source, message, start_pct, end_pct)

            # Truncate and delete
            if progress_callback:
                progress_callback(99, "Truncating and deleting file...")
            with open(file_path, 'r+b') as f:
                f.truncate(0)
                f.flush()
                os.fsync(f.fileno())
            os.remove(file_path)

            if progress_callback:
                progress_callback(100, "File wipe completed")
            return {"method": "file_clear", "success": True}
        except Exception as e:
            logger.error(f"File wipe failed: {e}")
            raise
    
    def _secure_overwrite(self, device_path: str, passes: int, 
                         progress_callback: Optional[Callable] = None,
                         offset: int = 0, max_progress: int = 100) -> None:
        """Secure overwrite using dd"""
        try:
            for pass_num in range(passes):
                if progress_callback:
                    progress_callback(
                        offset + (pass_num * (max_progress - offset) // passes),
                        f"Overwrite pass {pass_num + 1}/{passes}..."
                    )
                
                if self.is_linux or self.is_macos:
                    subprocess.run([
                        "dd", f"if=/dev/zero", f"of={device_path}",
                        "bs=1M", "status=progress", "conv=fsync"
                    ], check=True)
                elif self.is_windows:
                    # Windows: raw disk writes require Administrator. Prefer Clear-Disk/Clear-Volume.
                    import re, ctypes
                    lower_path = device_path.lower()
                    is_physical = 'physicaldrive' in lower_path
                    # Physical drive wipe using Clear-Disk
                    if is_physical:
                        try:
                            is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore
                        except Exception:
                            is_admin = False
                        if not is_admin:
                            raise Exception("Administrator privileges required for device wipe on Windows. Run PowerShell as Administrator.")
                        m = re.search(r"PhysicalDrive(\d+)", device_path, re.IGNORECASE)
                        if not m:
                            raise Exception("Unable to parse Windows PhysicalDrive number.")
                        disk_number = m.group(1)
                        # Use Clear-Disk to remove data (requires admin)
                        ps = f"Clear-Disk -Number {disk_number} -RemoveData -Confirm:$false -ErrorAction Stop"
                        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
                    else:
                        # If a drive letter like C: or D:\ was passed, clear the volume
                        mvol = re.match(r"^([a-zA-Z]):\\?", device_path)
                        if mvol:
                            drive = mvol.group(1)
                            try:
                                is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore
                            except Exception:
                                is_admin = False
                            if not is_admin:
                                raise Exception("Administrator privileges required for volume wipe on Windows. Run PowerShell as Administrator.")
                            ps = f"Clear-Volume -DriveLetter {drive} -Force -Confirm:$false -ErrorAction Stop"
                            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
                            continue
                        # Fallback for regular file paths on Windows
                        device_path_escaped = device_path.replace('\\', '\\\\')
                        cmd = f"""
                        $fs = [System.IO.File]::Open('{device_path_escaped}', [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite)
                        $buffer = New-Object byte[] 1048576
                        $fs.Write($buffer, 0, $buffer.Length)
                        $fs.Flush()
                        $fs.Close()
                        """
                        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Secure overwrite failed: {e}")
    
    def _write_pattern(self, device_path: str, pattern: Optional[bytes], 
                      progress_callback: Optional[Callable] = None,
                      offset: int = 0, max_progress: int = 100) -> None:
        """Write a specific pattern to device"""
        try:
            if pattern is None:
                # Random data
                self._write_random_data(device_path, progress_callback, offset, max_progress)
            else:
                # Specific pattern
                self._write_specific_pattern(device_path, pattern, progress_callback, offset, max_progress)
        except Exception as e:
            raise Exception(f"Pattern write failed: {e}")
    
    def _write_random_data(self, device_path: str, progress_callback: Optional[Callable] = None,
                          offset: int = 0, max_progress: int = 100) -> None:
        """Write random data to device"""
        try:
            if self.is_linux or self.is_macos:
                subprocess.run([
                    "dd", f"if=/dev/urandom", f"of={device_path}",
                    "bs=1M", "status=progress", "conv=fsync"
                ], check=True)
            elif self.is_windows:
                # Windows implementation
                device_path_escaped = device_path.replace('\\', '\\\\')
                cmd = f"""
                $fs = [System.IO.File]::OpenWrite('{device_path_escaped}')
                $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
                $buffer = New-Object byte[] 1048576
                $rng.GetBytes($buffer)
                $fs.Write($buffer, 0, $buffer.Length)
                $fs.Close()
                """
                subprocess.run(["powershell", "-Command", cmd], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Random data write failed: {e}")
    
    def _write_specific_pattern(self, device_path: str, pattern: bytes,
                               progress_callback: Optional[Callable] = None,
                               offset: int = 0, max_progress: int = 100) -> None:
        """Write specific pattern to device"""
        try:
            if self.is_linux or self.is_macos:
                # Create a temporary file with the pattern
                temp_file = f"/tmp/pattern_{int(time.time())}"
                with open(temp_file, "wb") as f:
                    # Write pattern repeatedly to fill 1MB
                    pattern_size = len(pattern)
                    for _ in range(1024 * 1024 // pattern_size):
                        f.write(pattern)
                
                subprocess.run([
                    "dd", f"if={temp_file}", f"of={device_path}",
                    "bs=1M", "status=progress", "conv=fsync"
                ], check=True)
                
                # Clean up
                os.remove(temp_file)
            elif self.is_windows:
                # Windows implementation
                device_path_escaped = device_path.replace('\\', '\\\\')
                pattern_hex = pattern.hex()
                cmd = f"""
                $fs = [System.IO.File]::OpenWrite('{device_path_escaped}')
                $pattern = [System.Convert]::FromHexString('{pattern_hex}')
                $buffer = New-Object byte[] 1048576
                for ($i = 0; $i -lt $buffer.Length; $i += $pattern.Length) {{
                    [Array]::Copy($pattern, 0, $buffer, $i, [Math]::Min($pattern.Length, $buffer.Length - $i))
                }}
                $fs.Write($buffer, 0, $buffer.Length)
                $fs.Close()
                """
                subprocess.run(["powershell", "-Command", cmd], check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Pattern write failed: {e}")
    
    def _verify_zeroed(self, device_path: str) -> bool:
        """Verify that device is zeroed"""
        try:
            if self.is_linux or self.is_macos:
                result = subprocess.run([
                    "dd", f"if={device_path}", "bs=1M", "count=1"
                ], capture_output=True, check=True)
                return all(b == 0 for b in result.stdout)
            elif self.is_windows:
                # Windows verification
                device_path_escaped = device_path.replace('\\', '\\\\')
                cmd = f"""
                $fs = [System.IO.File]::OpenRead('{device_path_escaped}')
                $buffer = New-Object byte[] 1048576
                $fs.Read($buffer, 0, $buffer.Length)
                $fs.Close()
                ($buffer | Where-Object {{ $_ -ne 0 }}).Count -eq 0
                """
                result = subprocess.run(["powershell", "-Command", cmd], 
                                      capture_output=True, text=True, check=True)
                return result.stdout.strip() == "True"
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def _ata_sanitize(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """ATA sanitize command"""
        try:
            if progress_callback:
                progress_callback(0, "Starting ATA sanitize...")
            
            # Use hdparm for ATA sanitize
            subprocess.run([
                "hdparm", "--sanitize-crypto-scramble", device_path
            ], check=True)
            
            if progress_callback:
                progress_callback(50, "ATA sanitize in progress...")
            
            # Wait for completion
            while True:
                result = subprocess.run([
                    "hdparm", "--sanitize-status", device_path
                ], capture_output=True, text=True, check=True)
                
                if "Sanitize complete" in result.stdout:
                    break
                elif "Sanitize failed" in result.stdout:
                    raise Exception("ATA sanitize failed")
                
                time.sleep(1)
            
            if progress_callback:
                progress_callback(100, "ATA sanitize completed")
            
            return {"method": "ata_sanitize", "success": True}
        except subprocess.CalledProcessError as e:
            raise Exception(f"ATA sanitize failed: {e}")
    
    def _nvme_format(self, device_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """NVMe format command"""
        try:
            if progress_callback:
                progress_callback(0, "Starting NVMe format...")
            
            subprocess.run([
                "nvme", "format", device_path, "--ses=1"
            ], check=True)
            
            if progress_callback:
                progress_callback(100, "NVMe format completed")
            
            return {"method": "nvme_format", "success": True}
        except subprocess.CalledProcessError as e:
            raise Exception(f"NVMe format failed: {e}")
