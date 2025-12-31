from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..engines.lab import LabManager
from ..models import Module, Topic
from ..schemas.lab import (
    LabCommandRequest,
    LabInstructionResponse,
    LabModuleResponse,
    LabTopicResponse,
)

router = APIRouter(prefix="/api/labs", tags=["labs"])
lab_manager = LabManager()


@router.get("/modules", response_model=list[LabModuleResponse])
def get_lab_modules(db: Session = Depends(get_db)):
    """Get all lab modules."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        modules = db.query(Module).order_by(Module.id).all()
        return modules
    except Exception as e:
        logger.error(f"Error getting lab modules: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve modules")


@router.get("/modules/{module_id}/topics", response_model=list[LabTopicResponse])
def get_lab_topics(module_id: int, db: Session = Depends(get_db)):
    """Get topics for a specific lab module."""
    import logging
    logger = logging.getLogger(__name__)
    
    if module_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid module ID")
    
    try:
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        topics = db.query(Topic).filter(Topic.module_id == module_id).order_by(Topic.id).all()
        return topics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting topics for module {module_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve topics")


@router.get("/{lab_id}/instructions", response_model=LabInstructionResponse)
def get_lab_instructions(lab_id: str):
    """Get instructions for a lab."""
    import logging
    logger = logging.getLogger(__name__)
    
    if not lab_id or len(lab_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Lab ID is required")
    
    try:
        instructions = lab_manager.get_lab_instructions(lab_id.strip())
        if not instructions:
            raise HTTPException(status_code=404, detail="Lab not found")
        return instructions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lab instructions for {lab_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve lab instructions")


@router.post("/{lab_id}/execute")
async def execute_lab_command(lab_id: str, payload: LabCommandRequest, db: Session = Depends(get_db)):
    """Execute a command in a lab environment."""
    import logging
    from ..models import User
    from ..security import get_current_user_optional
    
    logger = logging.getLogger(__name__)
    
    # Validate inputs
    if not lab_id or len(lab_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Lab ID is required")
    
    if not payload.command or len(payload.command.strip()) == 0:
        raise HTTPException(status_code=400, detail="Command is required")
    
    # Security: Limit command length
    if len(payload.command) > 1000:
        raise HTTPException(status_code=400, detail="Command too long (max 1000 characters)")
    
    # Security: Block dangerous commands
    dangerous_commands = ['rm -rf', 'format', 'del /f', 'shutdown', 'reboot', 'dd if=']
    command_lower = payload.command.lower()
    for dangerous in dangerous_commands:
        if dangerous.lower() in command_lower:
            raise HTTPException(
                status_code=400,
                detail=f"Command contains potentially dangerous operation: {dangerous}"
            )
    
    # Try to get user if authenticated
    user_id = None
    try:
        user_email = await get_current_user_optional()
        if user_email:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                user_id = str(user.id)
    except Exception as e:
        logger.debug(f"Could not get user for lab execution: {e}")
        # Not authenticated, use anonymous lab - this is okay
    
    try:
        result = lab_manager.execute_command(lab_id.strip(), payload.command.strip(), user_id=user_id)
        return {"lab_id": lab_id, "output": result, "command": payload.command}
    except Exception as e:
        logger.error(f"Error executing lab command: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")


@router.post("/{lab_id}/start")
async def start_lab(lab_id: str, db: Session = Depends(get_db)):
    """Start a lab environment."""
    import logging
    from ..models import User
    from ..security import get_current_user_optional
    
    logger = logging.getLogger(__name__)
    
    if not lab_id or len(lab_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Lab ID is required")
    
    user_id = None
    try:
        user_email = await get_current_user_optional()
        if user_email:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                user_id = str(user.id)
    except Exception as e:
        logger.debug(f"Could not get user for lab start: {e}")
        # Not authenticated, use anonymous lab - this is okay
    
    try:
        result = lab_manager.start_lab(lab_id.strip(), user_id=user_id)
        return {"lab_id": lab_id, "message": result, "status": "started"}
    except Exception as e:
        logger.error(f"Error starting lab: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start lab: {str(e)}")


@router.post("/{lab_id}/stop")
async def stop_lab(lab_id: str, db: Session = Depends(get_db)):
    """Stop a lab environment."""
    import logging
    from ..models import User
    from ..security import get_current_user_optional
    
    logger = logging.getLogger(__name__)
    
    if not lab_id or len(lab_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="Lab ID is required")
    
    user_id = None
    try:
        user_email = await get_current_user_optional()
        if user_email:
            user = db.query(User).filter(User.email == user_email).first()
            if user:
                user_id = str(user.id)
    except Exception as e:
        logger.debug(f"Could not get user for lab stop: {e}")
        # Not authenticated, use anonymous lab - this is okay
    
    try:
        result = lab_manager.stop_lab(lab_id.strip(), user_id=user_id)
        return {"lab_id": lab_id, "message": result, "status": "stopped"}
    except Exception as e:
        logger.error(f"Error stopping lab: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop lab: {str(e)}")


@router.get("/active")
def list_active_labs():
    """List all active lab environments."""
    active_labs = lab_manager.list_active_labs()
    return {"active_labs": active_labs, "count": len(active_labs)}

