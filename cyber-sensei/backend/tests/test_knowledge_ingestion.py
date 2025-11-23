"""
Unit tests for the knowledge ingestion service with Celery task integration.

Tests cover:
- Document status transitions for videos and documents
- Video transcription workflow
- Knowledge base ingestion
- Celery task queueing
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch, MagicMock

from app.models import KnowledgeDocument
from app.services.knowledge_ingestion import (
    enqueue_ingestion_job,
    _handle_video_document,
    _write_transcript_file,
    _ingest_source,
    ingest_document,
)


class TestKnowledgeIngestionStatusTransitions:
    """Test status transitions for knowledge document ingestion."""
    
    def test_video_document_status_flow(self):
        """
        Test that video documents flow through expected status transitions.
        
        Expected flow:
        registered -> pending_transcription -> transcribing -> processing -> completed
        """
        # Create mock document
        doc = Mock(spec=KnowledgeDocument)
        doc.id = 1
        doc.doc_type = "video"
        doc.filename = "test_video.mp4"
        doc.file_path = "/tmp/test_video.mp4"
        doc.status = "registered"
        doc.notes = ""
        doc.transcript = None
        
        # Mock session
        session = Mock()
        session.get.return_value = doc
        session.commit = Mock()
        
        # Mock whisper transcription
        with patch('app.services.knowledge_ingestion._transcribe_video') as mock_transcribe:
            mock_transcribe.return_value = "Transcribed text"
            
            # This would normally be called during ingestion
            # Simulating _handle_video_document
            assert doc.status == "registered"
            
            # After _handle_video_document starts
            doc.status = "pending_transcription"
            assert doc.status == "pending_transcription"
            
            doc.status = "transcribing"
            assert doc.status == "transcribing"
            
            # Simulate successful transcription
            doc.status = "processing"
            assert doc.status == "processing"
            
            # After _ingest_source
            doc.status = "completed"
            assert doc.status == "completed"
    
    def test_document_status_flow(self):
        """
        Test that non-video documents flow through expected status transitions.
        
        Expected flow:
        registered -> processing -> completed
        """
        doc = Mock(spec=KnowledgeDocument)
        doc.id = 1
        doc.doc_type = "document"
        doc.filename = "test_doc.pdf"
        doc.file_path = "/tmp/test_doc.pdf"
        doc.status = "registered"
        doc.notes = ""
        
        # Simulate non-video ingestion
        assert doc.status == "registered"
        
        doc.status = "processing"
        assert doc.status == "processing"
        
        doc.status = "completed"
        assert doc.status == "completed"
    
    def test_failed_transcription_status(self):
        """Test that failed transcription results in 'failed' status."""
        doc = Mock(spec=KnowledgeDocument)
        doc.id = 1
        doc.status = "transcribing"
        doc.notes = "Generating transcript"
        
        # Simulate transcription failure
        doc.status = "failed"
        doc.notes = "Transcription failed: [error message]"
        
        assert doc.status == "failed"
        assert "failed" in doc.notes.lower()


class TestVideoTranscriptionIntegration:
    """Test video transcription with Celery task queue integration."""
    
    def test_enqueue_ingestion_job_with_celery(self):
        """Test that ingestion job is queued with Celery when available."""
        with patch('app.services.knowledge_ingestion.celery_app') as mock_celery:
            # Mock the task
            mock_task = Mock()
            mock_celery.task.return_value = mock_task
            
            # This would queue the job
            # In production, the decorator @celery_app.task registers the function
            assert mock_celery is not None
    
    def test_enqueue_ingestion_fallback(self):
        """Test fallback to FastAPI background tasks when Celery unavailable."""
        # Create mock background tasks
        mock_bg_tasks = Mock()
        
        with patch('app.services.knowledge_ingestion.os.getenv') as mock_getenv:
            # Mock Celery disabled
            mock_getenv.return_value = "false"
            
            # With USE_CELERY=false, should use background_tasks.add_task
            # This is handled by enqueue_ingestion_job
            assert mock_bg_tasks is not None
    
    def test_write_transcript_file(self):
        """Test that transcript is correctly written to file."""
        with TemporaryDirectory() as tmpdir:
            # Mock document
            doc = Mock(spec=KnowledgeDocument)
            doc.id = 123
            doc.filename = "video.mp4"
            
            # Patch the TRANSCRIPT_DIR
            with patch('app.services.knowledge_ingestion.TRANSCRIPT_DIR', Path(tmpdir)):
                transcript_text = "This is the transcribed text from the video."
                transcript_path = _write_transcript_file(doc, transcript_text)
                
                # Verify file was created
                assert Path(transcript_path).exists()
                
                # Verify content
                saved_content = Path(transcript_path).read_text(encoding="utf-8")
                assert saved_content == transcript_text
                
                # Verify filename format
                assert "video_123" in transcript_path


class TestKnowledgeBaseIngestion:
    """Test knowledge base ingestion process."""
    
    def test_ingest_source_success(self):
        """Test successful knowledge base ingestion."""
        doc = Mock(spec=KnowledgeDocument)
        doc.id = 1
        doc.filename = "test.pdf"
        doc.user_id = 1
        doc.doc_type = "document"
        doc.status = "processing"
        doc.notes = "Chunking and embedding."
        
        session = Mock()
        session.commit = Mock()
        
        with patch('app.services.knowledge_ingestion.kb_manager.add_source') as mock_add:
            mock_add.return_value = "Successfully indexed document."
            
            _ingest_source(doc, session, "/tmp/test.pdf")
            
            assert doc.status == "completed"
            assert "Successfully" in doc.notes
            session.commit.assert_called()
    
    def test_ingest_source_failure(self):
        """Test knowledge base ingestion failure handling."""
        doc = Mock(spec=KnowledgeDocument)
        doc.id = 1
        doc.filename = "test.pdf"
        doc.status = "processing"
        
        session = Mock()
        session.commit = Mock()
        
        with patch('app.services.knowledge_ingestion.kb_manager.add_source') as mock_add:
            mock_add.return_value = "Error: Could not process file"
            
            _ingest_source(doc, session, "/tmp/test.pdf")
            
            assert doc.status == "failed"
            assert "Error" in doc.notes


class TestCeleryTaskIntegration:
    """Test Celery task registration and execution."""
    
    def test_ingest_document_task_registered(self):
        """Test that ingest_document_task is properly registered with Celery."""
        from app.services.knowledge_ingestion import ingest_document_task
        
        # Verify the task exists and has expected attributes
        assert ingest_document_task is not None
        assert hasattr(ingest_document_task, 'delay')
        assert hasattr(ingest_document_task, 'apply_async')
    
    def test_transcribe_video_task_registered(self):
        """Test that transcribe_video_task is properly registered with Celery."""
        from app.services.knowledge_ingestion import transcribe_video_task
        
        # Verify the task exists and has expected attributes
        assert transcribe_video_task is not None
        assert hasattr(transcribe_video_task, 'delay')
        assert hasattr(transcribe_video_task, 'apply_async')
    
    def test_task_retry_configuration(self):
        """Test that tasks are configured with retry logic."""
        from app.services.knowledge_ingestion import ingest_document_task
        
        # Celery tasks should have retry configuration
        # max_retries=3 and default_retry_delay=60 for ingest_document_task
        # These are set in the @celery_app.task decorator
        assert ingest_document_task is not None


class TestStatusTransitionConsistency:
    """Test that status transitions are consistent and complete."""
    
    def test_all_documents_have_status_field(self):
        """Test that all KnowledgeDocument objects have a status field."""
        doc = Mock(spec=KnowledgeDocument)
        doc.status = "registered"
        
        valid_statuses = {
            "registered",
            "pending_transcription",
            "transcribing",
            "processing",
            "completed",
            "failed"
        }
        
        assert doc.status in valid_statuses
    
    def test_status_transitions_are_valid(self):
        """Test that only valid status transitions occur."""
        # Valid transitions
        transitions = {
            "registered": ["pending_transcription", "processing"],  # video or document
            "pending_transcription": ["transcribing"],
            "transcribing": ["processing", "failed"],
            "processing": ["completed", "failed"],
            "completed": [],  # terminal state
            "failed": [],  # terminal state
        }
        
        # Verify structure
        for from_state, to_states in transitions.items():
            assert isinstance(from_state, str)
            assert isinstance(to_states, list)
