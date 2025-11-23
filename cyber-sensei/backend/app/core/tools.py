from langchain.tools import tool
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..engines.progress import ProgressTracker
from ..engines.curriculum import CurriculumEngine
from ..engines.knowledge_base import PersonalKnowledgeBase
from ..engines.lab import LabManager

# Instantiate engines (they will get a db session when called)
kb_manager = PersonalKnowledgeBase()
lab_manager = LabManager()

@tool
def get_next_learning_step_for_user(username: str) -> str:
    """Determines the next learning step for the given user."""
    db = SessionLocal()
    try:
        engine = CurriculumEngine(db)
        step = engine.get_next_step(username)
        return f"Next Step: {step['message']}"
    finally:
        db.close()

@tool
def query_personal_knowledge(query: str) -> str:
    """Searches the user's personal knowledge base for information."""
    context = kb_manager.query(query)
    if "Error" in context or "couldn't find" in context:
        return context
    return f"Here is relevant information from your personal notes:\n\n{context}"

@tool
def add_document_to_knowledge_base(file_path: str) -> str:
    """Adds a local document to the user's personal knowledge base."""
    return kb_manager.add_source(file_path)

@tool
def start_lab_environment(lab_name: str) -> str:
    """Starts a predefined lab environment."""
    return lab_manager.start_lab(lab_name)

# Note: The quiz submission and progress update will be handled by a dedicated API endpoint
# for better control and validation, rather than a generic tool.