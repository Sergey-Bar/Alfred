// API service for dashboard endpoints

const API_BASE = '/v1';

class ApiService {
    constructor() {
        // Safely access localStorage (may be undefined in some test environments)
        try {
            this.apiKey = (typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function')
                ? localStorage.getItem('admin_api_key') || ''
                : '';
        } catch (e) {
            this.apiKey = '';
        }
    }

    setApiKey(key) {
        this.apiKey = key;
        localStorage.setItem('admin_api_key', key);
    }

    clearApiKey() {
        this.apiKey = '';
        localStorage.removeItem('admin_api_key');
    }

    getApiKey() {
        return this.apiKey;
    }

    isAuthenticated() {
        return !!this.apiKey;
    }

    async fetchJson(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // Add API key if available
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers,
            ...options,
        });

        if (response.status === 401 || response.status === 403) {
            this.clearApiKey();
            throw new Error('Authentication required');
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Dashboard endpoints
    async getOverview() {
        return this.fetchJson('/dashboard/overview');
    }

    async getUserStats() {
        return this.fetchJson('/dashboard/users');
    }

    async getTeamStats() {
        return this.fetchJson('/dashboard/teams');
    }

    async getCostTrends(days = 30) {
        return this.fetchJson(`/dashboard/trends?days=${days}`);
    }

    async getModelUsage() {
        return this.fetchJson('/dashboard/models');
    }

    async getLeaderboard(limit = 10) {
        return this.fetchJson(`/dashboard/leaderboard?limit=${limit}`);
    }

    async getApprovalStats() {
        return this.fetchJson('/dashboard/approvals');
    }

    async getTransfers(limit = 50) {
        return this.fetchJson(`/dashboard/transfers?limit=${limit}`);
    }

    // User management (admin endpoints)
    async getUsers() {
        return this.fetchJson('/admin/users');
    }

    async createUser(userData) {
        return this.fetchJson('/admin/users', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async updateUser(userId, userData) {
        return this.fetchJson(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData),
        });
    }

    async deleteUser(userId) {
        return this.fetchJson(`/admin/users/${userId}`, {
            method: 'DELETE',
        });
    }

    // Team management (admin endpoints)
    async getTeams() {
        return this.fetchJson('/admin/teams');
    }

    async createTeam(teamData) {
        return this.fetchJson('/admin/teams', {
            method: 'POST',
            body: JSON.stringify(teamData),
        });
    }

    async updateTeam(teamId, teamData) {
        return this.fetchJson(`/admin/teams/${teamId}`, {
            method: 'PUT',
            body: JSON.stringify(teamData),
        });
    }

    async deleteTeam(teamId) {
        return this.fetchJson(`/admin/teams/${teamId}`, {
            method: 'DELETE',
        });
    }

    async addTeamMember(teamId, userId, isAdmin = false) {
        return this.fetchJson(`/admin/teams/${teamId}/members/${userId}?is_admin=${isAdmin}`, {
            method: 'POST',
        });
    }

    async removeTeamMember(teamId, userId) {
        return this.fetchJson(`/admin/teams/${teamId}/members/${userId}`, {
            method: 'DELETE',
        });
    }

    // Credit Reallocation
    async createTransfer(toUserId, amount, reason = '') {
        return this.fetchJson('/users/me/transfer', {
            method: 'POST',
            body: JSON.stringify({ to_user_id: toUserId, amount, reason }),
        });
    }

    // User status (vacation mode)
    async updateUserStatus(status) {
        return this.fetchJson(`/users/me/status?status=${status}`, {
            method: 'PUT',
        });
    }

    // Privacy preference
    async updatePrivacyMode(mode) {
        return this.fetchJson(`/users/me/privacy?mode=${mode}`, {
            method: 'PUT',
        });
    }

    // Approvals
    async getPendingApprovals() {
        return this.fetchJson('/approvals/pending');
    }

    async createApprovalRequest(amount, reason) {
        return this.fetchJson('/approvals', {
            method: 'POST',
            body: JSON.stringify({ requested_amount: amount, reason }),
        });
    }

    async approveRequest(approvalId, approvedAmount = null) {
        const params = approvedAmount ? `?approved_amount=${approvedAmount}` : '';
        return this.fetchJson(`/approvals/${approvalId}/approve${params}`, {
            method: 'POST',
        });
    }

    async rejectRequest(approvalId, reason = '') {
        return this.fetchJson(`/approvals/${approvalId}/reject`, {
            method: 'POST',
            body: JSON.stringify({ reason }),
        });
    }

    // Get all users for dropdown
    async getUsersSimple() {
        return this.fetchJson('/admin/users');
    }
}

export const api = new ApiService();
export default api;
