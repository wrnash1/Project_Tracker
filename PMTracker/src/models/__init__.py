from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class ProjectBase(BaseModel):
    project_number: str
    project_name: str
    project_type: Optional[str] = None
    project_status: Optional[str] = None
    pm_name: Optional[str] = None
    pm_email: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    actual_cost: Optional[float] = None
    region: Optional[str] = None
    market: Optional[str] = None
    priority: Optional[str] = None

class ProjectResponse(ProjectBase):
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None

class ProjectMetrics(BaseModel):
    total_ccrs: int = 0
    completed_ccrs: int = 0
    total_orders: int = 0
    completed_orders: int = 0
    budget_variance: float = 0.0
    estimated_hours: float = 0.0
    actual_hours: float = 0.0

class NoteCreate(BaseModel):
    project_number: str
    title: str
    content: str
    tags: Optional[str] = ''
    created_by: Optional[str] = ''

class NoteResponse(NoteCreate):
    id: int
    created_date: datetime
    modified_date: datetime

class TaskCreate(BaseModel):
    project_number: str
    task_name: str
    description: Optional[str] = ''
    status: str = 'Pending'
    priority: str = 'Medium'
    assigned_to: Optional[str] = ''
    due_date: Optional[date] = None

class TaskResponse(TaskCreate):
    id: int
    completed_date: Optional[datetime] = None
    created_date: datetime
    modified_date: datetime

class CommentCreate(BaseModel):
    project_number: str
    entity_type: str
    entity_id: int
    comment_text: str
    author: str
    mentions: Optional[str] = ''

class CommentResponse(CommentCreate):
    id: int
    created_date: datetime

class ReportRequest(BaseModel):
    report_type: str
    project_numbers: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    format: str = 'PDF'
    include_charts: bool = True

class MLPrediction(BaseModel):
    project_number: str
    predicted_delay_days: Optional[int] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    factors: Optional[dict] = None

class DashboardConfig(BaseModel):
    dashboard_name: str
    layout: str
    widgets: str
    created_by: Optional[str] = ''
