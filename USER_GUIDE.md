# Verizon Tracker - User Guide

**Version 2.0.0**

Welcome to Verizon Tracker! This guide will help you get started and make the most of the application.

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [For Project Managers](#for-project-managers)
3. [For Administrators](#for-administrators)
4. [For Directors/Engineers](#for-directorsengin eers)
5. [Common Tasks](#common-tasks)
6. [Tips & Tricks](#tips--tricks)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### First Time Login

1. **Start the Application**
   ```bash
   cd /home/wrnash1/development/Project_Tracker
   ./run.sh
   ```

2. **Open Your Browser**
   - Navigate to: `http://localhost:8501`

3. **Login with Default Credentials**
   - **Admin:** username: `admin`, password: `admin123`
   - **PM User:** username: `pmuser`, password: `pm123`

4. **Change Your Password** (Recommended)
   - Contact your administrator to set a secure password

### Understanding Your Role

The application has **4 user roles**, each with different permissions:

| Role | Access Level | Main Purpose |
|------|-------------|--------------|
| **Sr. Project Manager** | Project management | Create/edit projects, sync data |
| **Principal Engineer** | Read-only | View projects, generate reports |
| **Associate Director** | Admin | User management, system config, data import |
| **Director** | Executive | View dashboards, reports, analytics |

---

## 👨‍💼 For Project Managers

### Your Main Pages

1. **Home** - Dashboard overview
2. **My Dashboard** - Your projects
3. **New Project** - Create projects
4. **Sync Data** - Push to master database
5. **All Projects** - View all (read-only)
6. **Reports** - Analytics
7. **AI Assistant** - Help (coming soon)

### Creating a New Project

1. Click **"New Project"** in sidebar
2. Fill in required fields:
   - **Project Name** * (required)
   - **CCR/NFID** * (unique identifier)
   - **Status** * (Active, On Hold, Completed, Cancelled)
3. Fill in optional fields as needed
4. Click **"Create Project"**
5. Project is saved to your **local database**

**Important:** New projects are only in your local database until you sync!

### Managing Your Projects

1. Go to **"My Dashboard"**
2. View all your projects in an editable table
3. **Edit inline:** Click on cells to update
4. **Save Changes:** Click "Save Changes" button
5. Changes are tracked for sync

### Taking KPI Snapshots

KPI snapshots record point-in-time metrics for reporting.

1. Go to **"My Dashboard"**
2. Scroll to **"KPI Snapshots"** section
3. Click **"Take KPI Snapshot"** expander
4. Select project
5. Enter snapshot data:
   - Snapshot Date
   - Budget Status
   - Schedule Status
   - On-Time Completion %
   - Notes
6. Click **"Save Snapshot"**

**Use Case:** Take monthly snapshots to track project health over time.

### Managing Dependencies

Define relationships between projects (e.g., Project B depends on Project A).

1. Go to **"My Dashboard"**
2. Scroll to **"Project Dependencies"** section
3. Click **"Manage Dependencies"** expander
4. Select:
   - **Dependent Project** (the one that waits)
   - **Depends On Project** (must complete first)
   - **Dependency Type** (usually Finish-to-Start)
5. Add notes if needed
6. Click **"Add Dependency"**

### Syncing Your Data

**Why Sync?** Your changes are local until you sync them to the master database.

1. Go to **"Sync Data"** page
2. Review **pending changes**:
   - Projects (new or updated)
   - KPI Snapshots
   - Dependencies
   - Contacts
3. Click **"Sync to Master"** button
4. Your data is packaged and sent to the sync inbox
5. Admin will process and merge into master database

**Best Practice:** Sync at least once per day.

---

## 👨‍💻 For Administrators

### Your Main Responsibilities

1. User management
2. System configuration
3. Data import/export
4. Sync processing
5. System monitoring

### User Management

**Creating New Users:**

1. Go to **"Admin Panel"**
2. Click **"User Management"** tab
3. Fill in the form:
   - Username (unique)
   - Full Name
   - Email
   - Role
   - Reports To (optional)
   - Initial Password (8+ characters)
4. Click **"Create User"**

**Viewing Users:**
- User list shows all active users
- See username, role, reporting hierarchy
- Check who reports to whom

### System Configuration

**Editing Settings:**

1. Go to **"Admin Panel"**
2. Click **"Configuration"** tab
3. Expand a setting
4. Enter new value
5. Click **"Update"**

**Common Settings:**
- `ai_model_name` - AI model for future features
- `kpi_threshold_green` - KPI % for green status (default: 90)
- `kpi_threshold_yellow` - KPI % for yellow status (default: 70)
- `business_days_per_week` - For calculations (default: 5)

### Importing Data

**Bulk Import from Excel/CSV:**

1. Go to **"Import Data"** page
2. **Download template** (recommended for first time)
3. Fill in your data:
   - Required: name, ccr_nfid, pm_id, status
   - Optional: customer, clli, site_address, etc.
4. **Upload file** (CSV or Excel)
5. **Review preview** and validation results
6. Fix any errors shown
7. Click **"Import Projects"**
8. Monitor progress bar
9. Review import summary

**Tips:**
- Use User ID Reference table to get pm_id values
- Status must be: Active, On Hold, Completed, or Cancelled
- CCR/NFID must be unique
- Duplicates are automatically skipped

### Processing Syncs

**Merging PM Data into Master:**

1. Go to **"Process Sync Inbox"** page
2. View **pending sync files**
3. Review each file:
   - See username and timestamp
   - Check number of items
   - Preview project names
4. **Option A:** Click **"Process All Syncs"** for batch processing
5. **Option B:** Click **"Process"** on individual files
6. Monitor progress
7. Files are automatically moved to archive

**Best Practice:** Process syncs at least once per day.

### Team Dashboard

**Monitoring Team Performance:**

1. Go to **"Team Dashboard"** page
2. View **executive summary**:
   - Total projects
   - Active/Completed/On Hold counts
   - Number of PMs
3. Analyze **charts**:
   - Projects by Status (pie chart)
   - Projects by Type (bar chart)
   - Top 10 PMs (horizontal bar)
   - Projects by Program
4. Review **PM Performance table**
5. Check **Recent Activity**
6. Use **filters** to drill down
7. **Export** data as CSV

---

## 📊 For Directors/Engineers

### Viewing Projects

1. Go to **"All Projects"** page
2. View **summary metrics** at top
3. Use **filters**:
   - Status (Active, On Hold, etc.)
   - Program
   - Project Type
   - Project Manager
4. Use **search box** for specific projects
5. **Export** filtered results to CSV

### Running Reports

**Report Types Available:**

1. **Executive Summary**
   - High-level overview
   - Status distribution
   - Summary by type

2. **Project Status Report**
   - Status breakdown charts
   - Phase distribution
   - Detailed status table

3. **KPI Dashboard**
   - Budget vs schedule metrics
   - KPI trends over time
   - Recent snapshots table

4. **Timeline Analysis**
   - Project duration statistics
   - Duration distribution histogram
   - Gantt-style timeline

5. **Program Performance**
   - Program comparison
   - Projects by program and status
   - Program details drill-down

**How to Run a Report:**

1. Go to **"Reports"** page
2. Select **report type** from dropdown
3. View **charts and tables**
4. Use **filters** if available
5. **Export** data to CSV

---

## 📝 Common Tasks

### Changing Project Status

1. Go to **"My Dashboard"** (PM) or **"All Projects"** (view only)
2. Find the project
3. Click the **Status** cell
4. Select new status from dropdown
5. Click **"Save Changes"** (PM only)

### Searching for a Project

1. Go to **"All Projects"** page
2. Type in **search box** (searches name and CCR/NFID)
3. Results filter automatically
4. Clear search to see all again

### Exporting Data

**From All Projects:**
1. Apply desired filters
2. Click **"Download as CSV"** button
3. File downloads with timestamp in name

**From Reports:**
1. Select and view report
2. Click **"Download Full Data (CSV)"**
3. Get complete dataset for that report

**From Team Dashboard:**
1. Apply filters if desired
2. Click **"Export to CSV"**
3. Get team dashboard data

---

## 💡 Tips & Tricks

### For Everyone

1. **Use Search:** The search box on All Projects is very fast
2. **Bookmark Pages:** Bookmark your most-used pages in your browser
3. **Keyboard:** Use Tab to move between form fields quickly
4. **Filters Stack:** You can use multiple filters at once
5. **CSV Opens in Excel:** Downloaded CSV files open directly in Excel

### For Project Managers

1. **Batch Edit:** Edit multiple fields before clicking "Save Changes"
2. **CCR Format:** Use a consistent format for CCR/NFID (e.g., CCR-12345)
3. **Regular Snapshots:** Take KPI snapshots monthly for best trends
4. **Sync Often:** Sync at least daily to keep master database current
5. **Dependencies:** Only add critical dependencies to keep it simple

### For Administrators

1. **Template First:** Always download and use the import template
2. **Test Import:** Import a small test file first (2-3 rows)
3. **Process Daily:** Process sync inbox at least once per day
4. **Monitor Metrics:** Check Team Dashboard weekly
5. **Backup Config:** Document any config changes you make

---

## 🔧 Troubleshooting

### Login Issues

**Problem:** Can't log in
- ✅ Check username (case-sensitive)
- ✅ Check password (case-sensitive)
- ✅ Try default accounts first
- ✅ Contact admin for password reset

**Problem:** "Access Denied" on a page
- ✅ Check your role permissions
- ✅ Some pages are role-restricted
- ✅ Contact admin if you need different access

### Project Issues

**Problem:** Can't create project
- ✅ Check all required fields are filled (*)
- ✅ CCR/NFID must be unique
- ✅ Check for error messages
- ✅ Try a different CCR/NFID

**Problem:** Changes not saving
- ✅ Click "Save Changes" button
- ✅ Check for error messages
- ✅ Refresh page and try again
- ✅ Check your internet connection

### Sync Issues

**Problem:** Nothing to sync
- ✅ Create or edit a project first
- ✅ Make sure changes are saved locally
- ✅ Check sync status in My Dashboard

**Problem:** Sync failed
- ✅ Check error message
- ✅ Verify network drive is accessible
- ✅ Try again in a few minutes
- ✅ Contact admin if persists

### Import Issues

**Problem:** Validation errors
- ✅ Check required columns exist
- ✅ Verify status values are valid
- ✅ Check PM IDs exist in system
- ✅ Look for duplicate CCR/NFIDs
- ✅ Use the template file

**Problem:** Some rows skipped
- ✅ Check for duplicate CCR/NFIDs
- ✅ Skipped rows already exist
- ✅ This is normal and safe

### Report Issues

**Problem:** No data in reports
- ✅ Create some projects first
- ✅ Take KPI snapshots for KPI reports
- ✅ Add dates for Timeline Analysis
- ✅ Assign programs for Program Performance

**Problem:** Charts not showing
- ✅ Refresh the page
- ✅ Check browser console for errors
- ✅ Try a different browser
- ✅ Clear browser cache

---

## 📞 Getting Help

### Documentation
- **README.md** - Quick start guide
- **FEATURES.md** - Complete feature list
- **STATUS.md** - Current version status
- **USER_GUIDE.md** - This document

### Support
- **GitHub Issues** - Report bugs or request features
- **Admin Team** - Contact your system administrator
- **Documentation** - Check inline help text in the app

---

## 🎓 Training Resources

### Quick Start Checklist

**First Day:**
- [ ] Login successfully
- [ ] Navigate to your role's main pages
- [ ] Understand the sidebar navigation
- [ ] View existing projects

**First Week (PM):**
- [ ] Create your first project
- [ ] Edit a project
- [ ] Take a KPI snapshot
- [ ] Sync your data

**First Week (Admin):**
- [ ] Create a test user
- [ ] Import test data
- [ ] Process a sync file
- [ ] View team dashboard

**First Week (All):**
- [ ] Run a report
- [ ] Export data to CSV
- [ ] Use filters and search
- [ ] Bookmark favorite pages

---

## 🎯 Best Practices

### Data Entry
1. Be consistent with naming conventions
2. Fill in as many fields as possible
3. Use standard abbreviations
4. Keep notes concise but informative
5. Update status promptly

### Project Management
1. Create projects as soon as they're approved
2. Update status at least weekly
3. Take monthly KPI snapshots
4. Document dependencies clearly
5. Sync data daily

### Reporting
1. Run reports weekly
2. Export data for presentations
3. Track trends over time
4. Share insights with team
5. Archive important reports

### Administration
1. Process syncs daily
2. Back up data regularly (manual for now)
3. Monitor system health via Admin Panel
4. Review user list monthly
5. Document configuration changes

---

**Enjoy using Verizon Tracker!** 🎉

For additional help, contact your system administrator or refer to the technical documentation.

---

*Version 2.0.0 - October 26, 2025*
