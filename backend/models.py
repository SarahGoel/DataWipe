from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class WipeMethod(enum.Enum):
    NIST_800_88 = "nist_800_88"
    DOD_5220_22_M = "dod_5220_22_m"
    GUTMANN = "gutmann"
    CRYPTO_ERASE = "crypto_erase"
    ATA_SANITIZE = "ata_sanitize"
    NVME_FORMAT = "nvme_format"
    SINGLE_PASS = "single_pass"
    THREE_PASS = "three_pass"

class DeviceType(enum.Enum):
    HDD = "hdd"
    SSD = "ssd"
    USB = "usb"
    NVME = "nvme"
    UNKNOWN = "unknown"

class WipeStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_path = Column(String(255), unique=True, index=True, nullable=False)
    device_name = Column(String(255), nullable=False)
    device_type = Column(Enum(DeviceType), default=DeviceType.UNKNOWN)
    size_bytes = Column(Integer, nullable=True)
    model = Column(String(255), nullable=True)
    serial_number = Column(String(255), nullable=True)
    is_removable = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    mount_point = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wipe_sessions = relationship("WipeSession", back_populates="device")

class WipeSession(Base):
    __tablename__ = "wipe_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    method = Column(Enum(WipeMethod), nullable=False)
    passes = Column(Integer, default=1)
    status = Column(Enum(WipeStatus), default=WipeStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    sha_before = Column(String(64), nullable=True)
    sha_after = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    report_path = Column(String(500), nullable=True)
    signature_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    device = relationship("Device", back_populates="wipe_sessions")
    progress_updates = relationship("WipeProgress", back_populates="session")

class WipeProgress(Base):
    __tablename__ = "wipe_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("wipe_sessions.id"), nullable=False)
    progress_percentage = Column(Float, default=0.0)
    current_pass = Column(Integer, default=0)
    total_passes = Column(Integer, default=1)
    bytes_processed = Column(Integer, default=0)
    total_bytes = Column(Integer, default=0)
    estimated_time_remaining = Column(Float, nullable=True)
    status_message = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("WipeSession", back_populates="progress_updates")

class CryptographicKey(Base):
    __tablename__ = "cryptographic_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String(255), unique=True, index=True, nullable=False)
    key_type = Column(String(50), nullable=False)  # 'aes', 'rsa', 'device_key'
    key_data = Column(Text, nullable=False)  # Encrypted key data
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    destroyed_at = Column(DateTime, nullable=True)
    
    # Relationships
    device = relationship("Device")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)  # 'device', 'session', 'key'
    resource_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)