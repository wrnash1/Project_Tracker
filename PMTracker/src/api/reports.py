from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from models import ReportRequest
from core.oracle_manager import OracleManager
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import openpyxl
from pathlib import Path
from datetime import datetime
import tempfile

router = APIRouter()

@router.post("/generate")
async def generate_report(report: ReportRequest):
    """Generate a report based on request parameters"""
    try:
        with OracleManager() as db:
            # Gather data based on report type
            if report.report_type == 'project_summary':
                data = _generate_project_summary(db, report)
            elif report.report_type == 'ccr_analysis':
                data = _generate_ccr_analysis(db, report)
            elif report.report_type == 'budget_variance':
                data = _generate_budget_variance(db, report)
            else:
                raise HTTPException(status_code=400, detail="Invalid report type")

            # Generate file based on format
            if report.format.upper() == 'PDF':
                file_path = _create_pdf_report(data, report.report_type)
            elif report.format.upper() == 'EXCEL':
                file_path = _create_excel_report(data, report.report_type)
            else:
                raise HTTPException(status_code=400, detail="Invalid format")

            return FileResponse(
                file_path,
                filename=f"{report.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{report.format.lower()}",
                media_type='application/octet-stream'
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _generate_project_summary(db, report: ReportRequest):
    """Generate project summary data"""
    data = {'projects': []}

    if report.project_numbers:
        for proj_num in report.project_numbers:
            project = db.get_project_by_number(proj_num)
            if project:
                metrics = db.get_project_metrics(proj_num)
                data['projects'].append({
                    'project': project,
                    'metrics': metrics
                })
    else:
        filters = {}
        if report.start_date:
            filters['start_date'] = report.start_date
        if report.end_date:
            filters['end_date'] = report.end_date
        projects = db.get_projects(filters)
        for project in projects:
            metrics = db.get_project_metrics(project['PROJECT_NUMBER'])
            data['projects'].append({
                'project': project,
                'metrics': metrics
            })

    return data

def _generate_ccr_analysis(db, report: ReportRequest):
    """Generate CCR analysis data"""
    data = {'ccrs': []}

    if report.project_numbers:
        for proj_num in report.project_numbers:
            ccrs = db.get_ccrs_data(proj_num)
            data['ccrs'].extend(ccrs)

    return data

def _generate_budget_variance(db, report: ReportRequest):
    """Generate budget variance data"""
    data = {'variances': []}

    if report.project_numbers:
        for proj_num in report.project_numbers:
            project = db.get_project_by_number(proj_num)
            if project and project.get('BUDGET') and project.get('ACTUAL_COST'):
                variance = project['BUDGET'] - project['ACTUAL_COST']
                variance_pct = (variance / project['BUDGET']) * 100 if project['BUDGET'] > 0 else 0
                data['variances'].append({
                    'project_number': proj_num,
                    'project_name': project['PROJECT_NAME'],
                    'budget': project['BUDGET'],
                    'actual_cost': project['ACTUAL_COST'],
                    'variance': variance,
                    'variance_percentage': variance_pct
                })

    return data

def _create_pdf_report(data, report_type: str):
    """Create PDF report"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_path = temp_file.name
    temp_file.close()

    # Create PDF
    doc = SimpleDocTemplate(temp_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(f"{report_type.replace('_', ' ').title()} Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))

    # Add data based on report type
    if report_type == 'project_summary':
        for item in data['projects']:
            project = item['project']
            metrics = item['metrics']

            # Project header
            header = Paragraph(f"<b>{project['PROJECT_NAME']}</b> ({project['PROJECT_NUMBER']})", styles['Heading2'])
            elements.append(header)
            elements.append(Spacer(1, 0.1 * inch))

            # Project details table
            proj_data = [
                ['PM Name', project.get('PM_NAME', 'N/A')],
                ['Status', project.get('PROJECT_STATUS', 'N/A')],
                ['Budget', f"${project.get('BUDGET', 0):,.2f}"],
                ['Actual Cost', f"${project.get('ACTUAL_COST', 0):,.2f}"],
                ['CCRs', f"{metrics.get('completed_ccrs', 0)}/{metrics.get('total_ccrs', 0)}"],
                ['Orders', f"{metrics.get('completed_orders', 0)}/{metrics.get('total_orders', 0)}"]
            ]

            table = Table(proj_data, colWidths=[2 * inch, 4 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))

    # Build PDF
    doc.build(elements)
    return temp_path

def _create_excel_report(data, report_type: str):
    """Create Excel report"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_path = temp_file.name
    temp_file.close()

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = report_type

    # Add headers and data based on report type
    if report_type == 'project_summary':
        headers = ['Project Number', 'Project Name', 'PM Name', 'Status', 'Budget', 'Actual Cost', 'Variance', 'CCRs', 'Orders']
        ws.append(headers)

        for item in data['projects']:
            project = item['project']
            metrics = item['metrics']
            row = [
                project.get('PROJECT_NUMBER', ''),
                project.get('PROJECT_NAME', ''),
                project.get('PM_NAME', ''),
                project.get('PROJECT_STATUS', ''),
                project.get('BUDGET', 0),
                project.get('ACTUAL_COST', 0),
                metrics.get('budget_variance', 0),
                f"{metrics.get('completed_ccrs', 0)}/{metrics.get('total_ccrs', 0)}",
                f"{metrics.get('completed_orders', 0)}/{metrics.get('total_orders', 0)}"
            ]
            ws.append(row)

    # Save workbook
    wb.save(temp_path)
    return temp_path

@router.get("/history")
async def get_report_history():
    """Get report generation history"""
    try:
        from core.sqlite_manager import SQLiteManager
        with SQLiteManager() as db:
            history = db.execute_query("SELECT * FROM report_history ORDER BY created_date DESC LIMIT 50")
            return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
