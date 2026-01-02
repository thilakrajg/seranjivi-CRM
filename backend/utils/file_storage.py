import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from datetime import datetime, timezone

# Storage directory for uploaded files
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def save_upload_file(upload_file: UploadFile, entity_type: str, entity_id: str) -> dict:
    """
    Save an uploaded file and return its metadata
    """
    # Validate file extension
    file_ext = Path(upload_file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {file_ext} not allowed")
    
    # Read file content
    content = await upload_file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum of 10MB")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Create entity-specific directory
    entity_dir = UPLOAD_DIR / entity_type / entity_id
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = entity_dir / unique_filename
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Return metadata
    return {
        "id": str(uuid.uuid4()),
        "name": upload_file.filename,
        "originalName": upload_file.filename,
        "storedName": unique_filename,
        "size": len(content),
        "type": upload_file.content_type,
        "path": str(file_path),
        "url": f"/api/files/{entity_type}/{entity_id}/{unique_filename}",
        "uploadedAt": datetime.now(timezone.utc).isoformat()
    }

def delete_file(file_path: str) -> bool:
    """
    Delete a file from storage
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def get_file_path(entity_type: str, entity_id: str, filename: str) -> Path:
    """
    Get the full path to a stored file
    """
    return UPLOAD_DIR / entity_type / entity_id / filename
