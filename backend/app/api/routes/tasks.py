import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.models import Task, TaskCreate, TaskPublic, TasksPublic

router = APIRouter()

@router.get("/", response_model=TasksPublic)
def read_tasks(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve batch tasks.
    """
    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    return TasksPublic(data=tasks, count=count)

@router.post("/", response_model=TaskPublic)
def create_task(
    *, session: SessionDep, task_in: TaskCreate
) -> Any:
    """
    Create new batch task.
    """
    task = Task.model_validate(task_in)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/{id}", response_model=TaskPublic)
def read_task(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get task status/result.
    """
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{id}/cancel", response_model=TaskPublic)
def cancel_task(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Cancel a task.
    """
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed task")

    task.status = "cancelled"
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
