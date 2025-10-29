#!/usr/bin/env python3
"""
Generate sample data for Verizon Tracker testing
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vtrack.database import MasterProjectsDB, MasterUsersDB, LocalProjectsDB

# Sample data
PROJECT_NAMES = [
    "5G Tower Installation", "Network Fiber Upgrade", "Data Center Migration",
    "Cloud Infrastructure", "Security System Overhaul", "Backup System Implementation",
    "Network Monitoring Setup", "VoIP Migration", "WiFi Expansion",
    "Server Virtualization", "Storage Upgrade", "Disaster Recovery Site",
    "Network Segmentation", "Firewall Replacement", "Load Balancer Setup",
    "Database Migration", "Application Modernization", "API Gateway Implementation",
    "Microservices Migration", "Container Platform Setup"
]

CUSTOMERS = [
    "Verizon Business", "Verizon Wireless", "Verizon Enterprise",
    "Federal Government", "State of California", "City of New York",
    "Fortune 500 Corp A", "Fortune 500 Corp B", "Healthcare System",
    "University Network", "Retail Chain", "Financial Services"
]

SITES = [
    "New York Metro", "Los Angeles Central", "Chicago Loop", "Houston Center",
    "Phoenix Downtown", "Philadelphia Main", "San Antonio Hub", "San Diego Bay",
    "Dallas Fort Worth", "San Jose Tech", "Austin Innovation", "Jacksonville Port"
]

PHASES = ["Planning", "Design", "Implementation", "Testing", "Deployment", "Closeout"]

SYSTEM_TYPES = ["Fiber", "Wireless", "Data Center", "Cloud", "Security", "Network"]

QUEUES = ["Engineering", "Installation", "Testing", "Documentation", "Customer Acceptance"]

def generate_sample_projects(count=50):
    """Generate sample projects in master database"""
    
    print(f"Generating {count} sample projects...")
    
    # Connect to databases
    projects_db = MasterProjectsDB()
    projects_db.connect()
    
    users_db = MasterUsersDB()
    users_db.connect()
    
    # Get users, programs, and types
    users = users_db.fetchall("SELECT user_id FROM users WHERE role = 'Sr. Project Manager'")
    if not users:
        print("No Project Managers found! Create users first.")
        return
    
    user_ids = [u['user_id'] for u in users]
    
    programs = projects_db.fetchall("SELECT program_id FROM programs")
    program_ids = [p['program_id'] for p in programs] if programs else [None]
    
    types = projects_db.fetchall("SELECT type_id FROM project_types")
    type_ids = [t['type_id'] for t in types] if types else [None]
    
    # Generate projects
    created = 0
    skipped = 0
    
    for i in range(count):
        # Generate unique CCR/NFID
        ccr_nfid = f"CCR-{random.randint(10000, 99999)}"
        
        # Check if exists
        existing = projects_db.fetchone(
            "SELECT project_id FROM projects WHERE ccr_nfid = ?",
            (ccr_nfid,)
        )
        
        if existing:
            skipped += 1
            continue
        
        # Random project data
        name = random.choice(PROJECT_NAMES) + f" - {random.randint(1, 999)}"
        customer = random.choice(CUSTOMERS)
        clli = f"CLLI-{random.randint(1000, 9999)}"
        site_address = f"{random.randint(100, 9999)} {random.choice(SITES)}"
        phase = random.choice(PHASES)
        system_type = random.choice(SYSTEM_TYPES)
        current_queue = random.choice(QUEUES)
        
        # Status distribution: 60% Active, 20% Completed, 15% On Hold, 5% Cancelled
        status_roll = random.random()
        if status_roll < 0.60:
            status = "Active"
        elif status_roll < 0.80:
            status = "Completed"
        elif status_roll < 0.95:
            status = "On Hold"
        else:
            status = "Cancelled"
        
        # Random dates
        start_date = datetime.now() - timedelta(days=random.randint(30, 365))
        if status == "Completed":
            complete_date = start_date + timedelta(days=random.randint(30, 180))
        elif random.random() < 0.3:  # 30% have planned completion
            complete_date = start_date + timedelta(days=random.randint(60, 240))
        else:
            complete_date = None
        
        try:
            projects_db.execute("""
                INSERT INTO projects (
                    name, ccr_nfid, program_id, project_type_id, pm_id,
                    status, phase, notes, customer, clli, site_address,
                    system_type, current_queue, project_start_date, project_complete_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, ccr_nfid,
                random.choice(program_ids) if program_ids else None,
                random.choice(type_ids) if type_ids else None,
                random.choice(user_ids),
                status, phase,
                f"Sample project {i+1} for testing purposes",
                customer, clli, site_address, system_type, current_queue,
                start_date.strftime('%Y-%m-%d'),
                complete_date.strftime('%Y-%m-%d') if complete_date else None
            ))
            created += 1
            
        except Exception as e:
            print(f"Error creating project {i+1}: {e}")
            skipped += 1
    
    projects_db.close()
    users_db.close()
    
    print(f"\n✅ Sample data generation complete!")
    print(f"   Created: {created} projects")
    print(f"   Skipped: {skipped} (duplicates or errors)")


def generate_sample_kpis():
    """Generate sample KPI snapshots for existing projects"""
    
    print("Generating sample KPI snapshots...")
    
    projects_db = MasterProjectsDB()
    projects_db.connect()
    
    # Get all projects
    projects = projects_db.fetchall("SELECT project_id FROM projects")
    
    if not projects:
        print("No projects found! Generate projects first.")
        return
    
    budget_statuses = ["On Budget", "Over Budget", "Under Budget"]
    schedule_statuses = ["On Schedule", "Behind Schedule", "Ahead of Schedule"]
    
    created = 0
    
    # Create 1-3 KPI snapshots per project
    for project in projects:
        num_snapshots = random.randint(1, 3)
        
        for i in range(num_snapshots):
            snapshot_date = datetime.now() - timedelta(days=random.randint(1, 90))
            on_time_percent = random.randint(70, 100)
            
            try:
                projects_db.execute("""
                    INSERT INTO kpi_snapshots (
                        project_id, snapshot_date, budget_status, schedule_status,
                        on_time_percent, notes
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    project['project_id'],
                    snapshot_date.strftime('%Y-%m-%d'),
                    random.choice(budget_statuses),
                    random.choice(schedule_statuses),
                    on_time_percent,
                    f"KPI snapshot {i+1}"
                ))
                created += 1
                
            except Exception as e:
                print(f"Error creating KPI: {e}")
    
    projects_db.close()
    
    print(f"✅ Created {created} KPI snapshots")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Verizon Tracker - Sample Data Generator")
    print("="*60 + "\n")
    
    generate_sample_projects(50)
    generate_sample_kpis()
    
    print("\n" + "="*60)
    print("Done! Your database now has sample data for testing.")
    print("="*60 + "\n")
