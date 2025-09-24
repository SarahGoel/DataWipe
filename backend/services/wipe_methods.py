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
        
        # Step 3: Purge (prefer sanitize/crypto erase on SSD/NVMe; fallback overwrite; try discard)
        if progress_callback:
            progress_callback(80, "Purging device...")
        
        try:
            # Detect device type best-effort
            device_type = self._detect_device_type_best_effort(device_path)
            # Try crypto/sanitize erase first
            self.crypto_erase(device_path, device_type, None)
            if progress_callback:
                progress_callback(100, "NIST 800-88 wipe completed (crypto erase)")
        except:
            # Fallback to additional overwrite
            self._secure_overwrite(device_path, 1, progress_callback, offset=80, max_progress=95)
            # Best-effort discard/TRIM for SSDs
            try:
                if device_type in ("ssd", "nvme"):
                    if progress_callback:
                        progress_callback(96, "Attempting discard/TRIM...")
                    self._try_discard(device_path)
            except Exception:
                pass
            if progress_callback:
                progress_callback(100, "NIST 800-88 wipe completed (overwrite)")
        
        return {"method": "nist_800_88", "success": True}

    def _detect_device_type_best_effort(self, device_path: str) -> str:
        """Lightweight device type detection without cross-service dependency."""
        try:
            if self.is_linux:
                if "nvme" in device_path:
                    return "nvme"
                out = subprocess.run(["lsblk", "-d", "-o", "ROTA", device_path], capture_output=True, text=True)
                if out.returncode == 0:
                    lines = (out.stdout or "").strip().splitlines()
                    if lines:
                        rota = lines[-1].strip()
                        return "ssd" if rota == "0" else "hdd"
            elif self.is_macos:
                if "nvme" in device_path.lower():
                    return "nvme"
                info = subprocess.run(["diskutil", "info", device_path], capture_output=True, text=True)
                if info.returncode == 0 and "Solid State" in (info.stdout or ""):
                    return "ssd"
            elif self.is_windows:
                if "physicaldrive" in device_path.lower():
                    # Unable to reliably detect here; assume ssd unknown
                    return "unknown"
        except Exception:
            pass
        return "unknown"

    def _try_discard(self, device_path: str) -> None:
        """Best-effort discard/trim to inform SSD/NVMe the blocks are unused."""
        try:
            if self.is_linux:
                # blkdiscard may require exclusive access
                subprocess.run(["blkdiscard", "-f", device_path], check=False)
            elif self.is_macos:
                # macOS performs TRIM internally on erase; no direct tool commonly available
                pass
            elif self.is_windows:
                # Windows TRIM is FS-level; for raw device there is no simple direct call here
                pass
        except Exception:
            # best-effort only
            pass
    
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
        """Secure overwrite by streaming zeros across the entire target."""
        try:
            import ctypes, re
            chunk_size = 16 * 1024 * 1024
            zero_chunk = b"\x00" * chunk_size
            for pass_num in range(passes):
                if progress_callback:
                    progress_callback(
                        offset + (pass_num * (max_progress - offset) // passes),
                        f"Overwrite pass {pass_num + 1}/{passes}..."
                    )
                if self.is_windows:
                    lower_path = device_path.lower()
                    is_physical = 'physicaldrive' in lower_path
                    try:
                        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore
                    except Exception:
                        is_admin = False
                    if not is_admin:
                        raise Exception("Administrator privileges are required on Windows.")
                    if is_physical:
                        # Use DiskPart 'clean all' to write zeros to entire disk
                        m = re.search(r"PhysicalDrive(\d+)", device_path, re.IGNORECASE)
                        if not m:
                            raise Exception("Unable to parse Windows PhysicalDrive number.")
                        disk_number = m.group(1)
                        script = f"select disk {disk_number}\nclean all\n"
                        subprocess.run([
                            "powershell", "-NoProfile", "-Command",
                            f"$tmp=[System.IO.Path]::GetTempFileName(); Set-Content -Path $tmp -Value @'\n{script}\n'@; diskpart /s $tmp | Out-Null; Remove-Item $tmp -Force"
                        ], check=True)
                    else:
                        # Reject drive-letter/volume path to avoid partial clearing
                        raise Exception("On Windows, provide \\ \\.\\PhysicalDriveN for full-device secure wipe.")
                else:
                    # POSIX: stream zeros until EOF
                    with open(device_path, 'wb', buffering=0) as f:
                        while True:
                            try:
                                written = f.write(zero_chunk)
                                if not written:
                                    break
                                f.flush()
                                os.fsync(f.fileno())
                            except OSError:
                                break
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
        """Write random data across the entire target by streaming chunks."""
        try:
            chunk_size = 16 * 1024 * 1024
            if self.is_windows:
                device_path_escaped = device_path.replace('\\', '\\\\')
                cmd = (
                    "$fs = [System.IO.File]::Open('{path}', [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite)\n"
                    "$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()\n"
                    "$buffer = New-Object byte[] {size}\n"
                    "while ($true) {{\n"
                    "  $rng.GetBytes($buffer)\n"
                    "  try {{ $fs.Write($buffer, 0, $buffer.Length) }} catch {{ break }}\n"
                    "  $fs.Flush(); $fs.Flush(true)\n"
                    "}}\n"
                    "$fs.Close()\n"
                ).format(path=device_path_escaped, size=chunk_size)
                subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)
            else:
                with open(device_path, 'wb', buffering=0) as f:
                    while True:
                        data = os.urandom(chunk_size)
                        try:
                            written = f.write(data)
                            if not written:
                                break
                            f.flush()
                            os.fsync(f.fileno())
                        except OSError:
                            break
        except subprocess.CalledProcessError as e:
            raise Exception(f"Random data write failed: {e}")
    
    def _write_specific_pattern(self, device_path: str, pattern: bytes,
                               progress_callback: Optional[Callable] = None,
                               offset: int = 0, max_progress: int = 100) -> None:
        """Write specific pattern across the entire target by streaming repeated buffers."""
        try:
            chunk_size = 16 * 1024 * 1024
            if len(pattern) == 0:
                raise Exception("Pattern must be non-empty")
            repeats = (chunk_size // len(pattern)) + 1
            chunk = (pattern * repeats)[:chunk_size]
            if self.is_windows:
                device_path_escaped = device_path.replace('\\', '\\\\')
                pattern_hex = chunk.hex()
                cmd = (
                    "$fs = [System.IO.File]::Open('{path}', [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite)\n"
                    "$buffer = [System.Convert]::FromHexString('{hex}')\n"
                    "while ($true) {{\n"
                    "  try {{ $fs.Write($buffer, 0, $buffer.Length) }} catch {{ break }}\n"
                    "  $fs.Flush(); $fs.Flush(true)\n"
                    "}}\n"
                    "$fs.Close()\n"
                ).format(path=device_path_escaped, hex=pattern_hex)
                subprocess.run(["powershell", "-NoProfile", "-Command", cmd], check=True)
            else:
                with open(device_path, 'wb', buffering=0) as f:
                    while True:
                        try:
                            written = f.write(chunk)
                            if not written:
                                break
                            f.flush()
                            os.fsync(f.fileno())
                        except OSError:
                            break
        except subprocess.CalledProcessError as e:
            raise Exception(f"Pattern write failed: {e}")
    
    def _verify_zeroed(self, device_path: str) -> bool:
        """Verify multiple sampled regions are zeroed (head, middle, tail)."""
        try:
            sample_size = 1024 * 1024
            file_size = None
            try:
                file_size = os.path.getsize(device_path)
            except Exception:
                file_size = None
            def _check_region(offset_bytes: int) -> bool:
                try:
                    with open(device_path, 'rb') as f:
                        if offset_bytes > 0:
                            f.seek(offset_bytes)
                        data = f.read(sample_size)
                        if not data:
                            return True
                        return all(b == 0 for b in data)
                except Exception:
                    return False
            offsets = [0]
            if file_size and file_size > sample_size * 2:
                offsets.append(max(0, file_size // 2))
                offsets.append(max(0, file_size - sample_size))
            return all(_check_region(o) for o in offsets)
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
