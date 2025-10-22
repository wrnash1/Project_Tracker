// Main Application JavaScript

// API Base URL
const API_BASE = 'http://127.0.0.1:8000/api';

// Global state
const AppState = {
    currentTab: 'dashboard',
    selectedProject: null,
    projects: [],
    theme: 'light'
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initHeaderButtons();
    loadInitialData();
});

// Tab Management
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update button states
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(`${tabName}-tab`).classList.remove('hidden');

    // Update state
    AppState.currentTab = tabName;

    // Load tab-specific data
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'dashboard':
            if (typeof initDashboard === 'function') initDashboard();
            break;
        case 'projects':
            if (typeof loadProjects === 'function') loadProjects();
            break;
        case 'gantt':
            if (typeof loadGanttProjects === 'function') loadGanttProjects();
            break;
        case 'reports':
            if (typeof loadReportHistory === 'function') loadReportHistory();
            break;
        case 'tasks':
            if (typeof loadTasks === 'function') loadTasks();
            break;
        case 'notes':
            if (typeof loadNotes === 'function') loadNotes();
            break;
        case 'ml':
            if (typeof loadMLProjects === 'function') loadMLProjects();
            break;
    }
}

// Header Button Handlers
function initHeaderButtons() {
    document.getElementById('searchBtn').addEventListener('click', showSearch);
    document.getElementById('notificationsBtn').addEventListener('click', showNotifications);
    document.getElementById('settingsBtn').addEventListener('click', showSettings);
    document.getElementById('ttsBtn').addEventListener('click', toggleTTS);
}

function showSearch() {
    const searchTerm = prompt('Search projects:');
    if (searchTerm) {
        searchProjects(searchTerm);
    }
}

async function searchProjects(searchTerm) {
    try {
        const response = await fetch(`${API_BASE}/projects/search/${encodeURIComponent(searchTerm)}`);
        const results = await response.json();

        // Switch to projects tab and display results
        switchTab('projects');
        displaySearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed', 'error');
    }
}

function displaySearchResults(results) {
    // This will be implemented in projects.js
    if (typeof displayProjects === 'function') {
        displayProjects(results);
    }
}

function showNotifications() {
    showToast('No new notifications', 'info');
}

function showSettings() {
    const modal = createModal('Settings', `
        <div class="space-y-4">
            <div class="form-group">
                <label class="form-label">Theme</label>
                <select class="input-field w-full" id="themeSelect">
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Auto-save</label>
                <input type="checkbox" id="autoSave" checked>
            </div>
            <div class="form-group">
                <label class="form-label">TTS Enabled</label>
                <input type="checkbox" id="ttsEnabled" checked>
            </div>
            <button class="btn-primary" onclick="saveSettings()">Save Settings</button>
        </div>
    `);
    showModal(modal);
}

function saveSettings() {
    showToast('Settings saved successfully', 'success');
    closeModal();
}

function toggleTTS() {
    showToast('Text-to-Speech ready', 'info');
}

// Load Initial Data
async function loadInitialData() {
    try {
        // Check API health
        const response = await fetch(`${API_BASE.replace('/api', '')}/health`);
        const health = await response.json();
        console.log('API Status:', health);

        // Load projects for selectors
        await loadProjectsList();

        // Initialize dashboard
        if (typeof initDashboard === 'function') {
            initDashboard();
        }
    } catch (error) {
        console.error('Failed to load initial data:', error);
        showToast('Failed to connect to API', 'error');
    }
}

async function loadProjectsList() {
    try {
        const response = await fetch(`${API_BASE}/projects/`);
        AppState.projects = await response.json();

        // Populate project selectors
        populateProjectSelectors();
    } catch (error) {
        console.error('Failed to load projects:', error);
    }
}

function populateProjectSelectors() {
    const selectors = [
        document.getElementById('ganttProjectSelect'),
        document.getElementById('mlProjectSelect')
    ];

    selectors.forEach(selector => {
        if (selector) {
            selector.innerHTML = '<option value="">Select a project...</option>';
            AppState.projects.forEach(project => {
                const option = document.createElement('option');
                option.value = project.PROJECT_NUMBER;
                option.textContent = `${project.PROJECT_NUMBER} - ${project.PROJECT_NAME}`;
                selector.appendChild(option);
            });
        }
    });
}

// Modal Functions
function createModal(title, content) {
    return `
        <div class="modal">
            <div class="modal-header">
                ${title}
                <button onclick="closeModal()" class="float-right text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-content">
                ${content}
            </div>
        </div>
    `;
}

function showModal(html) {
    const overlay = document.getElementById('modalOverlay');
    overlay.innerHTML = html;
    overlay.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.add('hidden');
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast';

    const icon = type === 'success' ? 'check-circle' :
                 type === 'error' ? 'exclamation-circle' :
                 'info-circle';

    toast.innerHTML = `
        <i class="fas fa-${icon} mr-2"></i>
        ${message}
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Utility Functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getStatusBadgeClass(status) {
    const statusMap = {
        'ACTIVE': 'badge-active',
        'COMPLETED': 'badge-completed',
        'ON_HOLD': 'badge-on-hold'
    };
    return statusMap[status] || 'badge-active';
}

function getRiskBadgeClass(risk) {
    const riskMap = {
        'Low': 'badge-low',
        'Medium': 'badge-medium',
        'High': 'badge-high',
        'Critical': 'badge-critical'
    };
    return riskMap[risk] || 'badge-medium';
}

// Error Handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

// Export functions for use in other modules
window.AppState = AppState;
window.API_BASE = API_BASE;
window.showToast = showToast;
window.showModal = showModal;
window.closeModal = closeModal;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.getStatusBadgeClass = getStatusBadgeClass;
window.getRiskBadgeClass = getRiskBadgeClass;
