import oracledb
from typing import List, Dict, Optional
from datetime import datetime
from core.config_manager import ConfigManager

class OracleManager:
    """Manages Oracle database connections and queries (Read-only)"""

    def __init__(self):
        self.config = ConfigManager()
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish connection to Oracle database"""
        try:
            oracle_config = self.config.get_oracle_config()
            self.connection = oracledb.connect(
                user=oracle_config['user'],
                password=oracle_config['password'],
                dsn=oracle_config['host'],
                mode=oracledb.DEFAULT_AUTH
            )
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Oracle connection error: {e}")
            return False

    def disconnect(self):
        """Close Oracle database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute a SELECT query and return results as list of dicts"""
        if not self.connection:
            self.connect()

        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            columns = [col[0] for col in self.cursor.description]
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            print(f"Query execution error: {e}")
            return []

    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Fetch projects from GS_WFM_NF_PROJECTS"""
        query = """
            SELECT
                PROJECT_NUMBER,
                PROJECT_NAME,
                PROJECT_TYPE,
                PROJECT_STATUS,
                PM_NAME,
                PM_EMAIL,
                START_DATE,
                END_DATE,
                BUDGET,
                ACTUAL_COST,
                REGION,
                MARKET,
                PRIORITY,
                CREATED_DATE,
                MODIFIED_DATE
            FROM GS_WFM_NF_PROJECTS
            WHERE 1=1
        """

        if filters:
            if filters.get('status'):
                query += f" AND PROJECT_STATUS = :status"
            if filters.get('pm_name'):
                query += f" AND PM_NAME LIKE :pm_name"
            if filters.get('region'):
                query += f" AND REGION = :region"
            if filters.get('market'):
                query += f" AND MARKET = :market"

        query += " ORDER BY CREATED_DATE DESC"

        return self.execute_query(query, filters)

    def get_project_by_number(self, project_number: str) -> Optional[Dict]:
        """Fetch a single project by project number"""
        query = """
            SELECT
                PROJECT_NUMBER,
                PROJECT_NAME,
                PROJECT_TYPE,
                PROJECT_STATUS,
                PM_NAME,
                PM_EMAIL,
                START_DATE,
                END_DATE,
                BUDGET,
                ACTUAL_COST,
                REGION,
                MARKET,
                PRIORITY,
                CREATED_DATE,
                MODIFIED_DATE
            FROM GS_WFM_NF_PROJECTS
            WHERE PROJECT_NUMBER = :project_number
        """

        results = self.execute_query(query, {'project_number': project_number})
        return results[0] if results else None

    def get_ccrs_data(self, project_number: str) -> List[Dict]:
        """Fetch CCR data for a project from GS_CCP_CCRS"""
        query = """
            SELECT
                CCR_NUMBER,
                CCR_STATUS,
                CCR_TYPE,
                SUBMIT_DATE,
                COMPLETION_DATE,
                ESTIMATED_HOURS,
                ACTUAL_HOURS
            FROM GS_CCP_CCRS
            WHERE PROJECT_NUMBER = :project_number
            ORDER BY SUBMIT_DATE DESC
        """

        return self.execute_query(query, {'project_number': project_number})

    def get_provisioning_orders(self, project_number: str) -> List[Dict]:
        """Fetch provisioning orders from GS_PMRA_PROV_ORDERS"""
        query = """
            SELECT
                ORDER_NUMBER,
                ORDER_STATUS,
                ORDER_TYPE,
                SUBMIT_DATE,
                COMPLETION_DATE,
                CIRCUIT_ID,
                LOCATION
            FROM GS_PMRA_PROV_ORDERS
            WHERE PROJECT_NUMBER = :project_number
            ORDER BY SUBMIT_DATE DESC
        """

        return self.execute_query(query, {'project_number': project_number})

    def get_project_metrics(self, project_number: str) -> Dict:
        """Calculate project metrics from Oracle data"""
        project = self.get_project_by_number(project_number)
        if not project:
            return {}

        ccrs = self.get_ccrs_data(project_number)
        orders = self.get_provisioning_orders(project_number)

        metrics = {
            'total_ccrs': len(ccrs),
            'completed_ccrs': len([c for c in ccrs if c['CCR_STATUS'] == 'COMPLETED']),
            'total_orders': len(orders),
            'completed_orders': len([o for o in orders if o['ORDER_STATUS'] == 'COMPLETED']),
            'budget_variance': (project['BUDGET'] - project['ACTUAL_COST']) if project['BUDGET'] and project['ACTUAL_COST'] else 0,
            'estimated_hours': sum([c['ESTIMATED_HOURS'] or 0 for c in ccrs]),
            'actual_hours': sum([c['ACTUAL_HOURS'] or 0 for c in ccrs])
        }

        return metrics

    def search_projects(self, search_term: str) -> List[Dict]:
        """Search projects by name or project number"""
        query = """
            SELECT
                PROJECT_NUMBER,
                PROJECT_NAME,
                PROJECT_TYPE,
                PROJECT_STATUS,
                PM_NAME,
                START_DATE,
                END_DATE
            FROM GS_WFM_NF_PROJECTS
            WHERE UPPER(PROJECT_NAME) LIKE :search_term
               OR UPPER(PROJECT_NUMBER) LIKE :search_term
            ORDER BY PROJECT_NAME
        """

        search_param = f"%{search_term.upper()}%"
        return self.execute_query(query, {'search_term': search_param})

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
