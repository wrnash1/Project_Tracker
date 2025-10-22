// ML Insights Tab Functionality

function loadMLProjects() {
    // Project selector is already populated by app.js
    document.getElementById('predictBtn')?.addEventListener('click', () => {
        const projectNumber = document.getElementById('mlProjectSelect').value;
        if (projectNumber) {
            predictDelay(projectNumber);
        } else {
            showToast('Please select a project', 'error');
        }
    });
}

async function predictDelay(projectNumber) {
    try {
        showLoadingSpinner('mlResults');

        // Get both delay prediction and risk classification
        const [delayResponse, riskResponse] = await Promise.all([
            fetch(`${API_BASE}/ml/predict-delay/${projectNumber}`),
            fetch(`${API_BASE}/ml/classify-risk/${projectNumber}`)
        ]);

        const delayData = await delayResponse.json();
        const riskData = await riskResponse.json();

        displayMLResults(delayData, riskData);
    } catch (error) {
        console.error('Failed to run ML prediction:', error);
        showToast('Failed to run ML prediction', 'error');
    }
}

function displayMLResults(delayData, riskData) {
    const container = document.getElementById('mlResults');

    const html = `
        <div class="grid grid-cols-2 gap-6">
            <!-- Delay Prediction Card -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="font-bold text-xl mb-4 flex items-center">
                    <i class="fas fa-clock text-blue-600 mr-2"></i>
                    Delay Prediction
                </h3>

                <div class="text-center mb-6">
                    <div class="text-5xl font-bold ${getDelayColorClass(delayData.predicted_delay_days)}">
                        ${delayData.predicted_delay_days || 0}
                    </div>
                    <div class="text-gray-600 mt-2">Days of Predicted Delay</div>
                    <div class="mt-2">
                        <span class="badge ${getRiskBadgeClass(delayData.risk_level)}">
                            ${delayData.risk_level}
                        </span>
                    </div>
                </div>

                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Confidence:</span>
                        <span class="font-semibold">${Math.round((delayData.confidence || 0) * 100)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(delayData.confidence || 0) * 100}%"></div>
                    </div>
                </div>
            </div>

            <!-- Risk Classification Card -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="font-bold text-xl mb-4 flex items-center">
                    <i class="fas fa-exclamation-triangle text-orange-600 mr-2"></i>
                    Risk Classification
                </h3>

                <div class="text-center mb-6">
                    <div class="text-5xl font-bold risk-${(riskData.risk_level || 'medium').toLowerCase()}">
                        ${riskData.risk_level || 'Unknown'}
                    </div>
                    <div class="text-gray-600 mt-2">Risk Level</div>
                </div>

                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-600">Confidence:</span>
                        <span class="font-semibold">${Math.round((riskData.confidence || 0) * 100)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(riskData.confidence || 0) * 100}%"></div>
                    </div>
                </div>
            </div>

            <!-- Contributing Factors -->
            <div class="col-span-2 bg-white rounded-lg shadow-md p-6">
                <h3 class="font-bold text-xl mb-4 flex items-center">
                    <i class="fas fa-chart-bar text-green-600 mr-2"></i>
                    Contributing Factors
                </h3>

                <div class="grid grid-cols-2 gap-4">
                    ${Object.entries(delayData.factors || {}).map(([key, value]) => `
                        <div class="border rounded p-3">
                            <div class="text-sm text-gray-600 mb-1">${formatFactorName(key)}</div>
                            <div class="font-bold text-lg">${formatFactorValue(key, value)}</div>
                            <div class="progress-bar mt-2 h-2">
                                <div class="progress-fill ${getFactorColorClass(value)}"
                                     style="width: ${Math.abs(value) * 100}%"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Actions -->
            <div class="col-span-2 bg-gray-50 rounded-lg p-6">
                <h3 class="font-bold text-lg mb-4">Recommended Actions</h3>
                <div class="space-y-2">
                    ${generateRecommendations(delayData, riskData).map(rec => `
                        <div class="flex items-start">
                            <i class="fas fa-lightbulb text-yellow-500 mt-1 mr-2"></i>
                            <span>${rec}</span>
                        </div>
                    `).join('')}
                </div>

                <div class="flex space-x-2 mt-6">
                    <button onclick="shareMLInsights('${delayData.project_number}')" class="btn-primary">
                        <i class="fas fa-share mr-2"></i>Share Insights
                    </button>
                    <button onclick="exportMLReport('${delayData.project_number}')" class="btn-primary">
                        <i class="fas fa-file-export mr-2"></i>Export Report
                    </button>
                    <button onclick="retrainModels()" class="btn-secondary">
                        <i class="fas fa-sync-alt mr-2"></i>Retrain Models
                    </button>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function getDelayColorClass(days) {
    if (days < 0) return 'text-green-600';
    if (days < 30) return 'text-yellow-600';
    if (days < 60) return 'text-orange-600';
    return 'text-red-600';
}

function getFactorColorClass(value) {
    if (value < -0.1) return 'bg-red-600';
    if (value < 0) return 'bg-yellow-600';
    return 'bg-green-600';
}

function formatFactorName(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatFactorValue(key, value) {
    if (key.includes('ratio') || key.includes('completion')) {
        return `${Math.round(value * 100)}%`;
    }
    if (key.includes('variance')) {
        return value > 0 ? `+${Math.round(value * 100)}%` : `${Math.round(value * 100)}%`;
    }
    return Math.round(value * 100) / 100;
}

function generateRecommendations(delayData, riskData) {
    const recommendations = [];

    if (delayData.predicted_delay_days > 30) {
        recommendations.push('Schedule a project review meeting to identify bottlenecks');
        recommendations.push('Consider reallocating resources to critical path tasks');
    }

    if (delayData.factors?.budget_variance < -0.1) {
        recommendations.push('Review budget allocation and request additional funding if needed');
    }

    if (delayData.factors?.ccr_completion < 0.5) {
        recommendations.push('Prioritize completion of pending CCRs');
    }

    if (delayData.factors?.order_completion < 0.5) {
        recommendations.push('Follow up on pending provisioning orders');
    }

    if (riskData.risk_level === 'High' || riskData.risk_level === 'Critical') {
        recommendations.push('Escalate to senior management for immediate attention');
        recommendations.push('Implement daily standup meetings for closer monitoring');
    }

    if (recommendations.length === 0) {
        recommendations.push('Project is on track - continue with current approach');
        recommendations.push('Maintain regular monitoring and status updates');
    }

    return recommendations;
}

async function shareMLInsights(projectNumber) {
    const modalContent = `
        <div class="space-y-4">
            <h3 class="font-bold text-lg">Share ML Insights</h3>

            <div class="form-group">
                <label class="form-label">Share via:</label>
                <div class="space-y-2">
                    <button onclick="shareViaSlack('${projectNumber}')" class="btn-primary w-full">
                        <i class="fab fa-slack mr-2"></i>Share to Slack
                    </button>
                    <button onclick="shareViaWebex('${projectNumber}')" class="btn-primary w-full">
                        <i class="fas fa-video mr-2"></i>Share to Webex
                    </button>
                    <button onclick="shareViaEmail('${projectNumber}')" class="btn-primary w-full">
                        <i class="fas fa-envelope mr-2"></i>Share via Email
                    </button>
                </div>
            </div>

            <div class="flex justify-end">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
            </div>
        </div>
    `;

    showModal(createModal('Share Insights', modalContent));
}

function shareViaSlack(projectNumber) {
    showToast('Opening Slack...', 'info');
    closeModal();
    // Integration would copy data to clipboard and open Slack
}

function shareViaWebex(projectNumber) {
    showToast('Opening Webex...', 'info');
    closeModal();
}

function shareViaEmail(projectNumber) {
    showToast('Opening email client...', 'info');
    closeModal();
}

function exportMLReport(projectNumber) {
    showToast('Exporting ML report...', 'info');
    // This would generate a PDF report with ML insights
}

async function retrainModels() {
    if (!confirm('Retraining models requires at least 100 completed projects. This may take several minutes. Continue?')) {
        return;
    }

    try {
        showToast('Retraining ML models...', 'info');

        const response = await fetch(`${API_BASE}/ml/retrain`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        showToast('Models retrained successfully', 'success');

        // Show training metrics
        const modalContent = `
            <div class="space-y-4">
                <h3 class="font-bold text-lg">Model Retraining Complete</h3>

                <div class="grid grid-cols-2 gap-4">
                    <div class="border rounded p-3">
                        <div class="text-sm text-gray-600">Delay Predictor</div>
                        <div class="font-bold">Final MAE: ${result.delay_predictor?.final_mae?.toFixed(4) || 'N/A'}</div>
                        <div class="text-sm">Training Samples: ${result.delay_predictor?.samples || 0}</div>
                    </div>

                    <div class="border rounded p-3">
                        <div class="text-sm text-gray-600">Risk Classifier</div>
                        <div class="font-bold">Final Accuracy: ${result.risk_classifier?.final_accuracy ? (result.risk_classifier.final_accuracy * 100).toFixed(2) + '%' : 'N/A'}</div>
                        <div class="text-sm">Training Samples: ${result.risk_classifier?.samples || 0}</div>
                    </div>
                </div>

                <div class="flex justify-end">
                    <button onclick="closeModal()" class="btn-primary">Close</button>
                </div>
            </div>
        `;

        showModal(createModal('Training Results', modalContent));
    } catch (error) {
        console.error('Failed to retrain models:', error);
        showToast('Failed to retrain models', 'error');
    }
}

async function viewModelInfo() {
    try {
        const response = await fetch(`${API_BASE}/ml/model-info`);
        const info = await response.json();

        const modalContent = `
            <div class="space-y-4">
                <h3 class="font-bold text-lg">ML Model Information</h3>

                <div class="grid grid-cols-2 gap-4">
                    <div class="border rounded p-4">
                        <h4 class="font-semibold mb-2">Delay Predictor</h4>
                        <div class="text-sm space-y-1">
                            <div><strong>Type:</strong> ${info.models?.delay_predictor?.type || 'N/A'}</div>
                            <div><strong>Architecture:</strong> ${info.models?.delay_predictor?.architecture || 'N/A'}</div>
                            <div><strong>Features:</strong> ${info.models?.delay_predictor?.features?.length || 0}</div>
                        </div>
                    </div>

                    <div class="border rounded p-4">
                        <h4 class="font-semibold mb-2">Risk Classifier</h4>
                        <div class="text-sm space-y-1">
                            <div><strong>Type:</strong> ${info.models?.risk_classifier?.type || 'N/A'}</div>
                            <div><strong>Architecture:</strong> ${info.models?.risk_classifier?.architecture || 'N/A'}</div>
                            <div><strong>Classes:</strong> ${info.models?.risk_classifier?.classes?.join(', ') || 'N/A'}</div>
                        </div>
                    </div>
                </div>

                <div>
                    <h4 class="font-semibold mb-2">Training History</h4>
                    <div class="max-h-64 overflow-y-auto">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Model</th>
                                    <th>Training Date</th>
                                    <th>Samples</th>
                                    <th>Accuracy</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${info.training_history?.map(h => `
                                    <tr>
                                        <td>${h.model_type}</td>
                                        <td>${formatDate(h.training_date)}</td>
                                        <td>${h.training_samples}</td>
                                        <td>${h.accuracy ? (h.accuracy * 100).toFixed(2) + '%' : 'N/A'}</td>
                                    </tr>
                                `).join('') || '<tr><td colspan="4">No training history</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="flex justify-end">
                    <button onclick="closeModal()" class="btn-primary">Close</button>
                </div>
            </div>
        `;

        showModal(createModal('Model Information', modalContent));
    } catch (error) {
        console.error('Failed to load model info:', error);
        showToast('Failed to load model info', 'error');
    }
}

// Export functions
window.loadMLProjects = loadMLProjects;
window.predictDelay = predictDelay;
window.shareMLInsights = shareMLInsights;
window.exportMLReport = exportMLReport;
window.retrainModels = retrainModels;
window.viewModelInfo = viewModelInfo;
