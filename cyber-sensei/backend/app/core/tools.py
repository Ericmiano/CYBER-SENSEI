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
    import logging
    logger = logging.getLogger(__name__)
    
    if not username or len(username.strip()) == 0:
        return "Error: Username is required"
    
    db = SessionLocal()
    try:
        engine = CurriculumEngine(db)
        step = engine.get_next_step(username.strip())
        if step.get("type") == "error":
            return f"Error: {step.get('message', 'Unknown error')}"
        return f"Next Step: {step.get('message', 'No next step available')}"
    except Exception as e:
        logger.error(f"Error getting next step for {username}: {e}")
        return f"Error: Failed to get next learning step: {str(e)}"
    finally:
        db.close()

@tool
def query_personal_knowledge(query: str) -> str:
    """Searches the user's personal knowledge base for information."""
    import logging
    logger = logging.getLogger(__name__)
    
    if not query or len(query.strip()) == 0:
        return "Error: Query text is required"
    
    try:
        context = kb_manager.query(query.strip())
        if "Error" in context or "couldn't find" in context:
            return context
        return f"Here is relevant information from your personal notes:\n\n{context}"
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        return f"Error: Failed to query knowledge base: {str(e)}"

@tool
def add_document_to_knowledge_base(file_path: str) -> str:
    """Adds a local document to the user's personal knowledge base."""
    import logging
    logger = logging.getLogger(__name__)
    
    if not file_path or len(file_path.strip()) == 0:
        return "Error: File path is required"
    
    try:
        result = kb_manager.add_source(file_path.strip())
        return result
    except Exception as e:
        logger.error(f"Error adding document to knowledge base: {e}")
        return f"Error: Failed to add document: {str(e)}"

@tool
def start_lab_environment(lab_name: str) -> str:
    """Starts a predefined lab environment."""
    import logging
    logger = logging.getLogger(__name__)
    
    if not lab_name or len(lab_name.strip()) == 0:
        return "Error: Lab name is required"
    
    try:
        result = lab_manager.start_lab(lab_name.strip())
        return result
    except Exception as e:
        logger.error(f"Error starting lab {lab_name}: {e}")
        return f"Error: Failed to start lab: {str(e)}"

# Note: The quiz submission and progress update will be handled by a dedicated API endpoint
# for better control and validation, rather than a generic tool.