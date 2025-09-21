from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from routes.api import router as api_router
from database import init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(
    title="ZeroTrace Backend - SIH25070",
    description="Secure Data Wiping Tool Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Mount static files for reports
if not os.path.exists("reports"):
    os.makedirs("reports")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("ZeroTrace Backend starting up...")
    logger.info("Database initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("ZeroTrace Backend shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
