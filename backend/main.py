from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Serve built web frontend (Vite) from FastAPI for a one-command run
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'web', 'dist'))
if os.path.isdir(FRONTEND_DIST):
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"status": "frontend build not found"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_catch_all(full_path: str):
        # Let API and reports routes be handled by their routers
        if full_path.startswith("api/") or full_path.startswith("reports/"):
            return {"detail": "Not Found"}
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"status": "frontend build not found"}

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
