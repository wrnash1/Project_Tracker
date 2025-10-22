from fastapi import APIRouter, HTTPException
from typing import List, Dict
from core.oracle_manager import OracleManager
from datetime import datetime

router = APIRouter()

@router.get("/{project_number}")
async def get_gantt_data(project_number: str):
    """Get Gantt chart data for a project"""
    try:
        with OracleManager() as db:
            # Get project details
            project = db.get_project_by_number(project_number)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # Get CCRs and provisioning orders
            ccrs = db.get_ccrs_data(project_number)
            orders = db.get_provisioning_orders(project_number)

            # Transform data into Gantt format
            gantt_tasks = []

            # Add project as main task
            gantt_tasks.append({
                'id': f'project_{project_number}',
                'text': project['PROJECT_NAME'],
                'start_date': project['START_DATE'].isoformat() if project.get('START_DATE') else None,
                'end_date': project['END_DATE'].isoformat() if project.get('END_DATE') else None,
                'type': 'project',
                'progress': 0
            })

            # Add CCRs as tasks
            for idx, ccr in enumerate(ccrs):
                gantt_tasks.append({
                    'id': f'ccr_{ccr["CCR_NUMBER"]}',
                    'text': f'CCR {ccr["CCR_NUMBER"]} - {ccr["CCR_TYPE"]}',
                    'start_date': ccr['SUBMIT_DATE'].isoformat() if ccr.get('SUBMIT_DATE') else None,
                    'end_date': ccr['COMPLETION_DATE'].isoformat() if ccr.get('COMPLETION_DATE') else None,
                    'parent': f'project_{project_number}',
                    'type': 'task',
                    'progress': 1.0 if ccr['CCR_STATUS'] == 'COMPLETED' else 0.5
                })

            # Add provisioning orders as tasks
            for idx, order in enumerate(orders):
                gantt_tasks.append({
                    'id': f'order_{order["ORDER_NUMBER"]}',
                    'text': f'Order {order["ORDER_NUMBER"]} - {order["ORDER_TYPE"]}',
                    'start_date': order['SUBMIT_DATE'].isoformat() if order.get('SUBMIT_DATE') else None,
                    'end_date': order['COMPLETION_DATE'].isoformat() if order.get('COMPLETION_DATE') else None,
                    'parent': f'project_{project_number}',
                    'type': 'task',
                    'progress': 1.0 if order['ORDER_STATUS'] == 'COMPLETED' else 0.5
                })

            return {
                'data': gantt_tasks,
                'links': []
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_number}/critical-path")
async def get_critical_path(project_number: str):
    """Calculate and return critical path for project"""
    try:
        with OracleManager() as db:
            ccrs = db.get_ccrs_data(project_number)
            orders = db.get_provisioning_orders(project_number)

            # Simple critical path: longest chain of dependencies
            # This is a simplified version; actual critical path would need dependency data
            critical_items = []

            # Sort by duration (descending)
            all_items = []
            for ccr in ccrs:
                if ccr.get('SUBMIT_DATE') and ccr.get('COMPLETION_DATE'):
                    duration = (ccr['COMPLETION_DATE'] - ccr['SUBMIT_DATE']).days
                    all_items.append({
                        'type': 'CCR',
                        'number': ccr['CCR_NUMBER'],
                        'duration': duration
                    })

            for order in orders:
                if order.get('SUBMIT_DATE') and order.get('COMPLETION_DATE'):
                    duration = (order['COMPLETION_DATE'] - order['SUBMIT_DATE']).days
                    all_items.append({
                        'type': 'Order',
                        'number': order['ORDER_NUMBER'],
                        'duration': duration
                    })

            # Sort by duration
            all_items.sort(key=lambda x: x['duration'], reverse=True)

            return {
                'critical_path': all_items[:5],  # Top 5 longest duration items
                'total_duration': sum([item['duration'] for item in all_items[:5]])
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
