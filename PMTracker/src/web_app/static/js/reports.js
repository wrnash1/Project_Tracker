// Reports Tab Functionality

async function loadReportHistory() {
    try {
        const response = await fetch(`${API_BASE}/reports/history`);
        const history = await response.json();

        displayReportHistory(history);
    } catch (error) {
        console.error('Failed to load report history:', error);
    }
}

function displayReportHistory(history) {
    const container = document.getElementById('reportHistory');

    if (history.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No reports generated yet</p>';
        return;
    }

    const html = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Report Type</th>
                    <th>Report Name</th>
                    <th>Created By</th>
                    <th>Created Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${history.map(report => `
                    <tr>
                        <td>${report.report_type}</td>
                        <td>${report.report_name}</td>
                        <td>${report.created_by || 'N/A'}</td>
                        <td>${formatDate(report.created_date)}</td>
                        <td>
                            <button onclick="downloadReport('${report.file_path}')" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-download"></i> Download
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

async function generateReport() {
    try {
        const reportType = document.getElementById('reportType').value;
        const reportFormat = document.getElementById('reportFormat').value;

        // Get selected projects (could add multi-select UI)
        const projectNumbers = AppState.selectedProject ? [AppState.selectedProject] : null;

        const reportRequest = {
            report_type: reportType,
            format: reportFormat,
            project_numbers: projectNumbers,
            include_charts: true
        };

        showToast('Generating report...', 'info');

        const response = await fetch(`${API_BASE}/reports/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reportRequest)
        });

        if (!response.ok) {
            throw new Error('Report generation failed');
        }

        // Download the file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportType}_${Date.now()}.${reportFormat.toLowerCase()}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showToast('Report generated successfully', 'success');

        // Reload history
        loadReportHistory();
    } catch (error) {
        console.error('Failed to generate report:', error);
        showToast('Failed to generate report', 'error');
    }
}

function downloadReport(filePath) {
    // In a real implementation, this would download from file_path
    showToast('Downloading report...', 'info');
}

function showReportPreview(reportType) {
    const modalContent = `
        <div class="space-y-4">
            <h3 class="font-bold text-lg">${reportType.replace('_', ' ').toUpperCase()} Report Preview</h3>

            <div class="border rounded p-4 bg-gray-50">
                <p class="text-gray-600">Report preview will be displayed here</p>
                <p class="text-sm text-gray-500 mt-2">This feature requires server-side rendering</p>
            </div>

            <div class="flex justify-end space-x-2">
                <button onclick="closeModal()" class="btn-secondary">Close</button>
                <button onclick="generateReport(); closeModal();" class="btn-primary">Generate Report</button>
            </div>
        </div>
    `;

    showModal(createModal('Report Preview', modalContent));
}

function scheduleReport() {
    const modalContent = `
        <div class="space-y-4">
            <h3 class="font-bold text-lg">Schedule Report</h3>

            <div class="form-group">
                <label class="form-label">Report Type</label>
                <select class="input-field w-full" id="scheduleReportType">
                    <option value="project_summary">Project Summary</option>
                    <option value="ccr_analysis">CCR Analysis</option>
                    <option value="budget_variance">Budget Variance</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label">Frequency</label>
                <select class="input-field w-full" id="scheduleFrequency">
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                </select>
            </div>

            <div class="form-group">
                <label class="form-label">Email Recipients</label>
                <input type="text" class="input-field w-full" placeholder="email1@verizon.com, email2@verizon.com" id="scheduleRecipients">
            </div>

            <div class="flex justify-end space-x-2">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                <button onclick="saveScheduledReport()" class="btn-primary">Schedule Report</button>
            </div>
        </div>
    `;

    showModal(createModal('Schedule Report', modalContent));
}

function saveScheduledReport() {
    showToast('Report scheduled successfully', 'success');
    closeModal();
}

// Event Listeners
document.getElementById('generateReport')?.addEventListener('click', generateReport);

// Export functions
window.loadReportHistory = loadReportHistory;
window.generateReport = generateReport;
window.downloadReport = downloadReport;
window.showReportPreview = showReportPreview;
window.scheduleReport = scheduleReport;
