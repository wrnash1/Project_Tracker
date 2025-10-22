// Tasks Tab Functionality

async function loadTasks(filters = {}) {
    try {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${API_BASE}/tasks/?${params}`);
        const tasks = await response.json();

        displayTasks(tasks);
    } catch (error) {
        console.error('Failed to load tasks:', error);
        showToast('Failed to load tasks', 'error');
    }
}

function displayTasks(tasks) {
    const container = document.getElementById('tasksList');

    if (tasks.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500 py-8">No tasks found</p>';
        return;
    }

    // Group tasks by status
    const tasksByStatus = {
        'Pending': tasks.filter(t => t.status === 'Pending'),
        'In Progress': tasks.filter(t => t.status === 'In Progress'),
        'Completed': tasks.filter(t => t.status === 'Completed')
    };

    const html = `
        <div class="grid grid-cols-3 gap-4">
            ${Object.entries(tasksByStatus).map(([status, statusTasks]) => `
                <div class="bg-gray-50 rounded-lg p-4">
                    <h3 class="font-bold mb-3 text-lg">${status} (${statusTasks.length})</h3>
                    <div class="space-y-2">
                        ${statusTasks.map(task => `
                            <div class="bg-white rounded-lg p-3 shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer"
                                 onclick="viewTaskDetails(${task.id})">
                                <div class="font-semibold">${task.task_name}</div>
                                <div class="text-sm text-gray-600 mt-1">${task.description || 'No description'}</div>
                                <div class="flex justify-between items-center mt-2">
                                    <span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority}</span>
                                    ${task.due_date ? `<span class="text-xs text-gray-500">${formatDate(task.due_date)}</span>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    container.innerHTML = html;
}

function getPriorityBadgeClass(priority) {
    const priorityMap = {
        'High': 'badge-high',
        'Medium': 'badge-medium',
        'Low': 'badge-low'
    };
    return priorityMap[priority] || 'badge-medium';
}

async function viewTaskDetails(taskId) {
    try {
        // For simplicity, we'll fetch all tasks and find the one we need
        const response = await fetch(`${API_BASE}/tasks/`);
        const tasks = await response.json();
        const task = tasks.find(t => t.id === taskId);

        if (!task) {
            showToast('Task not found', 'error');
            return;
        }

        const modalContent = `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <strong>Task Name:</strong>
                        <p>${task.task_name}</p>
                    </div>
                    <div>
                        <strong>Status:</strong>
                        <select id="taskStatus" class="input-field w-full">
                            <option value="Pending" ${task.status === 'Pending' ? 'selected' : ''}>Pending</option>
                            <option value="In Progress" ${task.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                            <option value="Completed" ${task.status === 'Completed' ? 'selected' : ''}>Completed</option>
                        </select>
                    </div>
                    <div>
                        <strong>Priority:</strong>
                        <select id="taskPriority" class="input-field w-full">
                            <option value="Low" ${task.priority === 'Low' ? 'selected' : ''}>Low</option>
                            <option value="Medium" ${task.priority === 'Medium' ? 'selected' : ''}>Medium</option>
                            <option value="High" ${task.priority === 'High' ? 'selected' : ''}>High</option>
                        </select>
                    </div>
                    <div>
                        <strong>Assigned To:</strong>
                        <input type="text" id="taskAssignedTo" class="input-field w-full" value="${task.assigned_to || ''}">
                    </div>
                    <div>
                        <strong>Due Date:</strong>
                        <input type="date" id="taskDueDate" class="input-field w-full" value="${task.due_date || ''}">
                    </div>
                    <div>
                        <strong>Project:</strong>
                        <p>${task.project_number}</p>
                    </div>
                    <div class="col-span-2">
                        <strong>Description:</strong>
                        <textarea id="taskDescription" class="input-field w-full" rows="3">${task.description || ''}</textarea>
                    </div>
                </div>

                <div class="flex justify-end space-x-2 pt-4 border-t">
                    <button onclick="deleteTask(${task.id})" class="btn-secondary bg-red-600 hover:bg-red-700">
                        <i class="fas fa-trash mr-2"></i>Delete
                    </button>
                    <button onclick="updateTask(${task.id})" class="btn-primary">
                        <i class="fas fa-save mr-2"></i>Save Changes
                    </button>
                </div>
            </div>
        `;

        showModal(createModal('Task Details', modalContent));
    } catch (error) {
        console.error('Failed to load task details:', error);
        showToast('Failed to load task details', 'error');
    }
}

async function updateTask(taskId) {
    try {
        const updates = {
            status: document.getElementById('taskStatus').value,
            priority: document.getElementById('taskPriority').value,
            assigned_to: document.getElementById('taskAssignedTo').value,
            due_date: document.getElementById('taskDueDate').value,
            description: document.getElementById('taskDescription').value
        };

        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });

        if (!response.ok) {
            throw new Error('Update failed');
        }

        showToast('Task updated successfully', 'success');
        closeModal();
        loadTasks();
    } catch (error) {
        console.error('Failed to update task:', error);
        showToast('Failed to update task', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        showToast('Task deleted successfully', 'success');
        closeModal();
        loadTasks();
    } catch (error) {
        console.error('Failed to delete task:', error);
        showToast('Failed to delete task', 'error');
    }
}

function showAddTaskDialog() {
    const modalContent = `
        <div class="space-y-4">
            <div class="form-group">
                <label class="form-label">Task Name</label>
                <input type="text" id="newTaskName" class="input-field w-full" placeholder="Enter task name">
            </div>

            <div class="form-group">
                <label class="form-label">Project Number</label>
                <select id="newTaskProject" class="input-field w-full">
                    <option value="">Select a project...</option>
                    ${AppState.projects.map(p => `
                        <option value="${p.PROJECT_NUMBER}">${p.PROJECT_NUMBER} - ${p.PROJECT_NAME}</option>
                    `).join('')}
                </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div class="form-group">
                    <label class="form-label">Priority</label>
                    <select id="newTaskPriority" class="input-field w-full">
                        <option value="Low">Low</option>
                        <option value="Medium" selected>Medium</option>
                        <option value="High">High</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Due Date</label>
                    <input type="date" id="newTaskDueDate" class="input-field w-full">
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Assigned To</label>
                <input type="text" id="newTaskAssignedTo" class="input-field w-full" placeholder="Email or name">
            </div>

            <div class="form-group">
                <label class="form-label">Description</label>
                <textarea id="newTaskDescription" class="input-field w-full" rows="3" placeholder="Task description"></textarea>
            </div>

            <div class="flex justify-end space-x-2">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                <button onclick="createTask()" class="btn-primary">
                    <i class="fas fa-plus mr-2"></i>Create Task
                </button>
            </div>
        </div>
    `;

    showModal(createModal('Add New Task', modalContent));
}

async function createTask() {
    try {
        const taskData = {
            task_name: document.getElementById('newTaskName').value,
            project_number: document.getElementById('newTaskProject').value,
            priority: document.getElementById('newTaskPriority').value,
            due_date: document.getElementById('newTaskDueDate').value || null,
            assigned_to: document.getElementById('newTaskAssignedTo').value,
            description: document.getElementById('newTaskDescription').value,
            status: 'Pending'
        };

        if (!taskData.task_name || !taskData.project_number) {
            showToast('Please fill in required fields', 'error');
            return;
        }

        const response = await fetch(`${API_BASE}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });

        if (!response.ok) {
            throw new Error('Create failed');
        }

        showToast('Task created successfully', 'success');
        closeModal();
        loadTasks();
    } catch (error) {
        console.error('Failed to create task:', error);
        showToast('Failed to create task', 'error');
    }
}

// Event Listeners
document.getElementById('addTaskBtn')?.addEventListener('click', showAddTaskDialog);

// Export functions
window.loadTasks = loadTasks;
window.viewTaskDetails = viewTaskDetails;
window.updateTask = updateTask;
window.deleteTask = deleteTask;
window.createTask = createTask;
