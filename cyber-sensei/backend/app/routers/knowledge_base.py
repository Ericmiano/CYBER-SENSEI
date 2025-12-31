import os
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import KnowledgeDocument, User
from ..schemas.knowledge import KnowledgeDocumentCreate, KnowledgeDocumentResponse
from ..services.knowledge_ingestion import enqueue_ingestion_job

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge-base"])

DATA_ROOT = Path(os.getenv("DATA_DIR", "./data")).resolve()
UPLOAD_ROOT = (DATA_ROOT / "uploads").resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 25 * 1024 * 1024))
ALLOWED_DOC_EXTENSIONS = {".txt", ".pdf"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


async def _save_upload(file: UploadFile, category: str, allowed_extensions: set[str]) -> Path:
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'.")

    category_dir = UPLOAD_ROOT / category
    category_dir.mkdir(parents=True, exist_ok=True)
    destination = category_dir / file.filename
    counter = 1
    stem = destination.stem
    suffix = destination.suffix
    while destination.exists():
        destination = category_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    total_written = 0
    with destination.open("wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            buffer.write(chunk)
            total_written += len(chunk)
            if total_written > MAX_UPLOAD_BYTES:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large.")
    return destination


def _resolve_user_id(db: Session, username: str | None) -> int | None:
    if not username:
        return None
    user = db.query(User).filter_by(username=username).first()
    if user:
        return user.id
    return None


@router.get("", response_model=list[KnowledgeDocumentResponse])
def list_knowledge_documents(db: Session = Depends(get_db)):
    """Return all knowledge base documents."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        documents = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()
        return documents
    except Exception as e:
        logger.error(f"Error listing knowledge documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")


@router.post("/add-document", response_model=KnowledgeDocumentResponse)
def add_document_to_knowledge_base(
    payload: KnowledgeDocumentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Registers a document for ingestion from a shared path."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate file path
        if not payload.file_path:
            raise HTTPException(status_code=400, detail="File path is required")
        
        # Security: Prevent path traversal attacks
        file_path = Path(payload.file_path).resolve()
        data_root = Path(DATA_ROOT).resolve()
        
        # Ensure file is within data directory
        try:
            file_path.relative_to(data_root)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="File path must be within the data directory"
            )
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found on server. Upload a file first or provide a valid shared path."
            )
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path must point to a file, not a directory")
        
        # Validate file extension
        ext = file_path.suffix.lower()
        if ext not in ALLOWED_DOC_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_DOC_EXTENSIONS)}"
            )
        
        # Validate file size
        file_size = file_path.stat().st_size
        if file_size > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_UPLOAD_BYTES / (1024*1024):.1f}MB"
            )
        
        filename = payload.display_name or file_path.name
        if len(filename) > 255:
            filename = filename[:255]
        
        doc = KnowledgeDocument(
            user_id=_resolve_user_id(db, payload.username),
            filename=filename,
            file_path=str(file_path),
            doc_type="document",
            status="registered",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        enqueue_ingestion_job(doc.id, background_tasks)
        logger.info(f"Document registered: {doc.id} - {filename}")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail="Failed to register document")


@router.post("/upload-document", response_model=KnowledgeDocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    username: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    """Upload a document file for ingestion."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Sanitize filename
        filename = file.filename
        if len(filename) > 255:
            raise HTTPException(status_code=400, detail="Filename too long (max 255 characters)")
        
        # Check for path traversal in filename
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        saved_path = await _save_upload(file, "documents", ALLOWED_DOC_EXTENSIONS)
        
        doc = KnowledgeDocument(
            user_id=_resolve_user_id(db, username),
            filename=filename,
            file_path=str(saved_path),
            doc_type="document",
            status="registered",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        enqueue_ingestion_job(doc.id, background_tasks)
        logger.info(f"Document uploaded: {doc.id} - {filename}")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.post("/upload-video", response_model=KnowledgeDocumentResponse)
async def upload_video_to_knowledge_base(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    username: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    """Registers a video for future transcription and indexing."""
    saved_path = await _save_upload(file, "videos", ALLOWED_VIDEO_EXTENSIONS)
    doc = KnowledgeDocument(
        user_id=_resolve_user_id(db, username),
        filename=file.filename,
        file_path=str(saved_path),
        doc_type="video",
        status="registered",
        transcript="Transcription pending.",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    enqueue_ingestion_job(doc.id, background_tasks)
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_knowledge_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a knowledge base document."""
    import logging
    logger = logging.getLogger(__name__)
    
    if document_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    
    try:
        doc = db.query(KnowledgeDocument).filter_by(id=document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Optionally delete the file from disk
        try:
            from pathlib import Path
            file_path = Path(doc.file_path)
            if file_path.exists() and file_path.is_file():
                # Only delete if in uploads directory (user-uploaded files)
                if 'uploads' in str(file_path):
                    file_path.unlink()
                    logger.info(f"Deleted file: {file_path}")
        except Exception as file_error:
            logger.warning(f"Could not delete file {doc.file_path}: {file_error}")
            # Continue with DB deletion even if file deletion fails
        
        db.delete(doc)
        db.commit()
        logger.info(f"Deleted knowledge document: {document_id}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
