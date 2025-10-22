// Notes Tab Functionality

let currentProjectForNotes = null;

async function loadNotes(projectNumber = null) {
    if (!projectNumber && !currentProjectForNotes) {
        displayNotesPlaceholder();
        return;
    }

    const project = projectNumber || currentProjectForNotes;
    currentProjectForNotes = project;

    try {
        const response = await fetch(`${API_BASE}/notes/${project}`);
        const notes = await response.json();

        displayNotes(notes);
    } catch (error) {
        console.error('Failed to load notes:', error);
        showToast('Failed to load notes', 'error');
    }
}

function displayNotesPlaceholder() {
    const container = document.getElementById('notesList');
    container.innerHTML = `
        <div class="text-center py-8">
            <p class="text-gray-500 mb-4">Select a project to view notes</p>
            <select id="notesProjectSelect" class="input-field">
                <option value="">Select a project...</option>
                ${AppState.projects.map(p => `
                    <option value="${p.PROJECT_NUMBER}">${p.PROJECT_NUMBER} - ${p.PROJECT_NAME}</option>
                `).join('')}
            </select>
        </div>
    `;

    document.getElementById('notesProjectSelect')?.addEventListener('change', (e) => {
        if (e.target.value) {
            loadNotes(e.target.value);
        }
    });
}

function displayNotes(notes) {
    const container = document.getElementById('notesList');

    if (notes.length === 0) {
        container.innerHTML = `
            <p class="text-center text-gray-500 py-8">No notes found for this project</p>
            <p class="text-center">
                <button onclick="showAddNoteDialog()" class="btn-primary">
                    <i class="fas fa-plus mr-2"></i>Add First Note
                </button>
            </p>
        `;
        return;
    }

    const html = `
        <div class="space-y-4">
            ${notes.map(note => `
                <div class="bg-white rounded-lg shadow-md p-4 border-l-4 border-red-600">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="font-bold text-lg">${note.title}</h3>
                        <div class="flex space-x-2">
                            <button onclick="editNote(${note.id})" class="text-blue-600 hover:text-blue-800">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteNote(${note.id})" class="text-red-600 hover:text-red-800">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="text-gray-700 whitespace-pre-wrap mb-2">${note.content || ''}</div>
                    ${note.tags ? `
                        <div class="flex flex-wrap gap-2 mt-2">
                            ${note.tags.split(',').map(tag => `
                                <span class="badge badge-active text-xs">${tag.trim()}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                    <div class="text-xs text-gray-500 mt-2">
                        Created by ${note.created_by || 'Unknown'} on ${formatDate(note.created_date)}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    container.innerHTML = html;
}

function showAddNoteDialog() {
    if (!currentProjectForNotes) {
        showToast('Please select a project first', 'error');
        return;
    }

    const modalContent = `
        <div class="space-y-4">
            <div class="form-group">
                <label class="form-label">Title</label>
                <input type="text" id="noteTitle" class="input-field w-full" placeholder="Note title">
            </div>

            <div class="form-group">
                <label class="form-label">Content</label>
                <textarea id="noteContent" class="input-field w-full" rows="8" placeholder="Note content"></textarea>
            </div>

            <div class="form-group">
                <label class="form-label">Tags (comma-separated)</label>
                <input type="text" id="noteTags" class="input-field w-full" placeholder="tag1, tag2, tag3">
            </div>

            <div class="form-group">
                <label class="form-label">Created By</label>
                <input type="text" id="noteCreatedBy" class="input-field w-full" placeholder="Your name">
            </div>

            <div class="flex justify-end space-x-2">
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                <button onclick="saveNewNote()" class="btn-primary">
                    <i class="fas fa-save mr-2"></i>Save Note
                </button>
            </div>
        </div>
    `;

    showModal(createModal('Add New Note', modalContent));
}

async function saveNewNote() {
    try {
        const noteData = {
            project_number: currentProjectForNotes,
            title: document.getElementById('noteTitle').value,
            content: document.getElementById('noteContent').value,
            tags: document.getElementById('noteTags').value,
            created_by: document.getElementById('noteCreatedBy').value
        };

        if (!noteData.title) {
            showToast('Please enter a title', 'error');
            return;
        }

        const response = await fetch(`${API_BASE}/notes/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(noteData)
        });

        if (!response.ok) {
            throw new Error('Save failed');
        }

        showToast('Note saved successfully', 'success');
        closeModal();
        loadNotes();
    } catch (error) {
        console.error('Failed to save note:', error);
        showToast('Failed to save note', 'error');
    }
}

async function editNote(noteId) {
    try {
        const response = await fetch(`${API_BASE}/notes/${currentProjectForNotes}`);
        const notes = await response.json();
        const note = notes.find(n => n.id === noteId);

        if (!note) {
            showToast('Note not found', 'error');
            return;
        }

        const modalContent = `
            <div class="space-y-4">
                <div class="form-group">
                    <label class="form-label">Title</label>
                    <input type="text" id="editNoteTitle" class="input-field w-full" value="${note.title}">
                </div>

                <div class="form-group">
                    <label class="form-label">Content</label>
                    <textarea id="editNoteContent" class="input-field w-full" rows="8">${note.content || ''}</textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Tags (comma-separated)</label>
                    <input type="text" id="editNoteTags" class="input-field w-full" value="${note.tags || ''}">
                </div>

                <div class="flex justify-end space-x-2">
                    <button onclick="closeModal()" class="btn-secondary">Cancel</button>
                    <button onclick="updateNote(${noteId})" class="btn-primary">
                        <i class="fas fa-save mr-2"></i>Update Note
                    </button>
                </div>
            </div>
        `;

        showModal(createModal('Edit Note', modalContent));
    } catch (error) {
        console.error('Failed to load note:', error);
        showToast('Failed to load note', 'error');
    }
}

async function updateNote(noteId) {
    try {
        const title = document.getElementById('editNoteTitle').value;
        const content = document.getElementById('editNoteContent').value;
        const tags = document.getElementById('editNoteTags').value;

        const response = await fetch(`${API_BASE}/notes/${noteId}?title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}&tags=${encodeURIComponent(tags)}`, {
            method: 'PUT'
        });

        if (!response.ok) {
            throw new Error('Update failed');
        }

        showToast('Note updated successfully', 'success');
        closeModal();
        loadNotes();
    } catch (error) {
        console.error('Failed to update note:', error);
        showToast('Failed to update note', 'error');
    }
}

async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/notes/${noteId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        showToast('Note deleted successfully', 'success');
        loadNotes();
    } catch (error) {
        console.error('Failed to delete note:', error);
        showToast('Failed to delete note', 'error');
    }
}

// Event Listeners
document.getElementById('addNoteBtn')?.addEventListener('click', showAddNoteDialog);

// Export functions
window.loadNotes = loadNotes;
window.saveNewNote = saveNewNote;
window.editNote = editNote;
window.updateNote = updateNote;
window.deleteNote = deleteNote;
