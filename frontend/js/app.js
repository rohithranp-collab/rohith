/**
 * Main Frontend Application Controller for TaskCraft
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Application State ---
    const state = {
        todos: [],
        stats: null,
        filters: {
            search: '',
            status: 'all',
            category: 'all',
            priority: 'all',
            sortBy: 'created_at_desc'
        },
        editingTodoId: null
    };

    // --- DOM Element References ---
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const statusTabs = document.getElementById('statusTabs');
    const categoryFilter = document.getElementById('categoryFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const sortBySelect = document.getElementById('sortBySelect');
    
    const tasksList = document.getElementById('tasksList');
    const emptyState = document.getElementById('emptyState');
    const emptyCreateBtn = document.getElementById('emptyCreateBtn');

    // Stats elements
    const statTotal = document.getElementById('statTotal');
    const statPending = document.getElementById('statPending');
    const statCompleted = document.getElementById('statCompleted');
    const statHighPriority = document.getElementById('statHighPriority');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressBarFill = document.getElementById('progressBarFill');

    // Modal elements
    const openCreateModalBtn = document.getElementById('openCreateModalBtn');
    const taskModal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('modalTitle');
    const taskForm = document.getElementById('taskForm');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const taskIdInput = document.getElementById('taskId');
    const taskTitleInput = document.getElementById('taskTitleInput');
    const taskDescInput = document.getElementById('taskDescInput');
    const taskCategorySelect = document.getElementById('taskCategorySelect');
    const taskPrioritySelect = document.getElementById('taskPrioritySelect');
    const taskDueDateInput = document.getElementById('taskDueDateInput');
    const subtasksListBuilder = document.getElementById('subtasksListBuilder');
    const addSubtaskRowBtn = document.getElementById('addSubtaskRowBtn');
    const toast = document.getElementById('toast');

    // --- Theme Management ---
    function initTheme() {
        const savedTheme = localStorage.getItem('taskcraft_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('taskcraft_theme', nextTheme);
    });

    // --- Toast Banner ---
    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.style.borderColor = isError ? 'var(--danger)' : 'var(--success)';
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // --- Relative Date Formatter ---
    function formatDueDate(dateString) {
        if (!dateString) return null;
        
        const due = new Date(dateString);
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        due.setHours(0, 0, 0, 0);
        
        const diffDays = Math.round((due - now) / (1000 * 60 * 60 * 24));
        
        if (diffDays < 0) return { text: `Overdue (${Math.abs(diffDays)}d ago)`, isOverdue: true };
        if (diffDays === 0) return { text: 'Due Today', isOverdue: false, isToday: true };
        if (diffDays === 1) return { text: 'Due Tomorrow', isOverdue: false };
        
        return { text: `Due ${due.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`, isOverdue: false };
    }

    // --- Render Dashboard Stats ---
    async function loadStats() {
        try {
            const stats = await API.getStats();
            state.stats = stats;

            statTotal.textContent = stats.total;
            statPending.textContent = stats.pending;
            statCompleted.textContent = stats.completed;
            statHighPriority.textContent = stats.high_priority;

            progressPercentage.textContent = `${stats.completion_rate}%`;
            progressBarFill.style.width = `${stats.completion_rate}%`;
        } catch (err) {
            console.error('Error loading stats:', err);
        }
    }

    // --- Render Tasks List ---
    async function loadTasks() {
        try {
            tasksList.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading tasks...</div>';
            const todos = await API.getTodos(state.filters);
            state.todos = todos;
            renderTasksList(todos);
            await loadStats();
        } catch (err) {
            console.error('Error loading tasks:', err);
            showToast('Failed to load tasks', true);
        }
    }

    function renderTasksList(todos) {
        if (!todos || todos.length === 0) {
            tasksList.innerHTML = '';
            emptyState.style.display = 'flex';
            return;
        }

        emptyState.style.display = 'none';
        tasksList.innerHTML = todos.map(todo => createTodoCardHTML(todo)).join('');
    }

    function createTodoCardHTML(todo) {
        const isCompleted = todo.status === 'completed';
        const dueDateInfo = formatDueDate(todo.due_date);

        const subtaskCount = todo.subtasks ? todo.subtasks.length : 0;
        const completedSubtasks = todo.subtasks ? todo.subtasks.filter(s => s.is_completed).length : 0;

        const subtasksHTML = subtaskCount > 0 ? `
            <div class="subtasks-container">
                <button class="subtasks-toggle" data-action="toggle-subtasks-view" data-id="${todo.id}">
                    <span>Checklist (${completedSubtasks}/${subtaskCount})</span>
                </button>
                <div class="subtasks-list" id="subtasks-list-${todo.id}">
                    ${todo.subtasks.map(sub => `
                        <div class="subtask-item ${sub.is_completed ? 'completed' : ''}">
                            <div class="custom-checkbox ${sub.is_completed ? 'checked' : ''}" data-action="toggle-subtask" data-sub-id="${sub.id}">
                                ${sub.is_completed ? '✓' : ''}
                            </div>
                            <span>${escapeHTML(sub.title)}</span>
                            <button class="action-btn delete" data-action="delete-subtask" data-sub-id="${sub.id}" title="Delete subtask" style="margin-left: auto;">✕</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : '';

        return `
            <div class="task-card glass-card priority-${todo.priority} ${isCompleted ? 'completed' : ''}" data-id="${todo.id}">
                <div class="task-header">
                    <div class="custom-checkbox ${isCompleted ? 'checked' : ''}" data-action="toggle-todo" data-id="${todo.id}">
                        ${isCompleted ? '✓' : ''}
                    </div>

                    <div class="task-body">
                        <div class="task-title-row">
                            <h3 class="task-title">${escapeHTML(todo.title)}</h3>
                            <span class="badge badge-category">${escapeHTML(todo.category)}</span>
                            <span class="badge badge-${todo.priority}">${todo.priority}</span>
                        </div>

                        ${todo.description ? `<p class="task-desc">${escapeHTML(todo.description)}</p>` : ''}

                        <div class="task-meta">
                            ${dueDateInfo ? `
                                <div class="meta-item ${dueDateInfo.isOverdue ? 'overdue' : ''}">
                                    📅 <span>${dueDateInfo.text}</span>
                                </div>
                            ` : ''}
                            <div class="meta-item">
                                🕒 <span>Created ${new Date(todo.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>

                        ${subtasksHTML}
                    </div>

                    <div class="task-actions">
                        <button class="action-btn" data-action="add-subtask-inline" data-id="${todo.id}" title="Add subtask">➕</button>
                        <button class="action-btn" data-action="edit-todo" data-id="${todo.id}" title="Edit task">✏️</button>
                        <button class="action-btn delete" data-action="delete-todo" data-id="${todo.id}" title="Delete task">🗑️</button>
                    </div>
                </div>
            </div>
        `;
    }

    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    // --- Search & Filter Event Handlers ---
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value;
        clearSearchBtn.style.display = val ? 'block' : 'none';

        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            state.filters.search = val;
            loadTasks();
        }, 300);
    });

    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearSearchBtn.style.display = 'none';
        state.filters.search = '';
        loadTasks();
    });

    statusTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-btn')) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');

            state.filters.status = e.target.getAttribute('data-status');
            loadTasks();
        }
    });

    categoryFilter.addEventListener('change', (e) => {
        state.filters.category = e.target.value;
        loadTasks();
    });

    priorityFilter.addEventListener('change', (e) => {
        state.filters.priority = e.target.value;
        loadTasks();
    });

    sortBySelect.addEventListener('change', (e) => {
        state.filters.sortBy = e.target.value;
        loadTasks();
    });

    // --- Task Actions Delegate Handler ---
    tasksList.addEventListener('click', async (e) => {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.getAttribute('data-action');
        const todoId = parseInt(target.getAttribute('data-id'), 10);
        const subId = parseInt(target.getAttribute('data-sub-id'), 10);

        try {
            if (action === 'toggle-todo') {
                await API.toggleTodo(todoId);
                loadTasks();
            } else if (action === 'delete-todo') {
                if (confirm('Are you sure you want to delete this task?')) {
                    await API.deleteTodo(todoId);
                    showToast('Task deleted successfully');
                    loadTasks();
                }
            } else if (action === 'edit-todo') {
                const todo = state.todos.find(t => t.id === todoId);
                if (todo) openModal(todo);
            } else if (action === 'toggle-subtask') {
                await API.toggleSubtask(subId);
                loadTasks();
            } else if (action === 'delete-subtask') {
                await API.deleteSubtask(subId);
                loadTasks();
            } else if (action === 'add-subtask-inline') {
                const title = prompt('Enter subtask title:');
                if (title && title.strip()) {
                    await API.addSubtask(todoId, title);
                    showToast('Subtask added');
                    loadTasks();
                }
            }
        } catch (err) {
            console.error(`Error performing action ${action}:`, err);
            showToast(`Action failed: ${err.message}`, true);
        }
    });

    // --- Modal Handler ---
    function openModal(todo = null) {
        state.editingTodoId = todo ? todo.id : null;
        modalTitle.textContent = todo ? 'Edit Task' : 'Create New Task';

        taskIdInput.value = todo ? todo.id : '';
        taskTitleInput.value = todo ? todo.title : '';
        taskDescInput.value = todo ? todo.description || '' : '';
        taskCategorySelect.value = todo ? todo.category : 'Personal';
        taskPrioritySelect.value = todo ? todo.priority : 'medium';
        taskDueDateInput.value = todo && todo.due_date ? todo.due_date : '';

        // Clear subtasks builder
        subtasksListBuilder.innerHTML = '';
        if (todo && todo.subtasks && todo.subtasks.length > 0) {
            todo.subtasks.forEach(s => addSubtaskRow(s.title));
        } else if (!todo) {
            addSubtaskRow();
        }

        taskModal.style.display = 'flex';
    }

    function closeModal() {
        taskModal.style.display = 'none';
        taskForm.reset();
        state.editingTodoId = null;
    }

    function addSubtaskRow(initialValue = '') {
        const div = document.createElement('div');
        div.className = 'subtask-builder-row';
        div.innerHTML = `
            <input type="text" class="subtask-row-input" placeholder="e.g. Gather document files" value="${escapeHTML(initialValue)}">
            <button type="button" class="action-btn delete remove-subtask-row-btn">✕</button>
        `;

        div.querySelector('.remove-subtask-row-btn').addEventListener('click', () => {
            div.remove();
        });

        subtasksListBuilder.appendChild(div);
    }

    openCreateModalBtn.addEventListener('click', () => openModal());
    emptyCreateBtn.addEventListener('click', () => openModal());
    closeModalBtn.addEventListener('click', closeModal);
    cancelModalBtn.addEventListener('click', closeModal);
    addSubtaskRowBtn.addEventListener('click', () => addSubtaskRow());

    // Submit Modal Form
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = taskTitleInput.value.trim();
        if (!title) {
            showToast('Please enter a task title', true);
            return;
        }

        const subtaskInputs = Array.from(document.querySelectorAll('.subtask-row-input'))
            .map(input => input.value.trim())
            .filter(val => val.length > 0);

        const payload = {
            title: title,
            description: taskDescInput.value.trim(),
            category: taskCategorySelect.value,
            priority: taskPrioritySelect.value,
            due_date: taskDueDateInput.value || null
        };

        try {
            if (state.editingTodoId) {
                payload.status = state.todos.find(t => t.id === state.editingTodoId)?.status || 'pending';
                await API.updateTodo(state.editingTodoId, payload);
                showToast('Task updated successfully');
            } else {
                payload.subtasks = subtaskInputs;
                await API.createTodo(payload);
                showToast('Task created successfully');
            }

            closeModal();
            loadTasks();
        } catch (err) {
            console.error('Error saving task:', err);
            showToast(`Failed to save task: ${err.message}`, true);
        }
    });

    // --- Initial App Load ---
    initTheme();
    loadTasks();
});
