# Verizon Tracker - Quick Reference Card

**Version 2.0.0** | One-page guide for quick access

---

## Starting the Application

```bash
cd /home/wrnash1/development/Project_Tracker
./run.sh
```

Open browser: `http://localhost:8501`

---

## Default Login Credentials

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `admin123` | Associate Director | Full system |
| `pmuser` | `pm123` | Sr. Project Manager | PM features |

---

## Quick Workflows

### Create a New Project (PM)
1. Click **"New Project"** in sidebar
2. Fill in: Name*, CCR/NFID*, Status*
3. Add optional fields
4. Click **"Create Project"**
5. Go to **"Sync Data"** → Click **"Sync to Master"**

### Take a KPI Snapshot (PM)
1. Go to **"My Dashboard"**
2. Expand **"Take KPI Snapshot"**
3. Select project
4. Enter snapshot date and metrics
5. Click **"Save Snapshot"**
6. Sync when ready

### View All Projects (Any Role)
1. Click **"All Projects"** in sidebar
2. Use filters: Status, Program, Type, PM
3. Search by name or CCR/NFID
4. Click **"Download as CSV"** to export

### Process Syncs (Admin)
1. Go to **"Process Sync Inbox"**
2. Review pending sync files
3. Click **"Process All Syncs"** or individual files
4. Verify completion

### Import Data (Admin)
1. Go to **"Import Data"**
2. Download template (first time)
3. Fill in data
4. Upload CSV or Excel file
5. Review validation
6. Click **"Import Projects"**

### Run Reports (Director/Engineer)
1. Go to **"Reports"**
2. Select report type
3. View charts and tables
4. Click **"Download Full Data (CSV)"**

### Create Users (Admin)
1. Go to **"Admin Panel"**
2. Click **"User Management"** tab
3. Fill in user form
4. Select role
5. Click **"Create User"**

---

## Page Quick Reference

| Page | Icon | Who | Purpose |
|------|------|-----|---------|
| Home | 🏠 | All | Dashboard overview |
| My Dashboard | 📊 | PM | Edit projects, KPIs |
| New Project | ➕ | PM | Create projects |
| Sync Data | 🔄 | PM | Push to master |
| Team Dashboard | 👥 | Admin/Director | Team analytics |
| Import Data | 📁 | Admin | Bulk import |
| Process Sync Inbox | 📥 | Admin | Merge syncs |
| Admin Panel | ⚙️ | Admin | Users/config |
| Reports | 📈 | All | Advanced reports |
| All Projects | 📋 | All | Read-only view |

---

## Report Types

1. **Executive Summary** - High-level overview, status distribution
2. **Project Status Report** - Detailed status breakdown with charts
3. **KPI Dashboard** - Budget/schedule metrics, trends over time
4. **Timeline Analysis** - Duration stats, Gantt chart
5. **Program Performance** - Comparison across programs

---

## Project Status Values

- **Active** - Currently in progress
- **On Hold** - Temporarily paused
- **Completed** - Finished successfully
- **Cancelled** - Discontinued

---

## Common Filters

**All Projects Page:**
- Status (multi-select)
- Program (multi-select)
- Project Type (multi-select)
- Project Manager (multi-select)
- Search box (name or CCR/NFID)

**Team Dashboard:**
- Status filter
- Date range (coming soon)

---

## Keyboard Shortcuts

- **Tab** - Move between form fields
- **Enter** - Submit forms
- **Ctrl+F** - Browser search (within page)
- **Ctrl+S** - Save (in editable tables)

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Can't log in | Check username/password case-sensitivity |
| Access denied | Check your role permissions |
| Nothing to sync | Create/edit a project first |
| Import validation error | Download and use template |
| Page not loading | Clear browser cache, restart app |
| Sync failed | Check sync_inbox folder exists |
| No data in reports | Create projects/KPIs first |

---

## Essential Fields for New Projects

**Required (*)**
- Project Name*
- CCR/NFID* (must be unique)
- Status* (Active, On Hold, Completed, Cancelled)

**Recommended**
- Customer
- CLLI
- Site Address
- Project Manager (auto-assigned)
- Program
- Project Type

---

## Data Export Options

**From All Projects:**
- Apply filters
- Click "Download as CSV"

**From Reports:**
- Select report
- Click "Download Full Data (CSV)"

**From Team Dashboard:**
- Apply filters
- Click "Export to CSV"

---

## Sync Workflow

```
1. PM creates/edits projects locally
   ↓
2. PM clicks "Sync to Master"
   ↓
3. JSON bundle created in sync_inbox/
   ↓
4. Admin processes sync inbox
   ↓
5. Data merged into master database
   ↓
6. All users see updated data
```

---

## System Configuration (Admin)

**Common Settings:**
- `kpi_threshold_green` - KPI % for green status (default: 90)
- `kpi_threshold_yellow` - KPI % for yellow status (default: 70)
- `business_days_per_week` - For calculations (default: 5)
- `ai_model_name` - AI model for future features

---

## User Roles & Access

| Feature | PM | Engineer | Admin | Director |
|---------|----|-----------| ------|----------|
| View Projects | Own | All | All | All |
| Edit Projects | Own | No | Own | No |
| Create Projects | Yes | No | Yes | No |
| Sync Data | Yes | No | Yes | No |
| Import Data | No | No | Yes | No |
| Process Syncs | No | No | Yes | No |
| User Management | No | No | Yes | No |
| Team Dashboard | No | No | Yes | Yes |
| Reports | Yes | Yes | Yes | Yes |

---

## Import Template Columns

**Required:**
- name
- ccr_nfid
- pm_id
- status

**Optional:**
- customer, clli, site_address, current_queue, system_type
- program_id, project_type_id, phase
- project_start_date, project_complete_date
- scorecard_*, wbs_code, budget_amount

**Tips:**
- Download template first
- Use User ID Reference for pm_id
- Status: Active, On Hold, Completed, or Cancelled
- Duplicates auto-skipped

---

## Metric Cards Explained

**My Dashboard:**
- **Active Projects** - Your current active projects
- **Pending Sync** - Items waiting to sync
- **Completed** - Your completed projects
- **Total Projects** - All your projects

**All Projects:**
- **Total Projects** - All in master database
- **Active** - Currently in progress
- **Completed** - Finished projects
- **On Hold** - Paused projects

---

## File Locations

```
data/
├── master_users.db          # User accounts
├── master_projects.db       # All projects
├── config.db                # System settings
├── user_2_local.db          # PM local database
├── sync_inbox/              # Pending syncs
└── sync_archive/            # Processed syncs
```

---

## Best Practices

**For PMs:**
- Sync daily
- Take monthly KPI snapshots
- Use consistent CCR format
- Fill in as many fields as possible

**For Admins:**
- Process syncs daily
- Review Team Dashboard weekly
- Use import template
- Document config changes

**For All Users:**
- Use search for quick access
- Apply filters to narrow results
- Export data for presentations
- Bookmark favorite pages

---

## Support Resources

📖 **Full Documentation:**
- [USER_GUIDE.md](USER_GUIDE.md) - Complete manual
- [FEATURES.md](FEATURES.md) - Feature list
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide

🆘 **Get Help:**
- Check in-app help text
- Contact your administrator
- Report bugs on GitHub

---

## Version Info

- **Version:** 2.0.0
- **Released:** October 27, 2025
- **Test Coverage:** 100% (7/7 tests)
- **Status:** Production Ready

---

**Print this page for quick reference at your desk!**
