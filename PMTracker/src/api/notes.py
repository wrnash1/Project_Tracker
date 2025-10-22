from fastapi import APIRouter, HTTPException
from typing import List
from models import NoteCreate, NoteResponse
from core.sqlite_manager import SQLiteManager

router = APIRouter()

@router.post("/", response_model=dict)
async def create_note(note: NoteCreate):
    """Create a new project note"""
    try:
        with SQLiteManager() as db:
            note_id = db.create_note(
                note.project_number,
                note.title,
                note.content,
                note.tags,
                note.created_by
            )
            return {"id": note_id, "message": "Note created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_number}", response_model=List[NoteResponse])
async def get_notes(project_number: str):
    """Get all notes for a project"""
    try:
        with SQLiteManager() as db:
            notes = db.get_notes(project_number)
            return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{note_id}", response_model=dict)
async def update_note(note_id: int, title: str, content: str, tags: str = ''):
    """Update an existing note"""
    try:
        with SQLiteManager() as db:
            rows_affected = db.update_note(note_id, title, content, tags)
            if rows_affected == 0:
                raise HTTPException(status_code=404, detail="Note not found")
            return {"message": "Note updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{note_id}", response_model=dict)
async def delete_note(note_id: int):
    """Delete a note"""
    try:
        with SQLiteManager() as db:
            rows_affected = db.delete_note(note_id)
            if rows_affected == 0:
                raise HTTPException(status_code=404, detail="Note not found")
            return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
