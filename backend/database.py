import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models import Base, Device, WipeSession, WipeProgress, CryptographicKey, AuditLog
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/zerotrace.db")
DB_DIR = "data"
DB_FILE = os.path.join(DB_DIR, "zerotrace.db")

# Ensure data directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Create engine with proper configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database and create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session for direct use"""
    return SessionLocal()

def create_device(device_path, device_name, device_type="unknown", **kwargs):
    """Create a new device record"""
    db = get_db_session()
    try:
        device = Device(
            device_path=device_path,
            device_name=device_name,
            device_type=device_type,
            **kwargs
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create device: {e}")
        return None
    finally:
        db.close()

def get_device_by_path(device_path):
    """Get device by path"""
    db = get_db_session()
    try:
        return db.query(Device).filter(Device.device_path == device_path).first()
    except Exception as e:
        logger.error(f"Failed to get device: {e}")
        return None
    finally:
        db.close()

def get_all_devices():
    """Get all devices"""
    db = get_db_session()
    try:
        return db.query(Device).all()
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        return []
    finally:
        db.close()

def create_wipe_session(device_id, method, passes=1):
    """Create a new wipe session"""
    db = get_db_session()
    try:
        session = WipeSession(
            device_id=device_id,
            method=method,
            passes=passes
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create wipe session: {e}")
        return None
    finally:
        db.close()

def update_wipe_session(session_id, **kwargs):
    """Update wipe session"""
    db = get_db_session()
    try:
        session = db.query(WipeSession).filter(WipeSession.id == session_id).first()
        if session:
            for key, value in kwargs.items():
                setattr(session, key, value)
            db.commit()
            return session
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update wipe session: {e}")
        return None
    finally:
        db.close()

def add_progress_update(session_id, progress_percentage, **kwargs):
    """Add progress update for a session"""
    db = get_db_session()
    try:
        progress = WipeProgress(
            session_id=session_id,
            progress_percentage=progress_percentage,
            **kwargs
        )
        db.add(progress)
        db.commit()
        return progress
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add progress update: {e}")
        return None
    finally:
        db.close()

def get_session_progress(session_id):
    """Get latest progress for a session"""
    db = get_db_session()
    try:
        return db.query(WipeProgress).filter(
            WipeProgress.session_id == session_id
        ).order_by(WipeProgress.timestamp.desc()).first()
    except Exception as e:
        logger.error(f"Failed to get session progress: {e}")
        return None
    finally:
        db.close()

def log_audit_event(action, resource_type, resource_id, **kwargs):
    """Log audit event"""
    db = get_db_session()
    try:
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )
        db.add(audit_log)
        db.commit()
        return audit_log
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to log audit event: {e}")
        return None
    finally:
        db.close()

def get_wipe_history(limit=50):
    """Get wipe history"""
    db = get_db_session()
    try:
        return db.query(WipeSession).join(Device).order_by(
            WipeSession.created_at.desc()
        ).limit(limit).all()
    except Exception as e:
        logger.error(f"Failed to get wipe history: {e}")
        return []
    finally:
        db.close()

# Legacy compatibility functions
def init_db():
    """Legacy function for backward compatibility"""
    return init_database()

def insert_log(device, method, passes, start_time, end_time, sha_before, sha_after, status, report_path):
    """Legacy function for backward compatibility"""
    # Find or create device
    device_obj = get_device_by_path(device)
    if not device_obj:
        device_obj = create_device(device, device.split('/')[-1])
    
    if device_obj:
        session = create_wipe_session(device_obj.id, method, passes)
        if session:
            update_wipe_session(
                session.id,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.fromtimestamp(end_time),
                duration_seconds=end_time - start_time,
                sha_before=sha_before,
                sha_after=sha_after,
                status=status,
                report_path=report_path
            )