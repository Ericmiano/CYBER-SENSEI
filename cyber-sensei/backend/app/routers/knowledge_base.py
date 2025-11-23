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
    """Return all knowledge base documents (temporary global scope)."""
    documents = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()
    return documents


@router.post("/add-document", response_model=KnowledgeDocumentResponse)
def add_document_to_knowledge_base(
    payload: KnowledgeDocumentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Registers a document for ingestion from a shared path."""
    if not payload.file_path or not os.path.exists(payload.file_path):
        raise HTTPException(
            status_code=400,
            detail="File not found on server. Upload a file first or provide a valid shared path.",
        )

    filename = payload.display_name or os.path.basename(payload.file_path)
    doc = KnowledgeDocument(
        user_id=_resolve_user_id(db, payload.username),
        filename=filename,
        file_path=payload.file_path,
        doc_type="document",
        status="registered",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    enqueue_ingestion_job(doc.id, background_tasks)
    return doc


@router.post("/upload-document", response_model=KnowledgeDocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    username: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    saved_path = await _save_upload(file, "documents", ALLOWED_DOC_EXTENSIONS)
    doc = KnowledgeDocument(
        user_id=_resolve_user_id(db, username),
        filename=file.filename,
        file_path=str(saved_path),
        doc_type="document",
        status="registered",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    enqueue_ingestion_job(doc.id, background_tasks)
    return doc


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
    doc = db.query(KnowledgeDocument).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
