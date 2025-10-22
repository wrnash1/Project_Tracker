// Projects Tab Functionality

async function loadProjects(filters = {}) {
    try {
        showLoadingSpinner('projectsTable');

        // Build query string
        const params = new URLSearchParams(filters);
        const response = await fetch(`${API_BASE}/projects/?${params}`);
        const projects = await response.json();

        displayProjects(projects);
    } catch (error) {
        console.error('Failed to load projects:', error);
        showToast('Failed to load projects', 'error');
    }
}

function displayProjects(projects) {
    const container = document.getElementById('projectsTable');

    if (projects.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500 py-8">No projects found</p>';
        return;
    }

    const table = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Project Number</th>
                    <th>Project Name</th>
                    <th>PM Name</th>
                    <th>Status</th>
                    <th>Budget</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${projects.map(project => `
                    <tr onclick="viewProjectDetails('${project.PROJECT_NUMBER}')">
                        <td>${project.PROJECT_NUMBER}</td>
                        <td>${project.PROJECT_NAME}</td>
                        <td>${project.PM_NAME || 'N/A'}</td>
                        <td><span class="badge ${getStatusBadgeClass(project.PROJECT_STATUS)}">${project.PROJECT_STATUS || 'N/A'}</span></td>
                        <td>${formatCurrency(project.BUDGET || 0)}</td>
                        <td>${formatDate(project.START_DATE)}</td>
                        <td>${formatDate(project.END_DATE)}</td>
                        <td>
                            <button onclick="event.stopPropagation(); viewProjectDetails('${project.PROJECT_NUMBER}')" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = table;
}

async function viewProjectDetails(projectNumber) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectNumber}`);
        const project = await response.json();

        const metricsResponse = await fetch(`${API_BASE}/projects/${projectNumber}/metrics`);
        const metrics = await metricsResponse.json();

        const modalContent = `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <strong>Project Number:</strong> ${project.PROJECT_NUMBER}
                    </div>
                    <div>
                        <strong>Project Name:</strong> ${project.PROJECT_NAME}
                    </div>
                    <div>
                        <strong>PM Name:</strong> ${project.PM_NAME || 'N/A'}
                    </div>
                    <div>
                        <strong>Status:</strong> <span class="badge ${getStatusBadgeClass(project.PROJECT_STATUS)}">${project.PROJECT_STATUS}</span>
                    </div>
                    <div>
                        <strong>Budget:</strong> ${formatCurrency(project.BUDGET || 0)}
                    </div>
                    <div>
                        <strong>Actual Cost:</strong> ${formatCurrency(project.ACTUAL_COST || 0)}
                    </div>
                    <div>
                        <strong>Budget Variance:</strong> ${formatCurrency(metrics.budget_variance || 0)}
                    </div>
                    <div>
                        <strong>Region:</strong> ${project.REGION || 'N/A'}
                    </div>
                </div>

                <div class="border-t pt-4">
                    <h3 class="font-bold mb-2">Metrics</h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <strong>CCRs:</strong> ${metrics.completed_ccrs || 0} / ${metrics.total_ccrs || 0}
                        </div>
                        <div>
                            <strong>Orders:</strong> ${metrics.completed_orders || 0} / ${metrics.total_orders || 0}
                        </div>
                        <div>
                            <strong>Estimated Hours:</strong> ${metrics.estimated_hours || 0}
                        </div>
                        <div>
                            <strong>Actual Hours:</strong> ${metrics.actual_hours || 0}
                        </div>
                    </div>
                </div>

                <div class="flex space-x-2 pt-4 border-t">
                    <button onclick="viewGanttChart('${project.PROJECT_NUMBER}')" class="btn-primary">
                        <i class="fas fa-chart-gantt mr-2"></i>View Gantt
                    </button>
                    <button onclick="runMLPrediction('${project.PROJECT_NUMBER}')" class="btn-primary">
                        <i class="fas fa-brain mr-2"></i>ML Prediction
                    </button>
                    <button onclick="closeModal()" class="btn-secondary">Close</button>
                </div>
            </div>
        `;

        showModal(createModal('Project Details', modalContent));
    } catch (error) {
        console.error('Failed to load project details:', error);
        showToast('Failed to load project details', 'error');
    }
}

function viewGanttChart(projectNumber) {
    closeModal();
    document.querySelector('[data-tab="gantt"]').click();
    document.getElementById('ganttProjectSelect').value = projectNumber;
    loadGanttChart(projectNumber);
}

function runMLPrediction(projectNumber) {
    closeModal();
    document.querySelector('[data-tab="ml"]').click();
    document.getElementById('mlProjectSelect').value = projectNumber;
    predictDelay(projectNumber);
}

function showLoadingSpinner(elementId) {
    document.getElementById(elementId).innerHTML = `
        <div class="flex justify-center items-center py-8">
            <div class="spinner"></div>
        </div>
    `;
}

// Event Listeners
document.getElementById('refreshProjects')?.addEventListener('click', () => {
    const filters = {};
    const status = document.getElementById('statusFilter').value;
    if (status) filters.status = status;
    loadProjects(filters);
});

document.getElementById('projectSearch')?.addEventListener('input', (e) => {
    const searchTerm = e.target.value;
    if (searchTerm.length >= 3) {
        searchProjects(searchTerm);
    } else if (searchTerm.length === 0) {
        loadProjects();
    }
});

document.getElementById('statusFilter')?.addEventListener('change', (e) => {
    const filters = {};
    if (e.target.value) filters.status = e.target.value;
    loadProjects(filters);
});

// Export functions
window.loadProjects = loadProjects;
window.displayProjects = displayProjects;
window.viewProjectDetails = viewProjectDetails;
