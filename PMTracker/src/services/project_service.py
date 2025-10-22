from typing import List, Dict, Optional
from core.oracle_manager import OracleManager
from core.sqlite_manager import SQLiteManager
from datetime import datetime

class ProjectService:
    """Business logic layer for project operations"""

    def __init__(self):
        self.oracle_mgr = OracleManager()
        self.sqlite_mgr = SQLiteManager()

    def get_project_overview(self, project_number: str) -> Dict:
        """Get comprehensive project overview with all related data"""
        try:
            with self.oracle_mgr as oracle_db:
                # Get project details
                project = oracle_db.get_project_by_number(project_number)
                if not project:
                    return None

                # Get metrics
                metrics = oracle_db.get_project_metrics(project_number)

                # Get CCRs and orders
                ccrs = oracle_db.get_ccrs_data(project_number)
                orders = oracle_db.get_provisioning_orders(project_number)

            with self.sqlite_mgr as sqlite_db:
                # Get user-generated data
                notes = sqlite_db.get_notes(project_number)
                tasks = sqlite_db.get_tasks(project_number)

            return {
                'project': project,
                'metrics': metrics,
                'ccrs': ccrs,
                'orders': orders,
                'notes': notes,
                'tasks': tasks,
                'summary': self._generate_summary(project, metrics, ccrs, orders)
            }
        except Exception as e:
            print(f"Error getting project overview: {e}")
            return None

    def _generate_summary(self, project: Dict, metrics: Dict, ccrs: List, orders: List) -> str:
        """Generate natural language project summary"""
        summary = []

        # Status
        status = project.get('PROJECT_STATUS', 'Unknown')
        summary.append(f"Project is currently {status.lower()}.")

        # Budget
        if project.get('BUDGET') and project.get('ACTUAL_COST'):
            variance = project['BUDGET'] - project['ACTUAL_COST']
            if variance < 0:
                summary.append(f"Project is over budget by ${abs(variance):,.2f}.")
            elif variance > 0:
                summary.append(f"Project is under budget by ${variance:,.2f}.")
            else:
                summary.append("Project is on budget.")

        # CCRs
        total_ccrs = metrics.get('total_ccrs', 0)
        completed_ccrs = metrics.get('completed_ccrs', 0)
        if total_ccrs > 0:
            ccr_pct = (completed_ccrs / total_ccrs) * 100
            summary.append(f"{completed_ccrs} out of {total_ccrs} CCRs completed ({ccr_pct:.1f}%).")

        # Orders
        total_orders = metrics.get('total_orders', 0)
        completed_orders = metrics.get('completed_orders', 0)
        if total_orders > 0:
            order_pct = (completed_orders / total_orders) * 100
            summary.append(f"{completed_orders} out of {total_orders} orders completed ({order_pct:.1f}%).")

        return ' '.join(summary)

    def calculate_completion_percentage(self, project_number: str) -> float:
        """Calculate overall project completion percentage"""
        try:
            with self.oracle_mgr as oracle_db:
                metrics = oracle_db.get_project_metrics(project_number)

            total_items = metrics.get('total_ccrs', 0) + metrics.get('total_orders', 0)
            completed_items = metrics.get('completed_ccrs', 0) + metrics.get('completed_orders', 0)

            if total_items == 0:
                return 0.0

            return (completed_items / total_items) * 100
        except Exception as e:
            print(f"Error calculating completion: {e}")
            return 0.0

    def get_project_health_score(self, project_number: str) -> Dict:
        """Calculate project health score based on multiple factors"""
        try:
            with self.oracle_mgr as oracle_db:
                project = oracle_db.get_project_by_number(project_number)
                metrics = oracle_db.get_project_metrics(project_number)

            score = 100
            factors = []

            # Budget health (30 points)
            if project.get('BUDGET') and project.get('ACTUAL_COST'):
                variance_pct = ((project['BUDGET'] - project['ACTUAL_COST']) / project['BUDGET']) * 100
                if variance_pct < -20:  # Over budget by 20%+
                    score -= 30
                    factors.append({'factor': 'Budget', 'score': 0, 'max': 30, 'status': 'Critical'})
                elif variance_pct < -10:  # Over budget by 10-20%
                    score -= 15
                    factors.append({'factor': 'Budget', 'score': 15, 'max': 30, 'status': 'Warning'})
                elif variance_pct < 0:  # Over budget by 0-10%
                    score -= 5
                    factors.append({'factor': 'Budget', 'score': 25, 'max': 30, 'status': 'Acceptable'})
                else:
                    factors.append({'factor': 'Budget', 'score': 30, 'max': 30, 'status': 'Good'})

            # CCR completion (35 points)
            ccr_completion = metrics.get('completed_ccrs', 0) / max(metrics.get('total_ccrs', 1), 1)
            ccr_score = int(ccr_completion * 35)
            score = score - (35 - ccr_score)
            factors.append({'factor': 'CCR Completion', 'score': ccr_score, 'max': 35, 'status': self._get_status(ccr_completion)})

            # Order completion (35 points)
            order_completion = metrics.get('completed_orders', 0) / max(metrics.get('total_orders', 1), 1)
            order_score = int(order_completion * 35)
            score = score - (35 - order_score)
            factors.append({'factor': 'Order Completion', 'score': order_score, 'max': 35, 'status': self._get_status(order_completion)})

            # Determine overall health
            if score >= 90:
                health = 'Excellent'
            elif score >= 75:
                health = 'Good'
            elif score >= 60:
                health = 'Fair'
            elif score >= 40:
                health = 'Poor'
            else:
                health = 'Critical'

            return {
                'score': max(0, min(100, score)),
                'health': health,
                'factors': factors
            }
        except Exception as e:
            print(f"Error calculating health score: {e}")
            return {'score': 0, 'health': 'Unknown', 'factors': []}

    def _get_status(self, completion_ratio: float) -> str:
        """Get status based on completion ratio"""
        if completion_ratio >= 0.9:
            return 'Excellent'
        elif completion_ratio >= 0.7:
            return 'Good'
        elif completion_ratio >= 0.5:
            return 'Acceptable'
        elif completion_ratio >= 0.3:
            return 'Warning'
        else:
            return 'Critical'

    def get_trending_projects(self, limit: int = 10) -> List[Dict]:
        """Get projects with significant recent activity"""
        try:
            with self.oracle_mgr as oracle_db:
                projects = oracle_db.get_projects()

            # Sort by modification date
            sorted_projects = sorted(
                projects,
                key=lambda p: p.get('MODIFIED_DATE', datetime.min),
                reverse=True
            )

            return sorted_projects[:limit]
        except Exception as e:
            print(f"Error getting trending projects: {e}")
            return []

    def export_project_data(self, project_number: str, format: str = 'json') -> Dict:
        """Export all project data in specified format"""
        overview = self.get_project_overview(project_number)

        if format == 'json':
            return overview
        elif format == 'csv':
            # Convert to CSV-friendly format
            return self._convert_to_csv(overview)
        else:
            return overview

    def _convert_to_csv(self, overview: Dict) -> str:
        """Convert project overview to CSV format"""
        # This would return CSV formatted string
        # Implementation depends on specific requirements
        return "CSV export not yet implemented"
