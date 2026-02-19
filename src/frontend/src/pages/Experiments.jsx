/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       A/B Experiments page per UI.md Section 16. Displays
             experiment list with variant metrics, p-values,
             lift percentages, and confidence indicators.
Root Cause:  UI spec requires Experiments at /experiments.
Context:     Supports model A/B testing for cost/quality tradeoffs.
Suitability: L3 model for experiment UI with statistical displays.
──────────────────────────────────────────────────────────────
*/
import {
    ArrowDownRight,
    ArrowUpRight,
    CheckCircle2,
    Clock,
    Filter,
    FlaskConical,
    Pause,
    Play,
    Plus,
    Users
} from 'lucide-react';
import { useState } from 'react';

const DEMO_EXPERIMENTS = [
  {
    id: 1,
    name: 'GPT-4o vs Claude Sonnet for Support',
    description: 'Compare response quality & cost for customer support queries',
    status: 'running',
    startDate: '2026-02-10',
    traffic: 50,
    variants: [
      { name: 'Control (GPT-4o)', requests: 12400, avgLatency: 1.2, avgCost: 0.032, quality: 4.2 },
      { name: 'Variant (Claude Sonnet)', requests: 12380, avgLatency: 0.9, avgCost: 0.028, quality: 4.5 },
    ],
    lift: '+7.1%',
    liftDirection: 'up',
    pValue: 0.023,
    confidence: 97.7,
  },
  {
    id: 2,
    name: 'Haiku vs GPT-4o-mini for Classification',
    description: 'Test intent classification accuracy with smaller models',
    status: 'running',
    startDate: '2026-02-15',
    traffic: 30,
    variants: [
      { name: 'Control (GPT-4o-mini)', requests: 5600, avgLatency: 0.4, avgCost: 0.002, quality: 3.8 },
      { name: 'Variant (Haiku)', requests: 5580, avgLatency: 0.3, avgCost: 0.001, quality: 3.9 },
    ],
    lift: '+2.6%',
    liftDirection: 'up',
    pValue: 0.18,
    confidence: 82.0,
  },
  {
    id: 3,
    name: 'Semantic Cache Impact on Latency',
    description: 'Measure latency reduction with semantic caching enabled',
    status: 'completed',
    startDate: '2026-01-20',
    traffic: 100,
    variants: [
      { name: 'Control (No Cache)', requests: 28000, avgLatency: 1.8, avgCost: 0.041, quality: 4.1 },
      { name: 'Variant (Cache On)', requests: 28000, avgLatency: 0.6, avgCost: 0.015, quality: 4.1 },
    ],
    lift: '-63.4%',
    liftDirection: 'down',
    pValue: 0.001,
    confidence: 99.9,
  },
];

function StatusBadge({ status }) {
  const styles = {
    running: 'badge-blue',
    completed: 'badge-green',
    paused: 'badge-yellow',
    draft: 'badge-gray',
  };
  const icons = {
    running: <Play className="w-3 h-3 mr-1" />,
    completed: <CheckCircle2 className="w-3 h-3 mr-1" />,
    paused: <Pause className="w-3 h-3 mr-1" />,
  };
  return (
    <span className={`badge ${styles[status] || 'badge-gray'}`}>
      {icons[status]} {status}
    </span>
  );
}

function ExperimentCard({ experiment }) {
  const isSignificant = experiment.pValue < 0.05;

  return (
    <div className="card space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-base">{experiment.name}</h3>
          <p className="text-sm mt-1" style={{ color: 'var(--color-primary-500)' }}>
            {experiment.description}
          </p>
        </div>
        <StatusBadge status={experiment.status} />
      </div>

      {/* Meta */}
      <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--color-primary-500)' }}>
        <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Started {experiment.startDate}</span>
        <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {experiment.traffic}% traffic</span>
      </div>

      {/* Variants Table */}
      <div className="overflow-hidden rounded-lg" style={{ border: '1px solid var(--color-border)' }}>
        <table className="w-full text-sm">
          <thead>
            <tr style={{ background: 'var(--color-primary-100)' }}>
              <th className="text-left px-3 py-2 font-medium">Variant</th>
              <th className="text-right px-3 py-2 font-medium">Requests</th>
              <th className="text-right px-3 py-2 font-medium">Avg Latency</th>
              <th className="text-right px-3 py-2 font-medium">Avg Cost</th>
              <th className="text-right px-3 py-2 font-medium">Quality</th>
            </tr>
          </thead>
          <tbody>
            {experiment.variants.map((v, i) => (
              <tr key={i} style={{ borderTop: '1px solid var(--color-border)' }}>
                <td className="px-3 py-2 font-medium">{v.name}</td>
                <td className="px-3 py-2 text-right">{v.requests.toLocaleString()}</td>
                <td className="px-3 py-2 text-right">{v.avgLatency}s</td>
                <td className="px-3 py-2 text-right">${v.avgCost.toFixed(3)}</td>
                <td className="px-3 py-2 text-right">{v.quality}/5.0</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Results Row */}
      <div className="flex items-center justify-between pt-2" style={{ borderTop: '1px solid var(--color-border)' }}>
        <div className="flex items-center gap-6">
          <div>
            <span className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Lift</span>
            <p className={`font-semibold flex items-center gap-1 ${experiment.liftDirection === 'up' ? 'text-green-600' : 'text-blue-600'}`}>
              {experiment.liftDirection === 'up' ?
                <ArrowUpRight className="w-4 h-4" /> :
                <ArrowDownRight className="w-4 h-4" />}
              {experiment.lift}
            </p>
          </div>
          <div>
            <span className="text-xs" style={{ color: 'var(--color-primary-500)' }}>p-value</span>
            <p className="font-semibold">{experiment.pValue}</p>
          </div>
          <div>
            <span className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Confidence</span>
            <p className="font-semibold">{experiment.confidence}%</p>
          </div>
        </div>
        <div>
          {isSignificant ? (
            <span className="badge badge-green">
              <CheckCircle2 className="w-3 h-3 mr-1" /> Statistically Significant
            </span>
          ) : (
            <span className="badge badge-yellow">
              <Clock className="w-3 h-3 mr-1" /> Needs More Data
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Experiments() {
  const [experiments] = useState(DEMO_EXPERIMENTS);
  const [filterStatus, setFilterStatus] = useState('all');

  const filtered = filterStatus === 'all'
    ? experiments
    : experiments.filter(e => e.status === filterStatus);

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2">
            <FlaskConical className="w-6 h-6" style={{ color: 'var(--color-accent-600)' }} />
            Experiments
          </h1>
          <p className="subtitle">A/B test models, prompts, and routing strategies</p>
        </div>
        <button className="btn btn-primary">
          <Plus className="w-4 h-4 mr-2" /> New Experiment
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="stat-card">
          <span className="label">Running</span>
          <span className="value">{experiments.filter(e => e.status === 'running').length}</span>
        </div>
        <div className="stat-card">
          <span className="label">Completed</span>
          <span className="value">{experiments.filter(e => e.status === 'completed').length}</span>
        </div>
        <div className="stat-card">
          <span className="label">Significant Results</span>
          <span className="value">{experiments.filter(e => e.pValue < 0.05).length}</span>
        </div>
        <div className="stat-card">
          <span className="label">Total Requests</span>
          <span className="value">{experiments.reduce((sum, e) => sum + e.variants.reduce((s, v) => s + v.requests, 0), 0).toLocaleString()}</span>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4" style={{ color: 'var(--color-primary-500)' }} />
        {['all', 'running', 'completed', 'paused'].map(s => (
          <button
            key={s}
            className={`btn ${filterStatus === s ? 'btn-primary' : 'btn-ghost'} text-sm px-3 py-1`}
            onClick={() => setFilterStatus(s)}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Experiment List */}
      <div className="space-y-4">
        {filtered.map(exp => (
          <ExperimentCard key={exp.id} experiment={exp} />
        ))}
        {filtered.length === 0 && (
          <div className="empty-state">
            <FlaskConical className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--color-primary-400)' }} />
            <p className="font-medium">No experiments found</p>
            <p className="text-sm mt-1">Create a new experiment to start A/B testing.</p>
          </div>
        )}
      </div>
    </div>
  );
}
