// Task Detail Page JavaScript
class TaskDetailManager {
    constructor(taskData) {
        this.taskData = taskData;
        this.ws = null;
        this.isEditing = {
            title: false,
            description: false,
            assigned_user: false,
            due_date: false,
            estimated_time: false
        };
        this.setupWebSocket();
        this.setupEventListeners();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${location.host}/ws/task/${this.taskData.id}/`;

        let attempts = 0;
        const backoff = () => {
            const base = Math.min(1000 * Math.pow(1.6, attempts), 8000);
            const jitter = Math.random() * 300;
            return base + jitter;
        };

        const connect = () => {
            ('Connecting to real-time updates...', 'bg-yellow-100 text-yellow-800');
            console.log('Attempting WebSocket connection to:', wsUrl);
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                attempts = 0;
                console.log('WebSocket connected successfully');
            };

            this.ws.onmessage = (event) => {
                console.log('WebSocket message received:', event.data);
                const data = JSON.parse(event.data);
                if (data.type === 'task_updated' && data.task) {
                    this.updateTaskDisplay(data.task);
                }
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                // Only auto-reconnect if it wasn't a normal close (1000)
                if (event.code !== 1000) {
                    attempts++;
                    setTimeout(connect, backoff());
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                try { this.ws.close(); } catch {}
            };
        };

        connect();
    }

    setupEventListeners() {
        // Status toggle button for completion
        const statusToggle = document.getElementById('task-status-toggle');
        if (statusToggle) {
            statusToggle.addEventListener('click', (e) => {
                // Toggle based on current task data, not button text
                const newCompletedState = !this.taskData.completed;
                this.updateField('completed', newCompletedState);
            });
        }

        // User select component for assigned user
        const userSelectWrapper = document.querySelector('.user-select-wrapper');
        if (userSelectWrapper) {
            userSelectWrapper.addEventListener('userselect:change', (e) => {
                const { value } = e.detail;
                this.updateField('assigned_user_id', value || null);
            });
        }

        // Date input for due date
        const dueDateInput = document.getElementById('task-due-date');
        if (dueDateInput) {
            dueDateInput.addEventListener('focus', () => {
                this.isEditing.due_date = true;
            });
            dueDateInput.addEventListener('blur', () => {
                this.isEditing.due_date = false;
            });
            dueDateInput.addEventListener('change', (e) => {
                // e.target.value will be "YYYY-MM-DD" from <input type="date">
                this.updateField('due_date', e.target.value || null);
            });
        }

        // Number input for estimated time
        const estimatedTimeInput = document.getElementById('task-estimated-time');
        if (estimatedTimeInput) {
            estimatedTimeInput.addEventListener('focus', () => {
                this.isEditing.estimated_time = true;
            });
            estimatedTimeInput.addEventListener('blur', () => {
                this.isEditing.estimated_time = false;
            });
            estimatedTimeInput.addEventListener('change', (e) => {
                const val = e.target.value;
                this.updateField('estimated_time', val === '' ? null : parseInt(val, 10));
            });
        }

        // Title input
        const titleInput = document.getElementById('task-title');
        if (titleInput) {
            let typingTimer;
            const saveDelay = 400;
            titleInput.addEventListener('input', (e) => {
                clearTimeout(typingTimer);
                typingTimer = setTimeout(() => {
                    this.updateField('title', e.target.value);
                }, saveDelay);
            });
        }

        // Description textarea
        const descriptionTextarea = document.getElementById('task-description');
        if (descriptionTextarea) {
            let typingTimer;
            const saveDelay = 500;
            descriptionTextarea.addEventListener('input', (e) => {
                clearTimeout(typingTimer);
                typingTimer = setTimeout(() => {
                    // Only send update if there's actual content (required field)
                    if (e.target.value.trim().length > 0) {
                        this.updateField('description', e.target.value);
                    }
                }, saveDelay);
            });
        }

        // Estimate button -> POST to /api/tasks/<id>/estimate/
        const estimateBtn = document.getElementById('estimate-time-btn');
        if (estimateBtn) {
            estimateBtn.addEventListener('click', () => {
                const url = estimateBtn.dataset.estimateUrl || `/api/tasks/${this.taskData.id}/estimate/`;
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken(),
                    },
                    body: JSON.stringify({})
                })
                .then(response => {
                    if (response.ok) {
                        this.showMessage('AI estimation in progress...', 'success');
                    } else {
                        this.showMessage('Estimation failed. Please try again.', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error starting estimation:', error);
                    this.showMessage('Estimation failed. Please try again.', 'error');
                });
            });
        }

    }

    updateField(fieldName, value) {
        // Update local cache
        this.taskData[fieldName] = value;

        // POST to server to persist field
        fetch(`/api/tasks/${this.taskData.id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({ [fieldName]: value })
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data && data.task) {
                this.updateTaskDisplay(data.task);
            }
        })
        .catch(error => {
            console.error('Error updating field:', error);
            // Optionally, show a toast/snackbar here.
        });
    }

    updateTaskDisplay(task) {
        // Sync local cache
        this.taskData = {
            ...this.taskData,
            ...task
        };

        // Title
        const titleInput = document.getElementById('task-title');
        if (titleInput && !this.isEditing.title) {
            titleInput.value = task.title ?? '';
        }

        // Description
        const descriptionTextarea = document.getElementById('task-description');
        if (descriptionTextarea && !this.isEditing.description) {
            descriptionTextarea.value = task.description ?? '';
        }

        // Completed status button
        const statusToggle = document.getElementById('task-status-toggle');
        if (statusToggle) {
            const isCompleted = !!task.completed;
            statusToggle.textContent = isCompleted ? '✓ Completed' : 'Pending';
            statusToggle.className = `inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-colors cursor-pointer ${
                isCompleted 
                    ? 'bg-green-100 text-green-800 hover:bg-green-200'
                    : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
            }`;
        }

        // Assigned user - update the custom user select component
        const userSelectWrapper = document.querySelector('.user-select-wrapper');
        if (userSelectWrapper && !this.isEditing.assigned_user) {
            // Find the UserSelect instance and update it
            const userSelectInstance = window.UserSelect && userSelectWrapper.userSelectInstance;
            if (userSelectInstance) {
                const assignedUser = task.assigned_user_name || '';
                const assignedUserId = task.assigned_user_id || '';
                userSelectInstance.setValue(assignedUserId, assignedUser);
            }
        }

        // Due date (expecting server to send ISO "YYYY-MM-DD" or null)
        const dueDateInput = document.getElementById('task-due-date');
        if (dueDateInput && !this.isEditing.due_date) {
            dueDateInput.value = task.due_date ?? '';
        }

        // Estimated time
        const estimatedTimeInput = document.getElementById('task-estimated-time');
        if (estimatedTimeInput && !this.isEditing.estimated_time) {
            estimatedTimeInput.value = task.estimated_time ?? '';
        }
    }

    getCsrfToken() {
        const name = 'csrftoken';
        const cookies = document.cookie ? document.cookie.split('; ') : [];
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i];
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return '';
    }

    showMessage(text, type = 'info') {
        // Remove existing message if present
        const existingMessage = document.getElementById('task-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Create message element
        const message = document.createElement('div');
        message.id = 'task-message';
        message.className = `fixed top-4 right-4 px-4 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-300 ${
            type === 'success' ? 'bg-green-100 border border-green-200 text-green-800' :
            type === 'error' ? 'bg-red-100 border border-red-200 text-red-800' :
            'bg-blue-100 border border-blue-200 text-blue-800'
        }`;
        message.textContent = text;

        // Add to page
        document.body.appendChild(message);

        // Fade out after 3 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                if (message.parentNode) {
                    message.remove();
                }
            }, 300);
        }, 3000);
    }
}

window.TaskDetailManager = TaskDetailManager;
