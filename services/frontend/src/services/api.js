
// API service for dashboard endpoints

const API_BASE = '/v1';

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

    isDemoMode() {
        try {
            return typeof localStorage !== 'undefined' && localStorage.getItem('alfred_demo_mode') === 'true';
        } catch { return false; }
    }

    async fetchJson(endpoint, options = {}) {
        // In demo mode, return synthetic data instead of hitting the backend
        if (this.isDemoMode()) {
            return this._demoResponse(endpoint, options);
        }

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

    // Suitability: L1 boilerplate — mock data generation
    _demoResponse(endpoint) {
        const e = endpoint.split('?')[0]; // strip query params
        const demoData = {
            '/dashboard/overview': { total_users: 128, active_users: 94, total_teams: 12, total_credits_allocated: 250000, total_credits_spent: 147832.50, total_requests: 1842567, pending_approvals: 7, cache_hit_rate: 0.34, active_providers: 8 },
            '/dashboard/trends': Array.from({ length: 30 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() - (29 - i)); return { date: d.toISOString().slice(0,10), cost: Math.round(3000 + Math.random() * 2000), requests: Math.round(40000 + Math.random() * 20000) }; }),
            '/dashboard/models': [
                { model: 'gpt-4o', requests: 524300, cost: 42150.00, avg_latency_ms: 890 },
                { model: 'claude-sonnet-4-20250514', requests: 312100, cost: 38420.00, avg_latency_ms: 1120 },
                { model: 'gpt-4o-mini', requests: 698200, cost: 12840.00, avg_latency_ms: 320 },
                { model: 'claude-haiku-4-20250414', requests: 201000, cost: 8200.00, avg_latency_ms: 280 },
                { model: 'gemini-2.5-pro', requests: 107000, cost: 15600.00, avg_latency_ms: 950 },
            ],
            '/dashboard/leaderboard': [
                { user_id: 'u1', name: 'Alice Chen', email: 'alice@acme.com', efficiency_score: 94.2, total_cost: 12450, requests: 89200 },
                { user_id: 'u2', name: 'Bob Martinez', email: 'bob@acme.com', efficiency_score: 91.7, total_cost: 10200, requests: 72100 },
                { user_id: 'u3', name: 'Carol Kim', email: 'carol@acme.com', efficiency_score: 88.4, total_cost: 15800, requests: 64300 },
                { user_id: 'u4', name: 'Dave Patel', email: 'dave@acme.com', efficiency_score: 85.1, total_cost: 8900, requests: 51200 },
                { user_id: 'u5', name: 'Eve Johnson', email: 'eve@acme.com', efficiency_score: 82.3, total_cost: 7400, requests: 43100 },
            ],
            '/dashboard/approvals': { pending: 7, approved_today: 12, rejected_today: 3, avg_approval_time_hours: 2.4, items: [
                { id: 'apr-1', requester: 'Bob Martinez', type: 'quota_increase', amount: 5000, status: 'pending', created_at: new Date().toISOString() },
                { id: 'apr-2', requester: 'Carol Kim', type: 'new_provider', amount: 0, status: 'pending', created_at: new Date().toISOString() },
            ]},
            '/dashboard/users': { total: 128, active: 94, new_this_month: 8, by_role: { admin: 4, manager: 12, user: 112 } },
            '/dashboard/teams': { total: 12, active: 10, by_size: { small: 5, medium: 4, large: 3 } },
            '/users/me': { id: 'demo-user', email: 'demo@alfred.ai', name: 'Demo User', role: 'admin', team: 'Platform Engineering', created_at: '2025-01-15T00:00:00Z', preferences: {} },
            '/admin/audit-logs': { items: [
                { id: 'al-1', timestamp: new Date().toISOString(), user: 'alice@acme.com', action: 'quota.update', resource: 'team:platform', details: 'Increased quota by 10,000 credits', severity: 'info' },
                { id: 'al-2', timestamp: new Date(Date.now() - 3600000).toISOString(), user: 'bob@acme.com', action: 'api_key.rotate', resource: 'key:prod-east', details: 'Rotated production API key', severity: 'warning' },
                { id: 'al-3', timestamp: new Date(Date.now() - 7200000).toISOString(), user: 'system', action: 'circuit_breaker.trip', resource: 'provider:openai', details: 'Error rate exceeded 15% threshold', severity: 'critical' },
                { id: 'al-4', timestamp: new Date(Date.now() - 10800000).toISOString(), user: 'carol@acme.com', action: 'user.create', resource: 'user:dave@acme.com', details: 'New user added to team Engineering', severity: 'info' },
                { id: 'al-5', timestamp: new Date(Date.now() - 14400000).toISOString(), user: 'system', action: 'cache.purge', resource: 'cache:semantic', details: 'TTL expired, 1,247 entries purged', severity: 'info' },
            ], total: 5, page: 1, per_page: 25 },
            '/admin/users': [
                { id: 'u1', email: 'alice@acme.com', name: 'Alice Chen', role: 'admin', team: 'Platform', status: 'active', credits_used: 12450, last_active: new Date().toISOString() },
                { id: 'u2', email: 'bob@acme.com', name: 'Bob Martinez', role: 'manager', team: 'ML Research', status: 'active', credits_used: 10200, last_active: new Date().toISOString() },
                { id: 'u3', email: 'carol@acme.com', name: 'Carol Kim', role: 'user', team: 'Product', status: 'active', credits_used: 15800, last_active: new Date().toISOString() },
                { id: 'u4', email: 'dave@acme.com', name: 'Dave Patel', role: 'user', team: 'Engineering', status: 'active', credits_used: 8900, last_active: new Date(Date.now() - 86400000).toISOString() },
                { id: 'u5', email: 'eve@acme.com', name: 'Eve Johnson', role: 'user', team: 'Data Science', status: 'inactive', credits_used: 7400, last_active: new Date(Date.now() - 604800000).toISOString() },
            ],
            '/admin/api-keys': [
                { id: 'k1', name: 'Production East', prefix: 'tp-prod-east-****', created: '2026-01-15', lastUsed: '2 min ago', requests30d: 42100, status: 'active', expiresIn: '85 days', scopes: ['read', 'write', 'admin'] },
                { id: 'k2', name: 'Staging', prefix: 'tp-stg-****', created: '2025-08-15', lastUsed: '1 hour ago', requests30d: 8900, status: 'active', expiresIn: '116 days', scopes: ['read', 'write'] },
                { id: 'k3', name: 'CI/CD Pipeline', prefix: 'tp-ci-****', created: '2025-09-01', lastUsed: '5 hours ago', requests30d: 3400, status: 'active', expiresIn: '30 days', scopes: ['read'] },
            ],
            '/teams/my-teams': [{ id: 't1', name: 'Platform Engineering', members: 8, budget: 50000, spent: 23400 }],
            '/config/integrations': { slack: { enabled: true, channel: '#alfred-alerts' }, teams: { enabled: false }, pagerduty: { enabled: true }, jira: { enabled: true, project: 'ALF' } },
            '/governance/experiments': [
                { id: 'exp-1', name: 'GPT-4o vs Claude Sonnet', status: 'running', created_at: '2025-12-01T00:00:00Z', variants: 2, traffic_pct: 10 },
                { id: 'exp-2', name: 'Cache TTL 30m vs 60m', status: 'completed', created_at: '2025-11-15T00:00:00Z', variants: 2, traffic_pct: 20 },
            ],
            '/governance/routing-rules': [
                { id: 'rr-1', name: 'Cost Optimization', priority: 1, condition: 'request.model == "gpt-4o"', action: 'route_to_cheapest', enabled: true },
                { id: 'rr-2', name: 'Data Residency EU', priority: 2, condition: 'user.region == "eu"', action: 'route_to_eu_provider', enabled: true },
            ],
            '/admin/request-log': { items: Array.from({ length: 30 }, (_, i) => {
                const models = ['gpt-4o', 'claude-sonnet-4-20250514', 'gpt-4o-mini', 'claude-haiku-4-20250414', 'gemini-2.5-pro'];
                const users = ['alice@acme.com', 'bob@acme.com', 'carol@acme.com', 'dave@acme.com', 'eve@acme.com'];
                const statuses = ['success', 'success', 'success', 'success', 'cached', 'error'];
                const ts = new Date(Date.now() - i * 120000);
                const inTok = Math.round(200 + Math.random() * 1800);
                const outTok = Math.round(100 + Math.random() * 2000);
                return { id: `req-${i}`, timestamp: ts.toISOString(), user: users[i % users.length], team: ['Platform', 'ML Research', 'Product'][i % 3], model: models[i % models.length], provider: ['openai', 'anthropic', 'google'][i % 3], input_tokens: inTok, output_tokens: outTok, cost: parseFloat(((inTok * 0.003 + outTok * 0.015) / 1000).toFixed(4)), latency_ms: Math.round(200 + Math.random() * 1500), status: statuses[i % statuses.length], routing_decision: i % 2 === 0 ? 'cost_optimized' : 'latency_optimized', cache_hit: statuses[i % statuses.length] === 'cached' };
            }), total: 30, summary: { total_requests: 1842567, success_rate: 98.4, cache_hit_rate: 34.2, avg_latency_ms: 420 } },
            '/admin/sso/config': { provider: 'okta', protocol: 'saml', entity_id: 'https://alfred.ai/saml/metadata', sso_url: 'https://acme.okta.com/app/alfred/sso/saml', certificate: '-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----', scim_enabled: true, scim_base_url: 'https://alfred.ai/scim/v2', domains: [{ domain: 'acme.com', verified: true }, { domain: 'acme.io', verified: false }], enforce_sso: false, jit_provisioning: true, default_role: 'user' },
            '/intelligence/forecast': { current_spend: 147832.50, daily_burn_rate: 4928.42, projected_month_end: 195320.00, budget_limit: 250000, days_until_limit: 21, confidence: 0.85 },
            '/prompts': [
                { id: 'p-1', name: 'Customer Support Classifier', description: 'Classifies support tickets by intent', template: 'Classify the following support ticket...', version: 3, status: 'APPROVED', author: 'alice@acme.com', tags: ['classification', 'support'], created_at: '2026-01-10T00:00:00Z', updated_at: '2026-02-15T00:00:00Z', usage_count: 42300, avg_latency_ms: 280 },
                { id: 'p-2', name: 'Code Review Assistant', description: 'Reviews code changes and suggests improvements', template: 'Review the following code diff...', version: 5, status: 'APPROVED', author: 'bob@acme.com', tags: ['code-review', 'engineering'], created_at: '2025-11-20T00:00:00Z', updated_at: '2026-02-10T00:00:00Z', usage_count: 18900, avg_latency_ms: 1200 },
                { id: 'p-3', name: 'Data Extraction Pipeline', description: 'Extracts structured data from documents', template: 'Extract the following fields...', version: 2, status: 'PENDING_REVIEW', author: 'carol@acme.com', tags: ['extraction', 'data'], created_at: '2026-02-01T00:00:00Z', updated_at: '2026-02-14T00:00:00Z', usage_count: 5200, avg_latency_ms: 890 },
            ],
            '/finops/exports': [
                { id: 'exp-1', name: 'Monthly Chargeback Report', type: 'csv', schedule: 'monthly', lastRun: '2026-02-01T08:00:00Z', status: 'success', records: 12450, costCenters: ['ENG-001', 'ML-002', 'PROD-003'], enabled: true },
                { id: 'exp-2', name: 'Snowflake Daily Sync', type: 'snowflake', schedule: 'daily', lastRun: '2026-02-18T06:00:00Z', status: 'success', records: 4820, costCenters: [], enabled: true },
                { id: 'exp-3', name: 'SAP Quarterly Export', type: 'sap', schedule: 'manual', lastRun: '2026-01-01T09:00:00Z', status: 'success', records: 38200, costCenters: ['FIN-010', 'ENG-001'], enabled: false },
            ],
        };
        // Match exact or prefix patterns
        if (demoData[e]) return Promise.resolve(demoData[e]);
        // Fallback: return empty object/array based on endpoint pattern
        if (e.includes('list') || e.endsWith('s') || e.includes('teams') || e.includes('users') || e.includes('keys') || e.includes('logs')) return Promise.resolve([]);
        return Promise.resolve({});
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

    async getApiKeys() {
        return this.fetchJson('/admin/api-keys');
    }

    async createApiKey(name, scopes = []) {
        return this.fetchJson('/admin/api-keys', {
            method: 'POST',
            body: JSON.stringify({ name, scopes }),
        });
    }

    async rotateApiKey(keyId) {
        return this.fetchJson(`/admin/api-keys/${keyId}/rotate`, {
            method: 'POST',
        });
    }

    async revokeApiKey(keyId) {
        return this.fetchJson(`/admin/api-keys/${keyId}`, {
            method: 'DELETE',
        });
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

    async getTransferHistory({ page = 1, pageSize = 20, status, walletId } = {}) {
        const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
        if (status) params.set('status', status);
        if (walletId) params.set('wallet_id', walletId);
        try {
            return await this.fetchJson(`/transfers?${params.toString()}`);
        } catch {
            // Fallback to dashboard endpoint for backwards compatibility
            return this.fetchJson(`/dashboard/transfers?limit=${pageSize}`);
        }
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

    async getAuditLogs(skip = 0, limit = 100) {
        return this.fetchJson(`/admin/audit-logs?skip=${skip}&limit=${limit}`);
    }

    async getExperiments() {
        return this.fetchJson('/experiments');
    }

    async getExperiment(id) {
        return this.fetchJson(`/experiments/${id}`);
    }

    async createExperiment(experiment) {
        return this.fetchJson('/experiments', {
            method: 'POST',
            body: JSON.stringify(experiment),
        });
    }

    async startExperiment(id) {
        return this.fetchJson(`/experiments/${id}/start`, {
            method: 'POST',
        });
    }

    async stopExperiment(id) {
        return this.fetchJson(`/experiments/${id}/stop`, {
            method: 'POST',
        });
    }

    async getAdminConfig() {
        return this.fetchJson('/admin/config');
    }

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
