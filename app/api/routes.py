import os
import tempfile

from app.services.document_processor import process_and_extract_fields
from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("/process-documents", response_model=dict)
async def process_documents_endpoint(files: list[UploadFile] = File(...)):
    temp_file_paths = []
    for file in files:
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(suffix=file.filename, delete=False)
        temp_file_paths.append(temp_file.name)

        # Write content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

    # Process documents and extract fields
    result = process_and_extract_fields(temp_file_paths)

    # Clean up temp files
    for path in temp_file_paths:
        os.unlink(path)

    return result
