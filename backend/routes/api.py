from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.wipe_engine import list_drives, initiate_wipe

router = APIRouter()

class WipeRequest(BaseModel):
    device: str
    method: str
    passes: int = 1
    force: bool = False

@router.get("/drives")
def api_list_drives():
    return list_drives()

@router.post("/wipe")
def api_wipe(req: WipeRequest):
    if not req.device or not req.method:
        raise HTTPException(status_code=400, detail="device and method required")
    result = initiate_wipe(req.device, req.method, req.passes, req.force)
    return {"result": result}
