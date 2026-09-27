from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from typing import Dict, Any, List
import hashlib
import io
import json
import pandas as pd
from pydantic import BaseModel
from reelscope_engine.db import get_db
from reelscope_engine.importers import generate_preview, validate_mapped_data, commit_import_to_db

router = APIRouter(prefix="/api/import", tags=["Import"])

# In-memory storage for uploaded preview buffers (keyed by hash)
UPLOAD_CACHE: Dict[str, bytes] = {}

@router.post("/preview")
async def preview_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
    file_hash = hashlib.sha256(content).hexdigest()
    UPLOAD_CACHE[file_hash] = content

    preview_res = generate_preview(content, file.filename)
    preview_res["file_hash"] = file_hash
    return preview_res

class CommitImportRequest(BaseModel):
    file_hash: str
    filename: str
    mapping: Dict[str, str]

@router.post("/commit")
def commit_import(req: CommitImportRequest) -> Dict[str, Any]:
    if req.file_hash not in UPLOAD_CACHE:
        raise HTTPException(status_code=400, detail="Uploaded file session expired or not found. Please upload again.")
        
    content = UPLOAD_CACHE[req.file_hash]
    filename = req.filename

    if filename.endswith(".json"):
        df = pd.DataFrame(json.loads(content.decode("utf-8")))
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(content))
    else:
        df = pd.read_csv(io.BytesIO(content))

    val_report = validate_mapped_data(df, req.mapping)
    if not val_report["is_valid"]:
        raise HTTPException(status_code=422, detail={"validation_errors": val_report["errors"]})

    conn = get_db()
    result = commit_import_to_db(conn, df, req.mapping, req.file_hash, filename)
    return result

@router.get("/history")
def get_import_history() -> List[Dict[str, Any]]:
    conn = get_db()
    df = conn.execute("SELECT * FROM imports ORDER BY imported_at DESC").fetchdf()
    return df.to_dict(orient="records")
