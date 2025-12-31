import logging
import os
from pathlib import Path
import traceback
from typing import Optional

from fastapi import BackgroundTasks

try:
    import whisper
except ImportError:  # pragma: no cover - optional dependency
    whisper = None

from ..celery_app import celery_app
from ..database import SessionLocal
from ..engines.knowledge_base import PersonalKnowledgeBase
from ..models import KnowledgeDocument


logger = logging.getLogger(__name__)
kb_manager = PersonalKnowledgeBase()

DATA_ROOT = Path(os.getenv("DATA_DIR", "./data")).resolve()
TRANSCRIPT_DIR = Path(os.getenv("TRANSCRIPT_DIR", DATA_ROOT / "transcripts")).resolve()
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
_WHISPER_INSTANCE = None


def _load_whisper_model():
    global _WHISPER_INSTANCE  # pylint: disable=global-statement
    if whisper is None:
        raise RuntimeError(
            "openai-whisper is not installed. Install dependency to enable video transcription."
        )
    if _WHISPER_INSTANCE is None:
        _WHISPER_INSTANCE = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
    return _WHISPER_INSTANCE


def enqueue_ingestion_job(document_id: int, background_tasks: Optional[BackgroundTasks] = None):
    """Dispatch ingestion to Celery when possible, otherwise fall back to FastAPI background task."""
    use_celery = os.getenv("USE_CELERY", "true").strip().lower() not in {"0", "false", "no"}
    if use_celery:
        try:
            ingest_document_task.delay(document_id)
            return
        except Exception as exc:  # pragma: no cover - only hit when broker unavailable
            logger.warning("Celery dispatch failed, falling back to local task: %s", exc)
    if background_tasks is not None:
        background_tasks.add_task(ingest_document, document_id)
    else:
        ingest_document(document_id)


def _transcribe_video(doc: KnowledgeDocument) -> str:
    model = _load_whisper_model()
    logger.info("Starting transcription for document %s", doc.id)
    result = model.transcribe(doc.file_path)
    text = (result.get("text") or "").strip()
    if not text:
        raise RuntimeError("Transcription returned empty text.")
    return text


def _write_transcript_file(doc: KnowledgeDocument, transcript: str) -> str:
    safe_stem = f"{Path(doc.filename).stem}_{doc.id}".replace(" ", "_")
    transcript_path = TRANSCRIPT_DIR / f"{safe_stem}.txt"
    transcript_path.write_text(transcript, encoding="utf-8")
    return str(transcript_path)


def _ingest_source(doc: KnowledgeDocument, session, source_path: str):
    result_message = kb_manager.add_source(
        source_path,
        metadata={
            "doc_id": str(doc.id),
            "user_id": str(doc.user_id) if doc.user_id else "anonymous",
            "doc_type": doc.doc_type,
        },
    )
    if result_message.startswith("Error"):
        doc.status = "failed"
        doc.notes = result_message
    else:
        doc.status = "completed"
        doc.notes = result_message
    session.commit()


def _handle_video_document(doc: KnowledgeDocument, session) -> Optional[str]:
    doc.status = "pending_transcription"
    doc.notes = "Queued for transcription."
    session.commit()

    try:
        doc.status = "transcribing"
        doc.notes = "Generating transcript with Whisper."
        session.commit()

        transcript_text = _transcribe_video(doc)
        doc.transcript = transcript_text
        transcript_path = _write_transcript_file(doc, transcript_text)

        doc.status = "processing"
        doc.notes = "Transcript generated. Indexing now."
        session.commit()
        return transcript_path
    except Exception as exc:
        logger.exception("Video transcription failed for doc %s: %s", doc.id, exc)
        doc.status = "failed"
        doc.notes = f"Transcription failed: {exc}"
        session.commit()
        return None


def ingest_document(document_id: int):
    """Background ingestion job that chunks + embeds a document."""
    session = SessionLocal()
    source_path: Optional[str] = None
    try:
        doc: Optional[KnowledgeDocument] = session.get(KnowledgeDocument, document_id)
        if not doc:
            return

        if doc.doc_type == "video":
            source_path = _handle_video_document(doc, session)
            if not source_path:
                return
        else:
            doc.status = "processing"
            doc.notes = "Chunking and embedding."
            session.commit()
            source_path = doc.file_path

        _ingest_source(doc, session, source_path)

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Ingestion failed for doc %s: %s", document_id, exc)
        try:
            doc = session.get(KnowledgeDocument, document_id)
            if doc:
                doc.status = "failed"
                doc.notes = f"Ingestion failed: {exc}"
            session.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update document status: {commit_error}")
            session.rollback()
    finally:
        session.close()


@celery_app.task(name="knowledge.ingest_document")
def ingest_document_task(document_id: int):
    ingest_document(document_id)


@celery_app.task(name="knowledge.transcribe_video")
def transcribe_video_task(document_id: int):
    """Task wrapper to transcribe a video document and index it."""
    session = SessionLocal()
    try:
        doc = session.get(KnowledgeDocument, document_id)
        if not doc:
            return None
        # Use existing handler which updates status and does indexing
        _handle_video_document(doc, session)
    except Exception:
        logger.exception("transcribe_video_task failed for %s", document_id)
    finally:
        session.close()
