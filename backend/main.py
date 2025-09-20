from fastapi import FastAPI
from routes.api import router as api_router

app = FastAPI(title="DataWipe Backend - SIH25070")
app.include_router(api_router, prefix="/api")
