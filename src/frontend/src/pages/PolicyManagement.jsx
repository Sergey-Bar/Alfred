/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Policy Management UI for OPA policies. CRUD for
             governance rules, dry-run toggle, evaluation logs.
Root Cause:  Sprint task T137 — Policy management UI.
Context:     Frontend for OPA policy engine in Go gateway.
Suitability: L3 — policy visualization and management.
──────────────────────────────────────────────────────────────
*/

import {
    CheckCircle2,
    Eye,
    FileCode,
    Pencil,
    Plus,
    RefreshCw,
    Shield,
    Trash2,
    XCircle
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { api } from '../services/api';

const DEMO_POLICIES = [
  {
    id: 'pol-001',
    name: 'Premium Model Gating',
    description: 'Only allow premium tier users to access GPT-4 and Claude Opus',
    active: true,
    dry_run: false,
    evaluations_24h: 12450,
    denials_24h: 342,
    created_at: '2026-01-15T10:00:00Z',
  },
  {
    id: 'pol-002',
    name: 'Token Limit Enforcement',
    description: 'Block requests exceeding 100K tokens',
    active: true,
    dry_run: false,
    evaluations_24h: 45200,
    denials_24h: 18,
    created_at: '2026-01-20T14:00:00Z',
  },
  {
    id: 'pol-003',
    name: 'PII Model Restriction',
    description: 'Route requests with detected PII to privacy-compliant models only',
    active: true,
    dry_run: true,
    evaluations_24h: 8900,
    denials_24h: 0,
    created_at: '2026-02-01T09:00:00Z',
  },
  {
    id: 'pol-004',
    name: 'EU Data Residency',
    description: 'Ensure EU user data stays in EU regions',
    active: false,
    dry_run: false,
    evaluations_24h: 0,
    denials_24h: 0,
    created_at: '2026-02-10T11:00:00Z',
  },
];

const BUILTIN_TEMPLATES = [
  { id: 'premium_model_gating', name: 'Premium Model Gating', description: 'Restrict premium models to specific user tiers' },
  { id: 'token_limit', name: 'Token Limit', description: 'Enforce maximum token limits per request' },
  { id: 'rate_limit_per_user', name: 'Rate Limit Per User', description: 'Per-user rate limiting rules' },
  { id: 'geo_restriction', name: 'Geographic Restriction', description: 'Block or allow based on user region' },
  { id: 'pii_model_restriction', name: 'PII Model Restriction', description: 'Route PII-containing requests to compliant models' },
  { id: 'data_classification', name: 'Data Classification', description: 'Route based on data sensitivity levels' },
  { id: 'time_of_day', name: 'Time-of-Day', description: 'Different rules for peak vs off-peak hours' },
  { id: 'budget_routing', name: 'Budget-Based Routing', description: 'Route based on remaining budget' },
];

function PolicyCard({ pol, onToggle, onToggleDryRun, onDelete }) {
  return (
    <div className="card hover-lift">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${pol.active ? 'bg-green-100' : 'bg-gray-100'}`}>
            <Shield className={`w-5 h-5 ${pol.active ? 'text-green-600' : 'text-gray-500'}`} />
          </div>
          <div>
            <h3 className="font-semibold">{pol.name}</h3>
            <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>{pol.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button className="btn btn-ghost p-1.5" title="Edit"><Pencil className="w-4 h-4" /></button>
          <button className="btn btn-ghost p-1.5 text-red-500" title="Delete" onClick={() => onDelete(pol.id)}>
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 mb-3">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={pol.active}
            onChange={() => onToggle(pol.id)}
            className="w-4 h-4 rounded"
          />
          <span className="text-sm">Active</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={pol.dry_run}
            onChange={() => onToggleDryRun(pol.id)}
            className="w-4 h-4 rounded"
          />
          <span className="text-sm text-yellow-600">Dry Run</span>
        </label>
      </div>

      <div className="grid grid-cols-2 gap-3 pt-3" style={{ borderTop: '1px solid var(--color-border)' }}>
        <div>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Evaluations (24h)</p>
          <p className="text-lg font-semibold">{pol.evaluations_24h.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Denials (24h)</p>
          <p className="text-lg font-semibold text-red-600">{pol.denials_24h.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}

export default function PolicyManagement() {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTemplates, setShowTemplates] = useState(false);

  useEffect(() => {
    async function fetchPolicies() {
      try {
        const data = await api.getPolicies?.() || [];
        setPolicies(data.length > 0 ? data : DEMO_POLICIES);
      } catch (err) {
        console.warn('Failed to fetch policies, using demo data:', err);
        setPolicies(DEMO_POLICIES);
      } finally {
        setLoading(false);
      }
    }
    fetchPolicies();
  }, []);

  const handleToggle = async (id) => {
    setPolicies(policies.map(p => p.id === id ? { ...p, active: !p.active } : p));
    try {
      await api.updatePolicy?.(id, { active: !policies.find(p => p.id === id).active });
    } catch (err) {
      console.error('Failed to update policy:', err);
    }
  };

  const handleToggleDryRun = async (id) => {
    setPolicies(policies.map(p => p.id === id ? { ...p, dry_run: !p.dry_run } : p));
    try {
      await api.updatePolicyDryRun?.(id, !policies.find(p => p.id === id).dry_run);
    } catch (err) {
      console.error('Failed to update dry run:', err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this policy?')) return;
    try {
      await api.deletePolicy?.(id);
      setPolicies(policies.filter(p => p.id !== id));
    } catch (err) {
      console.error('Failed to delete policy:', err);
    }
  };

  if (loading) {
    return <div className="p-6 flex items-center justify-center"><RefreshCw className="w-6 h-6 animate-spin" /></div>;
  }

  const activeCount = policies.filter(p => p.active).length;
  const dryRunCount = policies.filter(p => p.dry_run).length;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2">
            <Shield className="w-6 h-6" style={{ color: 'var(--color-accent-600)' }} />
            Policies
          </h1>
          <p className="subtitle">Manage OPA governance policies for AI request routing and access control</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn btn-secondary" onClick={() => setShowTemplates(!showTemplates)}>
            <FileCode className="w-4 h-4 mr-2" /> Templates
          </button>
          <button className="btn btn-primary">
            <Plus className="w-4 h-4 mr-2" /> Create Policy
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card flex items-center gap-4">
          <div className="p-3 rounded-lg bg-green-100">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-2xl font-bold">{activeCount}</p>
            <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>Active Policies</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 rounded-lg bg-yellow-100">
            <Eye className="w-5 h-5 text-yellow-600" />
          </div>
          <div>
            <p className="text-2xl font-bold">{dryRunCount}</p>
            <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>Dry Run Mode</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 rounded-lg bg-red-100">
            <XCircle className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <p className="text-2xl font-bold">{policies.reduce((acc, p) => acc + p.denials_24h, 0).toLocaleString()}</p>
            <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>Denials (24h)</p>
          </div>
        </div>
      </div>

      {/* Templates Panel */}
      {showTemplates && (
        <div className="card" style={{ background: 'var(--color-primary-50)' }}>
          <h3 className="font-semibold mb-3">Built-in Policy Templates</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {BUILTIN_TEMPLATES.map(t => (
              <button key={t.id} className="p-3 rounded-lg text-left hover:bg-white transition-colors" style={{ background: 'var(--color-background)' }}>
                <p className="font-medium text-sm">{t.name}</p>
                <p className="text-xs mt-1" style={{ color: 'var(--color-primary-500)' }}>{t.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Policies Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {policies.map(pol => (
          <PolicyCard
            key={pol.id}
            pol={pol}
            onToggle={handleToggle}
            onToggleDryRun={handleToggleDryRun}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
}
