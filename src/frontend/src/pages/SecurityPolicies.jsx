/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Security & Policies page per UI.md Section 9. Shows
             safety pipeline status, PII detection config, prompt
             injection rules, and secret scanning settings.
Root Cause:  UI spec requires Security & Policies at /security.
Context:     Displays SafetyPipeline configuration status.
Suitability: L3 model for security configuration UI.
──────────────────────────────────────────────────────────────
*/
import {
    AlertTriangle,
    Settings,
    ShieldCheck
} from 'lucide-react';
import { useState } from 'react';

const POLICY_MODULES = [
  {
    id: 'pii',
    name: 'PII Detection',
    description: 'Scans prompts for personally identifiable information (SSN, credit cards, emails, phone numbers)',
    enabled: true,
    enforcement: 'block',
    detections: 847,
    lastTriggered: '2 hours ago',
  },
  {
    id: 'secrets',
    name: 'Secret Scanning',
    description: 'Detects API keys, passwords, tokens, and other credentials in prompt content',
    enabled: true,
    enforcement: 'block',
    detections: 234,
    lastTriggered: '5 hours ago',
  },
  {
    id: 'injection',
    name: 'Prompt Injection Guard',
    description: 'Detects jailbreak attempts, role manipulation, and instruction override patterns',
    enabled: true,
    enforcement: 'block',
    detections: 1203,
    lastTriggered: '30 min ago',
  },
  {
    id: 'blocklist',
    name: 'Custom Blocklist',
    description: 'Organization-defined blocked terms and patterns for compliance',
    enabled: true,
    enforcement: 'warn',
    detections: 56,
    lastTriggered: '1 day ago',
  },
];

function PolicyCard({ policy, onToggle }) {
  const enforcementColors = {
    block: 'badge-red',
    warn: 'badge-yellow',
    redact: 'badge-blue',
    allow: 'badge-green',
  };

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${policy.enabled ? 'bg-green-100' : 'bg-gray-100'}`}>
            <ShieldCheck className={`w-5 h-5 ${policy.enabled ? 'text-green-600' : 'text-gray-400'}`} />
          </div>
          <div>
            <h3 className="font-semibold">{policy.name}</h3>
            <p className="text-sm mt-1" style={{ color: 'var(--color-primary-500)' }}>{policy.description}</p>
          </div>
        </div>
        <button
          onClick={() => onToggle(policy.id)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${policy.enabled ? 'bg-green-500' : 'bg-gray-300'}`}
        >
          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${policy.enabled ? 'translate-x-6' : 'translate-x-1'}`} />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Enforcement</p>
          <span className={`badge ${enforcementColors[policy.enforcement]} mt-1`}>
            {policy.enforcement.toUpperCase()}
          </span>
        </div>
        <div>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Detections (30d)</p>
          <p className="font-semibold mt-1">{policy.detections.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Last Triggered</p>
          <p className="text-sm mt-1">{policy.lastTriggered}</p>
        </div>
      </div>
    </div>
  );
}

export default function SecurityPolicies() {
  const [policies, setPolicies] = useState(POLICY_MODULES);

  const togglePolicy = (id) => {
    setPolicies(prev => prev.map(p =>
      p.id === id ? { ...p, enabled: !p.enabled } : p
    ));
  };

  const totalDetections = policies.reduce((s, p) => s + p.detections, 0);
  const activeCount = policies.filter(p => p.enabled).length;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6" style={{ color: 'var(--color-accent-600)' }} />
            Security & Policies
          </h1>
          <p className="subtitle">Configure content safety, compliance rules, and threat detection</p>
        </div>
        <button className="btn btn-secondary">
          <Settings className="w-4 h-4 mr-2" /> Advanced Settings
        </button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat-card">
          <div className="stat-label">Active Policies</div>
          <div className="stat-value text-green-600">{activeCount}/{policies.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Detections (30d)</div>
          <div className="stat-value">{totalDetections.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Blocked Requests</div>
          <div className="stat-value text-red-600">2,284</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">False Positive Rate</div>
          <div className="stat-value">0.3%</div>
        </div>
      </div>

      {/* Security Alert */}
      <div className="card flex items-center gap-4 border-l-4" style={{ borderLeftColor: 'var(--color-warning-600)' }}>
        <AlertTriangle className="w-6 h-6 flex-shrink-0 text-yellow-600" />
        <div>
          <p className="font-medium">Security Advisory</p>
          <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>
            3 prompt injection attempts detected in the last hour. All were blocked by the injection guard.
          </p>
        </div>
        <button className="btn btn-secondary ml-auto whitespace-nowrap">View Details</button>
      </div>

      {/* Policy Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {policies.map(policy => (
          <PolicyCard key={policy.id} policy={policy} onToggle={togglePolicy} />
        ))}
      </div>
    </div>
  );
}
