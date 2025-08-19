// Task Detail Page JavaScript
class TaskDetailManager {
    constructor(taskData) {
        this.taskData = taskData;
        this.ws = null;
        this.setupWebSocket();
        this.setupEventListeners();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${location.host}/ws/task/${this.taskData.id}/`);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'task_updated' && data.task) {
                this.updateTaskDisplay(data.task);
            }
        };

        this.ws.onclose = () => {
            // Reconnect after 3 seconds
            setTimeout(() => this.setupWebSocket(), 3000);
        };
    }

    setupEventListeners() {
        // Checkbox for completion status
        const completedCheckbox = document.getElementById('task-completed');
        if (completedCheckbox) {
            completedCheckbox.addEventListener('change', (e) => {
                this.updateField('completed', e.target.checked);
            });
        }

        // Select for assigned user
        const assignedUserSelect = document.getElementById('task-assigned-user');
        if (assignedUserSelect) {
            assignedUserSelect.addEventListener('change', (e) => {
                this.updateField('assigned_user_id', e.target.value || null);
            });
        }

        // Date input for due date
        const dueDateInput = document.getElementById('task-due-date');
        if (dueDateInput) {
            dueDateInput.addEventListener('change', (e) => {
                this.updateField('due_date', e.target.value || null);
            });
        }

        // Number input for estimated time
        const estimatedTimeInput = document.getElementById('task-estimated-time');
        if (estimatedTimeInput) {
            estimatedTimeInput.addEventListener('change', (e) => {
                const value = e.target.value ? parseInt(e.target.value) : null;
                this.updateField('estimated_time', value);
            });
        }
    }

    // Update field optimistically and send to server
    updateField(fieldName, value) {
        // Update local data immediately
        this.taskData[fieldName] = value;
        this.updateLocalUI(fieldName, value);
        
        // Send to server
        const payload = {};
        payload[fieldName] = value;
        
        fetch(`/tasks/api/tasks/${this.taskData.id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify(payload)
        }).catch(error => {
            console.error('Update failed:', error);
            // Could implement rollback here
            this.showError('Failed to update task');
        });
    }

    // Update local UI immediately (optimistic)
    updateLocalUI(fieldName, value) {
        switch(fieldName) {
            case 'completed':
                const label = document.getElementById('completed-label');
                if (label) {
                    label.textContent = value ? 'Completed' : 'In Progress';
                    label.className = value ? 'ml-3 text-green-600 font-medium' : 'ml-3 text-gray-600';
                }
                break;
        }
        this.updateTimestamp();
    }

    // Update display when WebSocket message arrives
    updateTaskDisplay(task) {
        // Update local data
        Object.assign(this.taskData, task);
        
        // Update UI elements
        const titleElement = document.getElementById('task-title');
        if (titleElement) titleElement.textContent = task.title;
        
        const descriptionElement = document.getElementById('task-description');
        if (descriptionElement) {
            descriptionElement.textContent = task.description || 'Click to add description...';
        }
        
        const completedCheckbox = document.getElementById('task-completed');
        if (completedCheckbox) completedCheckbox.checked = task.completed;
        
        const completedLabel = document.getElementById('completed-label');
        if (completedLabel) {
            completedLabel.textContent = task.completed ? 'Completed' : 'In Progress';
            completedLabel.className = task.completed ? 'ml-3 text-green-600 font-medium' : 'ml-3 text-gray-600';
        }
        
        const assignedUserSelect = document.getElementById('task-assigned-user');
        if (assignedUserSelect) assignedUserSelect.value = task.assigned_user_id || '';
        
        const dueDateInput = document.getElementById('task-due-date');
        if (dueDateInput) {
            dueDateInput.value = task.due_date ? task.due_date.slice(0, 16) : '';
        }
        
        const estimatedTimeInput = document.getElementById('task-estimated-time');
        if (estimatedTimeInput) estimatedTimeInput.value = task.estimated_time || '';
        
        this.updateTimestamp();
    }

    updateTimestamp() {
        const timestampElement = document.getElementById('updated-at');
        if (timestampElement) {
            timestampElement.innerHTML = '<span class="font-medium">Updated:</span> Just now';
        }
    }

    // Simple inline editing for text fields
    editField(fieldName) {
        const element = document.getElementById(`task-${fieldName}`);
        if (!element) return;
        
        const currentValue = this.taskData[fieldName] || '';
        
        if (fieldName === 'title') {
            this.editTitle(element, currentValue);
        } else if (fieldName === 'description') {
            this.editDescription(element, currentValue);
        }
    }

    editTitle(element, currentValue) {
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentValue;
        input.className = 'text-3xl font-bold w-full p-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500';
        
        const saveAndRestore = () => {
            const newValue = input.value.trim();
            if (newValue && newValue !== currentValue) {
                this.updateField('title', newValue);
            }
            element.textContent = newValue || currentValue;
            element.onclick = () => this.editField('title');
        };
        
        input.onblur = saveAndRestore;
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveAndRestore();
            }
            if (e.key === 'Escape') {
                element.textContent = currentValue;
                element.onclick = () => this.editField('title');
            }
        };
        
        element.replaceWith(input);
        input.focus();
        input.select();
    }

    editDescription(element, currentValue) {
        const textarea = document.createElement('textarea');
        textarea.value = currentValue;
        textarea.className = 'w-full min-h-[100px] p-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500';
        
        const saveAndRestore = () => {
            const newValue = textarea.value.trim();
            if (newValue !== currentValue) {
                this.updateField('description', newValue);
            }
            element.textContent = newValue || 'Click to add description...';
            element.onclick = () => this.editField('description');
        };
        
        textarea.onblur = saveAndRestore;
        textarea.onkeydown = (e) => {
            if (e.key === 'Escape') {
                element.textContent = currentValue || 'Click to add description...';
                element.onclick = () => this.editField('description');
            }
        };
        
        element.replaceWith(textarea);
        textarea.focus();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showError(message) {
        // Simple error display - could be enhanced with toast notifications
        console.error(message);
        // You could add a toast notification system here
    }
}

// Global function to initialize the task manager
window.initTaskDetail = function(taskData) {
    window.taskManager = new TaskDetailManager(taskData);
    
    // Expose editField globally for onclick handlers
    window.editField = (fieldName) => {
        window.taskManager.editField(fieldName);
    };
};