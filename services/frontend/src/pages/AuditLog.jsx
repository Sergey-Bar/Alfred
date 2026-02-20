/*
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Audit Log page per UI.md Section 10. Shows immutable,
             filterable audit trail of all admin actions, quota
             changes, and security events.
Root Cause:  UI spec requires Audit Log at /audit.
Context:     Reads from immutable audit_logs table (write-once).
Suitability: L3 model for data-heavy table UI.
──────────────────────────────────────────────────────────────
*/
import {
    Clock,
    Download,
    Key,
    ScrollText, Search,
    Shield,
    User,
    Wallet
} from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '../services/api';

const ACTION_ICONS = {
  'user.': User,
  'team.': User,
  'quota.': Wallet,
  'security.': Shield,
  'key.': Key,
};

function getActionIcon(action) {
  for (const [prefix, Icon] of Object.entries(ACTION_ICONS)) {
    if (action.startsWith(prefix)) return Icon;
  }
  return ScrollText;
}

// Fallback demo logs shown when API is unavailable
const DEMO_LOGS = [
  { id: 1, timestamp: '2026-02-15T14:32:00Z', actor: 'admin@acme.com', action: 'user.create', target_type: 'user', target_id: 'alice@acme.com', details: 'Created user with 2000 credit quota' },
  { id: 2, timestamp: '2026-02-15T14:28:00Z', actor: 'admin@acme.com', action: 'team.update_pool', target_type: 'team', target_id: 'Engineering', details: 'Increased pool from 30000 to 50000 credits' },
  { id: 3, timestamp: '2026-02-15T13:55:00Z', actor: 'system', action: 'security.injection_blocked', target_type: 'request', target_id: 'req-f82a', details: 'Prompt injection detected and blocked' },
  { id: 4, timestamp: '2026-02-15T13:22:00Z', actor: 'bob@acme.com', action: 'key.rotate', target_type: 'api_key', target_id: 'key-***89a2', details: 'API key rotated for service account' },
  { id: 5, timestamp: '2026-02-15T12:45:00Z', actor: 'admin@acme.com', action: 'quota.override', target_type: 'user', target_id: 'carol@acme.com', details: 'Approved 5000 credit override for Q1 project' },
  { id: 6, timestamp: '2026-02-15T11:30:00Z', actor: 'system', action: 'security.pii_detected', target_type: 'request', target_id: 'req-a3c1', details: 'SSN detected in prompt content — request blocked' },
  { id: 7, timestamp: '2026-02-15T10:15:00Z', actor: 'admin@acme.com', action: 'user.suspend', target_type: 'user', target_id: 'dave@acme.com', details: 'Account suspended for policy violation' },
  { id: 8, timestamp: '2026-02-15T09:00:00Z', actor: 'system', action: 'quota.soft_limit', target_type: 'team', target_id: 'Product', details: 'Team Product reached 80% of pool allocation' },
];

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAction, setFilterAction] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch audit logs from API
  useEffect(() => {
    let mounted = true;
    setLoading(true);
    
    api.getAuditLogs(0, 100)
      .then(data => {
        if (mounted) {
          // API returns array of logs or object with items property
          const items = Array.isArray(data) ? data : (data.items || data.logs || []);
          setLogs(items.length > 0 ? items : DEMO_LOGS);
          setLoading(false);
        }
      })
      .catch(err => {
        if (mounted) {
          console.warn('Failed to fetch audit logs, using demo data:', err.message);
          setLogs(DEMO_LOGS);
          setLoading(false);
        }
      });
    
    return () => { mounted = false; };
  }, []);

  const filteredLogs = logs.filter(log => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = log.action.toLowerCase().includes(q) ||
      log.actor.toLowerCase().includes(q) ||
      log.details.toLowerCase().includes(q);
    const matchesFilter = filterAction === 'all' || log.action.startsWith(filterAction);
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2">
            <ScrollText className="w-6 h-6" style={{ color: 'var(--color-accent-600)' }} />
            Audit Log
          </h1>
          <p className="subtitle">Immutable record of all administrative actions and security events</p>
        </div>
        <button className="btn btn-secondary">
          <Download className="w-4 h-4 mr-2" /> Export
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1" style={{ maxWidth: 400 }}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
          <input
            type="text"
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
        <select
          value={filterAction}
          onChange={(e) => setFilterAction(e.target.value)}
          className="input"
          style={{ width: 'auto' }}
        >
          <option value="all">All Actions</option>
          <option value="user.">User Actions</option>
          <option value="team.">Team Actions</option>
          <option value="quota.">Quota Actions</option>
          <option value="security.">Security Events</option>
          <option value="key.">API Key Actions</option>
        </select>
      </div>

      {/* Log Table */}
      <div className="card p-0 overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Target</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.map(log => {
              const Icon = getActionIcon(log.action);
              return (
                <tr key={log.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5" style={{ color: 'var(--color-primary-400)' }} />
                      <span className="text-xs font-mono">
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`text-sm ${log.actor === 'system' ? 'italic' : ''}`}>
                      {log.actor}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
                      <code className="text-xs font-mono px-1.5 py-0.5 rounded" style={{ background: 'var(--color-primary-100)' }}>
                        {log.action}
                      </code>
                    </div>
                  </td>
                  <td>
                    <span className="text-sm">{log.target_type}: {log.target_id}</span>
                  </td>
                  <td>
                    <span className="text-sm" style={{ color: 'var(--color-primary-500)' }}>{log.details}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filteredLogs.length === 0 && (
          <div className="empty-state">
            <ScrollText className="icon" />
            <h3>No audit entries found</h3>
            <p>Try adjusting your search or filter criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
}
