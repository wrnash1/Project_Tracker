// Gantt Chart Tab Functionality

let ganttInitialized = false;

function loadGanttProjects() {
    // Populate project selector (already done in app.js)
    document.getElementById('ganttProjectSelect')?.addEventListener('change', (e) => {
        if (e.target.value) {
            loadGanttChart(e.target.value);
        }
    });
}

async function loadGanttChart(projectNumber) {
    try {
        showLoadingSpinner('ganttChart');

        const response = await fetch(`${API_BASE}/gantt/${projectNumber}`);
        const ganttData = await response.json();

        renderGanttChart(ganttData);
    } catch (error) {
        console.error('Failed to load Gantt chart:', error);
        showToast('Failed to load Gantt chart', 'error');
    }
}

function renderGanttChart(data) {
    if (!ganttInitialized) {
        initializeGantt();
        ganttInitialized = true;
    }

    // Clear existing data
    gantt.clearAll();

    // Load data
    gantt.parse({
        data: data.data,
        links: data.links
    });

    showToast('Gantt chart loaded successfully', 'success');
}

function initializeGantt() {
    // Configure Gantt
    gantt.config.date_format = "%Y-%m-%d %H:%i:%s";
    gantt.config.xml_date = "%Y-%m-%d";
    gantt.config.scale_unit = "day";
    gantt.config.date_scale = "%d %M";
    gantt.config.min_column_width = 50;
    gantt.config.scale_height = 54;
    gantt.config.row_height = 30;

    // Configure columns
    gantt.config.columns = [
        {name: "text", label: "Task", tree: true, width: 200},
        {name: "start_date", label: "Start", align: "center", width: 80},
        {name: "end_date", label: "End", align: "center", width: 80},
        {name: "progress", label: "Progress", align: "center", width: 60, template: function(task) {
            return Math.round(task.progress * 100) + "%";
        }}
    ];

    // Enable plugins
    gantt.plugins({
        tooltip: true,
        marker: true,
        critical_path: true
    });

    // Add today marker
    gantt.addMarker({
        start_date: new Date(),
        css: "today",
        text: "Today",
        title: "Today: " + new Date().toDateString()
    });

    // Initialize Gantt
    gantt.init("ganttChart");
}

async function exportGanttToPDF() {
    try {
        gantt.exportToPDF({
            name: "project-gantt.pdf"
        });
        showToast('Gantt chart exported to PDF', 'success');
    } catch (error) {
        console.error('Failed to export Gantt:', error);
        showToast('Failed to export Gantt chart', 'error');
    }
}

async function getCriticalPath() {
    try {
        const projectNumber = document.getElementById('ganttProjectSelect').value;
        if (!projectNumber) {
            showToast('Please select a project', 'error');
            return;
        }

        const response = await fetch(`${API_BASE}/gantt/${projectNumber}/critical-path`);
        const data = await response.json();

        const modalContent = `
            <div class="space-y-4">
                <h3 class="font-bold text-lg">Critical Path Analysis</h3>
                <p><strong>Total Duration:</strong> ${data.total_duration} days</p>

                <div class="mt-4">
                    <h4 class="font-semibold mb-2">Critical Items:</h4>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Number</th>
                                <th>Duration (days)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.critical_path.map(item => `
                                <tr>
                                    <td>${item.type}</td>
                                    <td>${item.number}</td>
                                    <td>${item.duration}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <div class="flex justify-end mt-4">
                    <button onclick="closeModal()" class="btn-secondary">Close</button>
                </div>
            </div>
        `;

        showModal(createModal('Critical Path', modalContent));
    } catch (error) {
        console.error('Failed to get critical path:', error);
        showToast('Failed to calculate critical path', 'error');
    }
}

// Export functions
window.loadGanttProjects = loadGanttProjects;
window.loadGanttChart = loadGanttChart;
window.exportGanttToPDF = exportGanttToPDF;
window.getCriticalPath = getCriticalPath;
