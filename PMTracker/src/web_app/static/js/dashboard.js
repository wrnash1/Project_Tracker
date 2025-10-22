// Dashboard Tab Functionality

function initDashboard() {
    loadDashboardWidgets();
}

async function loadDashboardWidgets() {
    try {
        const response = await fetch(`${API_BASE}/projects/`);
        const projects = await response.json();

        displayDashboardStats(projects);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function displayDashboardStats(projects) {
    const grid = document.getElementById('dashboardGrid');

    const activeProjects = projects.filter(p => p.PROJECT_STATUS === 'ACTIVE').length;
    const completedProjects = projects.filter(p => p.PROJECT_STATUS === 'COMPLETED').length;
    const totalBudget = projects.reduce((sum, p) => sum + (p.BUDGET || 0), 0);

    grid.innerHTML = `
        <div class="grid grid-cols-3 gap-6 mb-6">
            <div class="stat-card">
                <div class="stat-value">${activeProjects}</div>
                <div class="stat-label">Active Projects</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(to bottom right, #3b82f6, #1d4ed8);">
                <div class="stat-value">${completedProjects}</div>
                <div class="stat-label">Completed Projects</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(to bottom right, #10b981, #047857);">
                <div class="stat-value">${formatCurrency(totalBudget)}</div>
                <div class="stat-label">Total Budget</div>
            </div>
        </div>
        <div class="grid grid-cols-2 gap-6">
            <div class="widget">
                <div class="widget-header">Recent Projects</div>
                <div class="widget-content">
                    ${projects.slice(0, 5).map(p => `
                        <div class="mb-2 pb-2 border-b">
                            <div class="font-semibold">${p.PROJECT_NAME}</div>
                            <div class="text-sm text-gray-500">${p.PROJECT_NUMBER}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="widget">
                <div class="widget-header">Quick Actions</div>
                <div class="widget-content space-y-2">
                    <button onclick="document.querySelector('[data-tab=\\"reports\\"]').click()" class="btn-primary w-full">Generate Report</button>
                    <button onclick="document.querySelector('[data-tab=\\"tasks\\"]').click()" class="btn-primary w-full">View Tasks</button>
                    <button onclick="document.querySelector('[data-tab=\\"ml\\"]').click()" class="btn-primary w-full">ML Insights</button>
                </div>
            </div>
        </div>
    `;
}

window.initDashboard = initDashboard;
