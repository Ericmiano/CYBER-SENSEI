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
    modules = db.query(Module).order_by(Module.id).all()
    return modules


@router.get("/modules/{module_id}/topics", response_model=list[LabTopicResponse])
def get_lab_topics(module_id: int, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    topics = db.query(Topic).filter(Topic.module_id == module_id).order_by(Topic.id).all()
    return topics


@router.get("/{lab_id}/instructions", response_model=LabInstructionResponse)
def get_lab_instructions(lab_id: str):
    instructions = lab_manager.get_lab_instructions(lab_id)
    if not instructions:
        raise HTTPException(status_code=404, detail="Lab not found")
    return instructions


@router.post("/{lab_id}/execute")
def execute_lab_command(lab_id: str, payload: LabCommandRequest):
    result = lab_manager.execute_command(lab_id, payload.command)
    return {"lab_id": lab_id, "output": result}

