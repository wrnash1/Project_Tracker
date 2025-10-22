from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import ProjectResponse, ProjectMetrics
from core.oracle_manager import OracleManager

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    status: Optional[str] = Query(None),
    pm_name: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    market: Optional[str] = Query(None)
):
    """Get all projects with optional filters"""
    try:
        filters = {}
        if status:
            filters['status'] = status
        if pm_name:
            filters['pm_name'] = f"%{pm_name}%"
        if region:
            filters['region'] = region
        if market:
            filters['market'] = market

        with OracleManager() as db:
            projects = db.get_projects(filters)
            return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_number}", response_model=ProjectResponse)
async def get_project(project_number: str):
    """Get a single project by project number"""
    try:
        with OracleManager() as db:
            project = db.get_project_by_number(project_number)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_number}/metrics", response_model=ProjectMetrics)
async def get_project_metrics(project_number: str):
    """Get project metrics including CCRs and provisioning orders"""
    try:
        with OracleManager() as db:
            metrics = db.get_project_metrics(project_number)
            if not metrics:
                raise HTTPException(status_code=404, detail="Project not found")
            return metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_number}/ccrs")
async def get_project_ccrs(project_number: str):
    """Get CCR data for a project"""
    try:
        with OracleManager() as db:
            ccrs = db.get_ccrs_data(project_number)
            return ccrs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_number}/orders")
async def get_project_orders(project_number: str):
    """Get provisioning orders for a project"""
    try:
        with OracleManager() as db:
            orders = db.get_provisioning_orders(project_number)
            return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{search_term}")
async def search_projects(search_term: str):
    """Search projects by name or project number"""
    try:
        with OracleManager() as db:
            results = db.search_projects(search_term)
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
