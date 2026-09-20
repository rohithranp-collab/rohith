/**
 * REST API Client for TaskCraft Application
 */

const API_BASE_URL = '/api';

const API = {
    /**
     * Fetch list of todos with search and filter parameters
     */
    async getTodos(filters = {}) {
        const query = new URLSearchParams();
        
        if (filters.search) query.append('search', filters.search);
        if (filters.status && filters.status !== 'all') query.append('status', filters.status);
        if (filters.category && filters.category !== 'all') query.append('category', filters.category);
        if (filters.priority && filters.priority !== 'all') query.append('priority', filters.priority);
        if (filters.sortBy) query.append('sort_by', filters.sortBy);

        const response = await fetch(`${API_BASE_URL}/todos?${query.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch tasks');
        return await response.json();
    },

    /**
     * Fetch dashboard statistics
     */
    async getStats() {
        const response = await fetch(`${API_BASE_URL}/todos/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        return await response.json();
    },

    /**
     * Create a new task
     */
    async createTodo(todoData) {
        const response = await fetch(`${API_BASE_URL}/todos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(todoData)
        });
        if (!response.ok) throw new Error('Failed to create task');
        return await response.json();
    },

    /**
     * Update an existing task
     */
    async updateTodo(todoId, todoData) {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(todoData)
        });
        if (!response.ok) throw new Error('Failed to update task');
        return await response.json();
    },

    /**
     * Quick toggle completion status
     */
    async toggleTodo(todoId) {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}/toggle`, {
            method: 'PATCH'
        });
        if (!response.ok) throw new Error('Failed to toggle task');
        return await response.json();
    },

    /**
     * Delete task
     */
    async deleteTodo(todoId) {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete task');
        return true;
    },

    /**
     * Add a subtask to an existing task
     */
    async addSubtask(todoId, title) {
        const response = await fetch(`${API_BASE_URL}/todos/${todoId}/subtasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        if (!response.ok) throw new Error('Failed to add subtask');
        return await response.json();
    },

    /**
     * Toggle subtask completion status
     */
    async toggleSubtask(subtaskId) {
        const response = await fetch(`${API_BASE_URL}/subtasks/${subtaskId}/toggle`, {
            method: 'PATCH'
        });
        if (!response.ok) throw new Error('Failed to toggle subtask');
        return await response.json();
    },

    /**
     * Delete subtask
     */
    async deleteSubtask(subtaskId) {
        const response = await fetch(`${API_BASE_URL}/subtasks/${subtaskId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete subtask');
        return await response.json();
    }
};

window.API = API;
