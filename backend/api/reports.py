import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.config import settings
from backend.services.report_service import process_report_file

router = APIRouter(prefix="/reports", tags=["Reports"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

@router.post("/upload")
async def upload_lab_report(
    file: UploadFile = File(...),
    test_type: str = Form("cbc"),
    age: Optional[int] = Form(None),
    sex: Optional[str] = Form(None)
):
    """
    Report Upload API Endpoint.
    Accepts PDF or Image files, extracts lab data via OCR/Analyzer, and returns AI clinical explanation.
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    temp_dir = settings.BASE_DIR / "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = temp_dir / file.filename

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        report_result = process_report_file(
            file_path=str(temp_file_path),
            test_type=test_type,
            age=age,
            sex=sex
        )
        return report_result
    finally:
        if temp_file_path.exists():
            os.remove(temp_file_path)
