#!/usr/bin/env python3
"""
Comprehensive test suite for Verizon Tracker
Tests all major functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vtrack.database import (
    MasterUsersDB, MasterProjectsDB, LocalProjectsDB, ConfigDB,
    initialize_all_databases
)
from src.vtrack import auth, sync

def test_database_initialization():
    """Test 1: Database Initialization"""
    print("\n" + "="*60)
    print("TEST 1: Database Initialization")
    print("="*60)
    
    try:
        initialize_all_databases()
        print("✅ Databases initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def test_user_authentication():
    """Test 2: User Authentication"""
    print("\n" + "="*60)
    print("TEST 2: User Authentication")
    print("="*60)
    
    try:
        # Test admin login
        admin_user = auth.authenticate_user("admin", "admin123")
        if admin_user:
            print(f"✅ Admin authentication successful: {admin_user['full_name']}")
        else:
            print("❌ Admin authentication failed")
            return False
        
        # Test PM login
        pm_user = auth.authenticate_user("pmuser", "pm123")
        if pm_user:
            print(f"✅ PM authentication successful: {pm_user['full_name']}")
        else:
            print("❌ PM authentication failed")
            return False
        
        # Test invalid login
        invalid = auth.authenticate_user("baduser", "badpass")
        if not invalid:
            print("✅ Invalid authentication correctly rejected")
        else:
            print("❌ Invalid authentication incorrectly accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False


def test_project_operations():
    """Test 3: Project CRUD Operations"""
    print("\n" + "="*60)
    print("TEST 3: Project Operations")
    print("="*60)

    try:
        projects_db = MasterProjectsDB()
        projects_db.connect()

        # Count projects
        result = projects_db.fetchone("SELECT COUNT(*) as count FROM projects")
        count = result['count']
        print(f"✅ Found {count} projects in master database")

        # Test simple query first
        projects = projects_db.fetchall("SELECT name, status FROM projects LIMIT 5")
        print(f"✅ Successfully queried {len(projects)} projects")

        # Test filter by status
        active = projects_db.fetchall("SELECT name FROM projects WHERE status = 'Active' LIMIT 3")
        print(f"✅ Successfully filtered {len(active)} active projects")

        projects_db.close()
        return True

    except Exception as e:
        print(f"❌ Project operations test failed: {e}")
        return False


def test_kpi_operations():
    """Test 4: KPI Operations"""
    print("\n" + "="*60)
    print("TEST 4: KPI Operations")
    print("="*60)
    
    try:
        projects_db = MasterProjectsDB()
        projects_db.connect()
        
        # Count KPIs
        result = projects_db.fetchone("SELECT COUNT(*) as count FROM kpi_snapshots")
        count = result['count']
        print(f"✅ Found {count} KPI snapshots in database")
        
        # Test KPI query
        kpis = projects_db.fetchall("""
            SELECT k.snapshot_date, k.budget_status, p.name
            FROM kpi_snapshots k
            JOIN projects p ON k.project_id = p.project_id
            LIMIT 5
        """)
        
        print(f"✅ Successfully queried {len(kpis)} KPI snapshots")
        
        projects_db.close()
        return True
        
    except Exception as e:
        print(f"❌ KPI operations test failed: {e}")
        return False


def test_config_operations():
    """Test 5: Configuration Operations"""
    print("\n" + "="*60)
    print("TEST 5: Configuration Operations")
    print("="*60)
    
    try:
        config_db = ConfigDB()
        config_db.connect()
        
        # Get a config value
        version = config_db.get_config("app_version")
        print(f"✅ Retrieved config value 'app_version': {version}")
        
        # Set a new value
        config_db.set_config("test_key", "test_value")
        retrieved = config_db.get_config("test_key")
        
        if retrieved == "test_value":
            print("✅ Config set/get operations successful")
        else:
            print("❌ Config set/get operations failed")
            return False
        
        config_db.close()
        return True
        
    except Exception as e:
        print(f"❌ Config operations test failed: {e}")
        return False


def test_sync_operations():
    """Test 6: Sync Operations"""
    print("\n" + "="*60)
    print("TEST 6: Sync Operations")
    print("="*60)
    
    try:
        # Create a local database for testing
        local_db = LocalProjectsDB(2)  # PM user ID
        local_db.connect()
        local_db.initialize_schema()
        
        # Get pending counts
        counts = sync.get_pending_sync_counts(local_db)
        print(f"✅ Pending sync counts: {counts}")
        
        local_db.close()
        return True
        
    except Exception as e:
        print(f"❌ Sync operations test failed: {e}")
        return False


def test_user_management():
    """Test 7: User Management"""
    print("\n" + "="*60)
    print("TEST 7: User Management")
    print("="*60)
    
    try:
        users_db = MasterUsersDB()
        users_db.connect()
        
        # Get all users
        users = users_db.fetchall("SELECT * FROM users")
        print(f"✅ Found {len(users)} users in system")
        
        # Check roles
        roles = {}
        for user in users:
            role = user['role']
            roles[role] = roles.get(role, 0) + 1
        
        print("✅ User distribution by role:")
        for role, count in roles.items():
            print(f"   - {role}: {count}")
        
        users_db.close()
        return True
        
    except Exception as e:
        print(f"❌ User management test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("VERIZON TRACKER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("User Authentication", test_user_authentication),
        ("Project Operations", test_project_operations),
        ("KPI Operations", test_kpi_operations),
        ("Configuration Operations", test_config_operations),
        ("Sync Operations", test_sync_operations),
        ("User Management", test_user_management),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
