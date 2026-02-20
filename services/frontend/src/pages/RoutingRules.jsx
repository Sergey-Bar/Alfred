/*
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Routing Rules page per UI.md Section 8. Shows active
             routing policies, model mapping, fallback chains,
             and allows CRUD on routing rules.
Root Cause:  UI spec requires Routing Rules at /routing.
Context:     Controls AI request routing — affects cost and latency.
Suitability: L3 model for routing configuration UI.
──────────────────────────────────────────────────────────────
*/
import {
    CheckCircle2,
    GitBranch,
    Pencil,
    Plus,
    Search,
    Trash2,
    XCircle
} from 'lucide-react';
import { useState } from 'react';

const DEMO_RULES = [
  { id: 1, name: 'Cost Optimization', description: 'Route simple queries to cheaper models', condition: 'token_estimate < 500', action: 'route_to: gpt-3.5-turbo', priority: 1, status: 'active', hits: 12840 },
  { id: 2, name: 'High-Priority Override', description: 'Critical requests always use GPT-4', condition: 'priority == critical', action: 'route_to: gpt-4-turbo', priority: 0, status: 'active', hits: 342 },
  { id: 3, name: 'Geo-Compliance EU', description: 'EU users routed to EU-hosted models', condition: 'user.region == EU', action: 'route_to: eu-claude-3', priority: 2, status: 'active', hits: 5620 },
  { id: 4, name: 'Anthropic Fallback', description: 'Fallback to Claude on OpenAI errors', condition: 'provider.openai.status == degraded', action: 'fallback_to: anthropic', priority: 3, status: 'disabled', hits: 0 },
  { id: 5, name: 'Code Generation Specialist', description: 'Code tasks routed to Claude Sonnet', condition: 'intent == code_generation', action: 'route_to: claude-3.5-sonnet', priority: 4, status: 'active', hits: 8920 },
];

function RuleRow({ rule }) {
  const statusConfig = {
    active: { badge: 'badge-green', icon: CheckCircle2, label: 'Active' },
    disabled: { badge: 'badge-yellow', icon: XCircle, label: 'Disabled' },
  };

  const s = statusConfig[rule.status] || statusConfig.disabled;

  return (
    <tr className="group">
      <td>
        <div>
          <p className="font-medium">{rule.name}</p>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>{rule.description}</p>
        </div>
      </td>
      <td>
        <code className="text-xs font-mono px-2 py-1 rounded" style={{ background: 'var(--color-primary-100)' }}>
          {rule.condition}
        </code>
      </td>
      <td>
        <code className="text-xs font-mono px-2 py-1 rounded" style={{ background: 'var(--color-accent-50)' }}>
          {rule.action}
        </code>
      </td>
      <td className="text-center">{rule.priority}</td>
      <td>
        <span className={`badge ${s.badge}`}>
          <s.icon className="w-3 h-3 mr-1" />
          {s.label}
        </span>
      </td>
      <td className="text-right">{rule.hits.toLocaleString()}</td>
      <td>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="btn btn-ghost p-1.5"><Pencil className="w-4 h-4" /></button>
          <button className="btn btn-ghost p-1.5 text-red-500"><Trash2 className="w-4 h-4" /></button>
        </div>
      </td>
    </tr>
  );
}

export default function RoutingRules() {
  const [rules, setRules] = useState(DEMO_RULES);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredRules = rules.filter(r =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2">
            <GitBranch className="w-6 h-6" style={{ color: 'var(--color-accent-600)' }} />
            Routing Rules
          </h1>
          <p className="subtitle">Configure intelligent model routing, fallbacks, and cost optimization policies</p>
        </div>
        <button className="btn btn-primary">
          <Plus className="w-4 h-4 mr-2" /> Create Rule
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat-card">
          <div className="stat-label">Active Rules</div>
          <div className="stat-value">{rules.filter(r => r.status === 'active').length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Hits (30d)</div>
          <div className="stat-value">{rules.reduce((s, r) => s + r.hits, 0).toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Cost Reduction</div>
          <div className="stat-value text-green-600">-23%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Failover Events</div>
          <div className="stat-value">7</div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
        <input
          type="text"
          placeholder="Search rules..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10"
          style={{ maxWidth: 400 }}
        />
      </div>

      {/* Rules Table */}
      <div className="card p-0 overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Rule</th>
              <th>Condition</th>
              <th>Action</th>
              <th className="text-center">Priority</th>
              <th>Status</th>
              <th className="text-right">Hits (30d)</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filteredRules.map(rule => <RuleRow key={rule.id} rule={rule} />)}
          </tbody>
        </table>
        {filteredRules.length === 0 && (
          <div className="empty-state">
            <GitBranch className="icon" />
            <h3>No routing rules found</h3>
            <p>Create your first routing rule to optimize model selection.</p>
          </div>
        )}
      </div>
    </div>
  );
}
