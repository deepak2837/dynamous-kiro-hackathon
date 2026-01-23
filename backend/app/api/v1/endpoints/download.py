"""
Download endpoints for exporting study materials as PDFs.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.background import BackgroundTask
import os
import tempfile
from typing import Literal

from app.services.export_service import ExportService
from app.api.auth_simple import get_current_user

router = APIRouter()

ContentType = Literal["questions", "notes", "cheatsheet", "mnemonics"]

@router.get("/download/{content_type}/{session_id}")
async def download_content(
    content_type: ContentType,
    session_id: str,
    current_user = Depends(get_current_user)
):
    """Download study materials as PDF."""
    try:
        export_service = ExportService()
        filename = f"{content_type}_{session_id}.pdf"
        
        # Generate PDF based on content type
        if content_type == "questions":
            pdf_path = await export_service.generate_questions_pdf(session_id)
        elif content_type == "notes":
            pdf_path = await export_service.generate_notes_pdf(session_id)
        elif content_type == "cheatsheet":
            pdf_path = await export_service.generate_cheatsheet_pdf(session_id)
        elif content_type == "mnemonics":
            pdf_path = await export_service.generate_mnemonics_pdf(session_id)
        else:
            raise ValueError("Invalid content type")
        
        # Return file response with cleanup after sending
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf",
            background=BackgroundTask(export_service.cleanup_temp_file, pdf_path)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
