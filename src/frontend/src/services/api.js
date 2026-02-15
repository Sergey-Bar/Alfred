
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Centralized API service for all dashboard and admin endpoints. Handles authentication, error handling, and provides typed methods for all backend routes.
// Why: Prevents code duplication and ensures all API calls are consistent and secure.
// Root Cause: Scattered fetch logic leads to bugs, security issues, and inconsistent error handling.
// Context: All frontend API calls should use this service. Future: consider request batching or GraphQL for complex dashboards.
// Model Suitability: For API service patterns, GPT-4.1 is sufficient.
// API service for dashboard endpoints

const API_BASE = '/v1';

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Encapsulates all API logic, authentication, and error handling for the frontend dashboard.
// Why: Ensures all API calls are authenticated, typed, and error-resilient.
// Root Cause: Ad-hoc API calls are hard to maintain and secure.
// Context: Use this class for all backend communication.
class ApiService {
    constructor() {
        // Safely access localStorage (may be undefined in some test environments)
        try {
            this.apiKey = (typeof localStorage !== 'undefined' && typeof localStorage.getItem === 'function')
                ? localStorage.getItem('admin_api_key') || ''
                : '';
        } catch {
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

        // Add API key if available - use standard Authorization header
        if (this.apiKey) {
            headers['Authorization'] = `Bearer ${this.apiKey}`;
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

    // Personal User Data
    async getCurrentUser() {
        return this.fetchJson('/users/me');
    }

    async getUserPreferences() {
        const user = await this.getCurrentUser();
        return user.preferences || {};
    }

    async getQuotaStatus() {
        return this.fetchJson('/users/me/quota');
    }

    async getMyTransfers(limit = 20) {
        return this.fetchJson(`/users/me/transfers?limit=${limit}`);
    }

    async getMyTeams() {
        return this.fetchJson('/teams/my-teams');
    }

    async getUsageAnalytics(days = 7) {
        return this.fetchJson(`/analytics/usage?days=${days}`);
    }

    async updateProfile(updates) {
        return this.fetchJson('/users/me', {
            method: 'PUT',
            body: JSON.stringify(updates),
        });
    }

    async updateUserPreferences(preferences) {
        return this.updateProfile({ preferences });
    }

    async getIntegrationsConfig() {
        return this.fetchJson('/config/integrations');
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

    async getTeamMembers(teamId) {
        return this.fetchJson(`/admin/teams/${teamId}/members`);
    }

    async addTeamMember(teamId, userIdOrEmail, isAdmin = false) {
        // Check if userIdOrEmail looks like an email
        if (userIdOrEmail.includes('@')) {
            return this.fetchJson(`/admin/teams/${teamId}/members`, {
                method: 'POST',
                body: JSON.stringify({ email: userIdOrEmail, is_admin: isAdmin }),
            });
        }

        return this.fetchJson(`/admin/teams/${teamId}/members/${userIdOrEmail}?is_admin=${isAdmin}`, {
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
        // Send both keys to support backend accepting either `requested_credits` or `requested_amount`
        return this.fetchJson('/approvals', {
            method: 'POST',
            body: JSON.stringify({ requested_amount: amount, requested_credits: amount, reason }),
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

    // [AI GENERATED]
    // Model: GitHub Copilot (GPT-4.1)
    // Logic: Fetches audit logs for admin activity log UI and compliance dashboards.
    // Why: Enables frontend to display audit/activity logs for transparency and compliance.
    // Root Cause: No API existed for retrieving audit logs for admin review or analytics.
    // Context: Use in ActivityLog and admin dashboards. Future: add filtering, streaming, and advanced analytics.
    // Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced analytics, a more advanced model may be preferred.
    async getAuditLogs(skip = 0, limit = 100) {
        return this.fetchJson(`/admin/audit-logs?skip=${skip}&limit=${limit}`);
    }

    // [AI GENERATED]
    // Model: GitHub Copilot (GPT-4.1)
    // Logic: Fetches quotas, API keys, and endpoint config for the admin settings panel.
    // Why: Enables frontend to display and manage quotas, API keys, and LLM endpoints for admin review and configuration.
    // Root Cause: No unified API existed for surfacing these settings to the frontend.
    // Context: Use in Settings panel. Future: add PATCH/PUT for admin config updates.
    // Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced config management, a more advanced model may be preferred.
    async getAdminConfig() {
        return this.fetchJson('/admin/config');
    }

    // [AI GENERATED]
    // Model: GitHub Copilot (GPT-4.1)
    // Logic: RBAC management API methods for roles, permissions, and assignments. Enables admin UI to manage RBAC.
    // Why: Required for enterprise-grade governance and least-privilege workflows.
    // Root Cause: No frontend API existed for RBAC management.
    // Context: Use in RBAC admin panel. Future: add org/team scoping and fine-grained permission checks.
    // Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced policy engines, a more advanced model may be preferred.

    // --- Role Management ---
    async getRoles() {
        return this.fetchJson('/v1/rbac/roles');
    }
    async createRole(role) {
        return this.fetchJson('/v1/rbac/roles', {
            method: 'POST',
            body: JSON.stringify(role),
        });
    }
    async deleteRole(roleId) {
        return this.fetchJson(`/v1/rbac/roles/${roleId}`, {
            method: 'DELETE',
        });
    }

    // --- Permission Management ---
    async getPermissions() {
        return this.fetchJson('/v1/rbac/permissions');
    }
    async createPermission(permission) {
        return this.fetchJson('/v1/rbac/permissions', {
            method: 'POST',
            body: JSON.stringify(permission),
        });
    }
    async deletePermission(permissionId) {
        return this.fetchJson(`/v1/rbac/permissions/${permissionId}`, {
            method: 'DELETE',
        });
    }

    // --- User-Role Assignment ---
    async assignRoleToUser(userId, roleId) {
        return this.fetchJson(`/v1/rbac/users/${userId}/roles/${roleId}`, {
            method: 'POST',
        });
    }
    async removeRoleFromUser(userId, roleId) {
        return this.fetchJson(`/v1/rbac/users/${userId}/roles/${roleId}`, {
            method: 'DELETE',
        });
    }

    // --- Role-Permission Assignment ---
    async assignPermissionToRole(roleId, permissionId) {
        return this.fetchJson(`/v1/rbac/roles/${roleId}/permissions/${permissionId}`, {
            method: 'POST',
        });
    }
    async removePermissionFromRole(roleId, permissionId) {
        return this.fetchJson(`/v1/rbac/roles/${roleId}/permissions/${permissionId}`, {
            method: 'DELETE',
        });
    }

    // [AI GENERATED]
    // Model: GitHub Copilot (GPT-4.1)
    // Logic: Notification and alert management API methods for notification center and admin alerting UI.
    // Why: Enables real-time alerting, compliance, and operational transparency for admins and users.
    // Root Cause: No frontend API existed for notifications or alert management.
    // Context: Use in notification center and admin alerting UI. Future: extend for granular alert rules and user preferences.
    // Model Suitability: For REST API patterns, GPT-4.1 is sufficient; for advanced notification logic, a more advanced model may be preferred.

    // --- Notification Channel Management (Admin) ---
    async getNotificationChannels() {
        return this.fetchJson('/notifications/channels');
    }
    async addNotificationChannel(channel) {
        return this.fetchJson('/notifications/channels', {
            method: 'POST',
            body: JSON.stringify(channel),
        });
    }
    async deleteNotificationChannel(channelId) {
        return this.fetchJson(`/notifications/channels/${channelId}`, {
            method: 'DELETE',
        });
    }
    async testNotificationChannel(channelId) {
        return this.fetchJson(`/notifications/channels/${channelId}/test`, {
            method: 'POST',
        });
    }

    // --- User Notification Feed ---
    async getUserNotifications() {
        return this.fetchJson('/notifications/feed');
    }

    // --- Send Notification (Admin) ---
    async sendNotification(payload) {
        return this.fetchJson('/notifications/send', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }

    // [AI GENERATED]
    // Model: GitHub Copilot (GPT-4.1)
    // Logic: Bulk import/export API methods for users, teams, and models. Enables admin UI to upload/download CSV for onboarding, migration, and backup.
    // Why: Required for efficient onboarding, migration, and backup of user/team/model data.
    // Root Cause: No frontend API existed for bulk data import/export or migration.
    // Context: Use in admin import/export UI. Future: extend for audit logging, dry-run, and rollback support.
    // Model Suitability: For REST API and file handling, GPT-4.1 is sufficient; for advanced ETL, a more advanced model may be preferred.

    // --- Export ---
    async exportUsers() {
        const res = await fetch('/v1/import-export/users', { headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {} });
        return res.text();
    }
    async exportTeams() {
        const res = await fetch('/v1/import-export/teams', { headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {} });
        return res.text();
    }
    async exportModels() {
        const res = await fetch('/v1/import-export/models', { headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {} });
        return res.text();
    }

    // --- Import ---
    async importUsers(file) {
        const form = new FormData();
        form.append('file', file);
        const res = await fetch('/v1/import-export/users', {
            method: 'POST',
            headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {},
            body: form
        });
        return res.json();
    }
    async importTeams(file) {
        const form = new FormData();
        form.append('file', file);
        const res = await fetch('/v1/import-export/teams', {
            method: 'POST',
            headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {},
            body: form
        });
        return res.json();
    }
    async importModels(file) {
        const form = new FormData();
        form.append('file', file);
        const res = await fetch('/v1/import-export/models', {
            method: 'POST',
            headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {},
            body: form
        });
        return res.json();
    }
}

export const api = new ApiService();

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Add API methods for custom analytics/reporting: list, create, and run custom reports.
// Why: Enables frontend UI to create, schedule, and export custom reports (CSV/PDF/Excel).
// Root Cause: No frontend API existed for custom/scheduled/exportable reports.
// Context: Used by CustomReportsAdmin.jsx. Future: add advanced filters, BI integration, and permission checks.
// Model Suitability: For REST API and file handling, GPT-4.1 is sufficient; for advanced analytics, consider Claude 3 or Gemini 1.5.

api.listCustomReports = async function () {
    return this.fetchJson('/reports');
};
api.createCustomReport = async function (report) {
    return this.fetchJson('/reports', {
        method: 'POST',
        body: JSON.stringify(report),
    });
};
api.runCustomReport = async function (reportId, params) {
    return this.fetchJson(`/reports/${reportId}/run`, {
        method: 'POST',
        body: JSON.stringify(params || {}),
    });
};
export default api;
