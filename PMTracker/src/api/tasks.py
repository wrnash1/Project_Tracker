from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import TaskCreate, TaskResponse
from core.sqlite_manager import SQLiteManager

router = APIRouter()

@router.post("/", response_model=dict)
async def create_task(task: TaskCreate):
    """Create a new user task"""
    try:
        with SQLiteManager() as db:
            task_id = db.create_task(
                task.project_number,
                task.task_name,
                task.description,
                task.status,
                task.priority,
                task.assigned_to,
                task.due_date.isoformat() if task.due_date else None
            )
            return {"id": task_id, "message": "Task created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    project_number: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Get tasks with optional filters"""
    try:
        with SQLiteManager() as db:
            tasks = db.get_tasks(project_number, status)
            return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: int, updates: dict):
    """Update a task"""
    try:
        with SQLiteManager() as db:
            rows_affected = db.update_task(task_id, updates)
            if rows_affected == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"message": "Task updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int):
    """Delete a task"""
    try:
        with SQLiteManager() as db:
            rows_affected = db.delete_task(task_id)
            if rows_affected == 0:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
