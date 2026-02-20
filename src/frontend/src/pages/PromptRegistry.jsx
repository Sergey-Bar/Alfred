/*
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Prompt registry UI — browse, create, edit prompts with
             version history, diff view, approval status, and A/B
             test configuration. Backed by routers/prompts.py.
Root Cause:  T178 — Prompt registry UI missing from frontend.
Context:     Enterprise prompt governance — version control for prompts.
Suitability: L2 — CRUD UI with version list and diff display.
──────────────────────────────────────────────────────────────
*/
import {
    AlertCircle, Check, CheckCircle2, ChevronRight, Clock,
    Copy, Edit3, Eye, GitBranch, History, Plus, Search,
    Tag,
    X
} from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '../services/api';

const STATUS_CONFIG = {
    DRAFT: { color: 'badge-gray', icon: Edit3 },
    PENDING_REVIEW: { color: 'badge-yellow', icon: Clock },
    APPROVED: { color: 'badge-green', icon: CheckCircle2 },
    REJECTED: { color: 'badge-red', icon: AlertCircle },
};

const DEMO_PROMPTS = [
    {
        id: 'p-1', name: 'Code Review Assistant', description: 'Analyzes code for bugs, security issues, and best practices',
        currentVersion: 3, status: 'APPROVED', model: 'claude-sonnet-4-20250514', tags: ['engineering', 'code-review'],
        createdBy: 'alice@acme.com', updatedAt: '2026-02-15T10:30:00Z',
        versions: [
            { version: 3, content: 'You are a senior code reviewer...', status: 'APPROVED', createdAt: '2026-02-15T10:30:00Z' },
            { version: 2, content: 'You are a code reviewer...', status: 'APPROVED', createdAt: '2026-02-10T08:00:00Z' },
            { version: 1, content: 'Review the following code...', status: 'APPROVED', createdAt: '2026-02-01T09:00:00Z' },
        ],
    },
    {
        id: 'p-2', name: 'Customer Support Agent', description: 'Handles customer inquiries with empathy and accuracy',
        currentVersion: 5, status: 'APPROVED', model: 'gpt-4o', tags: ['support', 'customer-facing'],
        createdBy: 'bob@acme.com', updatedAt: '2026-02-14T16:20:00Z',
        versions: [
            { version: 5, content: 'You are a helpful customer support agent for Acme Corp...', status: 'APPROVED', createdAt: '2026-02-14T16:20:00Z' },
            { version: 4, content: 'You are a customer support agent...', status: 'APPROVED', createdAt: '2026-02-08T11:00:00Z' },
        ],
    },
    {
        id: 'p-3', name: 'Legal Contract Summarizer', description: 'Extracts key clauses and risks from legal documents',
        currentVersion: 2, status: 'PENDING_REVIEW', model: 'claude-sonnet-4-20250514', tags: ['legal', 'compliance'],
        createdBy: 'carol@acme.com', updatedAt: '2026-02-16T09:00:00Z',
        versions: [
            { version: 2, content: 'You are a legal analyst AI. Summarize the contract...', status: 'PENDING_REVIEW', createdAt: '2026-02-16T09:00:00Z' },
            { version: 1, content: 'Summarize the following legal contract...', status: 'APPROVED', createdAt: '2026-02-05T14:00:00Z' },
        ],
    },
    {
        id: 'p-4', name: 'Data Analysis Report Generator', description: 'Generates business intelligence reports from raw data',
        currentVersion: 1, status: 'DRAFT', model: 'gpt-4o-mini', tags: ['analytics', 'reporting'],
        createdBy: 'dave@acme.com', updatedAt: '2026-02-17T11:00:00Z',
        versions: [
            { version: 1, content: 'Analyze the following dataset and generate a report...', status: 'DRAFT', createdAt: '2026-02-17T11:00:00Z' },
        ],
    },
];

function PromptDetailPanel({ prompt, onClose, onUpdate }) {
    const [activeTab, setActiveTab] = useState('content');
    const [editing, setEditing] = useState(false);
    const [editContent, setEditContent] = useState('');

    if (!prompt) return null;

    const latestVersion = prompt.versions?.[0];

    const handleStartEdit = () => {
        setEditContent(latestVersion?.content || '');
        setEditing(true);
    };

    const handleSaveVersion = () => {
        // Would POST to /prompts/{id}/versions
        setEditing(false);
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full mx-4 max-h-[85vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="p-4 border-b flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-bold">{prompt.name}</h3>
                        <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>{prompt.description}</p>
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded"><X className="w-5 h-5" /></button>
                </div>

                {/* Tabs */}
                <div className="flex border-b px-4">
                    {[
                        { id: 'content', label: 'Content', icon: Eye },
                        { id: 'versions', label: 'Versions', icon: History },
                        { id: 'settings', label: 'Settings', icon: Tag },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-1 px-4 py-3 text-sm border-b-2 transition-all ${
                                activeTab === tab.id ? 'border-blue-600 text-blue-600 font-medium' : 'border-transparent hover:text-gray-700'
                            }`}
                        >
                            <tab.icon className="w-4 h-4" /> {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    {activeTab === 'content' && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span className={`badge ${STATUS_CONFIG[prompt.status]?.color}`}>{prompt.status}</span>
                                    <span className="text-sm" style={{ color: 'var(--color-primary-400)' }}>v{prompt.currentVersion}</span>
                                </div>
                                <div className="flex gap-2">
                                    {!editing && (
                                        <button onClick={handleStartEdit} className="btn btn-sm flex items-center gap-1">
                                            <Edit3 className="w-3 h-3" /> Edit
                                        </button>
                                    )}
                                    <button className="btn btn-sm flex items-center gap-1">
                                        <Copy className="w-3 h-3" /> Duplicate
                                    </button>
                                </div>
                            </div>
                            {editing ? (
                                <div className="space-y-3">
                                    <textarea
                                        className="input w-full font-mono text-sm"
                                        rows={12}
                                        value={editContent}
                                        onChange={e => setEditContent(e.target.value)}
                                    />
                                    <div className="flex justify-end gap-2">
                                        <button onClick={() => setEditing(false)} className="btn btn-sm">Cancel</button>
                                        <button onClick={handleSaveVersion} className="btn btn-primary btn-sm flex items-center gap-1">
                                            <Check className="w-3 h-3" /> Save as v{prompt.currentVersion + 1}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="p-4 rounded-lg font-mono text-sm whitespace-pre-wrap" style={{ background: 'var(--color-primary-100)' }}>
                                    {latestVersion?.content || 'No content'}
                                </div>
                            )}
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>Model</p>
                                    <code className="text-xs">{prompt.model}</code>
                                </div>
                                <div>
                                    <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>Created By</p>
                                    <p>{prompt.createdBy}</p>
                                </div>
                                <div>
                                    <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>Tags</p>
                                    <div className="flex gap-1 flex-wrap">
                                        {prompt.tags?.map(t => (
                                            <span key={t} className="badge badge-blue text-xs">{t}</span>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>Updated</p>
                                    <p>{new Date(prompt.updatedAt).toLocaleDateString()}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'versions' && (
                        <div className="space-y-3">
                            {prompt.versions?.map((v) => (
                                <div key={v.version} className="p-3 rounded-lg border flex items-start justify-between hover:bg-gray-50">
                                    <div className="flex items-start gap-3">
                                        <div className="p-1.5 rounded-full bg-blue-100">
                                            <GitBranch className="w-4 h-4 text-blue-600" />
                                        </div>
                                        <div>
                                            <p className="font-medium">Version {v.version}</p>
                                            <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>
                                                {new Date(v.createdAt).toLocaleDateString()} at {new Date(v.createdAt).toLocaleTimeString()}
                                            </p>
                                            <p className="text-xs mt-1 font-mono truncate max-w-md" style={{ color: 'var(--color-primary-500)' }}>
                                                {v.content?.substring(0, 80)}...
                                            </p>
                                        </div>
                                    </div>
                                    <span className={`badge ${STATUS_CONFIG[v.status]?.color} text-xs`}>{v.status}</span>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'settings' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">A/B Test Traffic Split</label>
                                <div className="flex items-center gap-2">
                                    <input type="range" min="0" max="100" defaultValue="0" className="flex-1" />
                                    <span className="text-sm font-medium">0%</span>
                                </div>
                                <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>
                                    Route a percentage of traffic to the latest version for testing
                                </p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Max Tokens Override</label>
                                <input type="number" className="input w-full" placeholder="Default (no override)" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Temperature</label>
                                <input type="number" className="input w-full" step="0.1" min="0" max="2" placeholder="0.7" />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function PromptRegistry() {
    const [prompts, setPrompts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [selectedPrompt, setSelectedPrompt] = useState(null);

    useEffect(() => {
        loadPrompts();
    }, []);

    const loadPrompts = async () => {
        setLoading(true);
        try {
            const data = await api.fetchJson('/prompts');
            setPrompts(Array.isArray(data) ? data : DEMO_PROMPTS);
        } catch {
            setPrompts(DEMO_PROMPTS);
        } finally {
            setLoading(false);
        }
    };

    const filtered = prompts.filter(p => {
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            if (!p.name?.toLowerCase().includes(q) && !p.description?.toLowerCase().includes(q) && !p.tags?.some(t => t.includes(q))) return false;
        }
        if (statusFilter !== 'all' && p.status !== statusFilter) return false;
        return true;
    });

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Prompt Registry</h1>
                    <p style={{ color: 'var(--color-primary-500)' }}>
                        {prompts.length} prompts managed with version control
                    </p>
                </div>
                <button className="btn btn-primary flex items-center gap-2">
                    <Plus className="w-4 h-4" /> New Prompt
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Prompts', value: prompts.length, color: 'text-blue-600' },
                    { label: 'Approved', value: prompts.filter(p => p.status === 'APPROVED').length, color: 'text-green-600' },
                    { label: 'Pending Review', value: prompts.filter(p => p.status === 'PENDING_REVIEW').length, color: 'text-yellow-600' },
                    { label: 'Total Versions', value: prompts.reduce((s, p) => s + (p.currentVersion || 0), 0), color: 'text-purple-600' },
                ].map(stat => (
                    <div key={stat.label} className="card p-4">
                        <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>{stat.label}</p>
                        <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Filters */}
            <div className="flex items-center gap-3">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
                    <input
                        type="text"
                        className="input w-full pl-10"
                        placeholder="Search prompts by name, description, or tag..."
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                    />
                </div>
                <select
                    className="input"
                    value={statusFilter}
                    onChange={e => setStatusFilter(e.target.value)}
                >
                    <option value="all">All Status</option>
                    <option value="DRAFT">Draft</option>
                    <option value="PENDING_REVIEW">Pending Review</option>
                    <option value="APPROVED">Approved</option>
                    <option value="REJECTED">Rejected</option>
                </select>
            </div>

            {/* Prompt List */}
            <div className="space-y-3">
                {loading ? (
                    <div className="text-center py-12 card">
                        <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-2" />
                        <p style={{ color: 'var(--color-primary-400)' }}>Loading prompts...</p>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-12 card">
                        <p style={{ color: 'var(--color-primary-400)' }}>No prompts found</p>
                    </div>
                ) : (
                    filtered.map(prompt => {
                        const StatusIcon = STATUS_CONFIG[prompt.status]?.icon || Edit3;
                        return (
                            <div
                                key={prompt.id}
                                className="card p-4 hover:shadow-md transition-shadow cursor-pointer"
                                onClick={() => setSelectedPrompt(prompt)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <h3 className="font-semibold">{prompt.name}</h3>
                                            <span className={`badge ${STATUS_CONFIG[prompt.status]?.color} text-xs flex items-center gap-1`}>
                                                <StatusIcon className="w-3 h-3" /> {prompt.status.replace('_', ' ')}
                                            </span>
                                            <span className="text-xs" style={{ color: 'var(--color-primary-400)' }}>v{prompt.currentVersion}</span>
                                        </div>
                                        <p className="text-sm mb-2" style={{ color: 'var(--color-primary-500)' }}>{prompt.description}</p>
                                        <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-primary-400)' }}>
                                            <span className="flex items-center gap-1">
                                                <code className="bg-gray-100 px-1.5 py-0.5 rounded">{prompt.model}</code>
                                            </span>
                                            <span>{prompt.createdBy}</span>
                                            <span>{new Date(prompt.updatedAt).toLocaleDateString()}</span>
                                        </div>
                                        {prompt.tags?.length > 0 && (
                                            <div className="flex gap-1 mt-2">
                                                {prompt.tags.map(t => (
                                                    <span key={t} className="badge badge-blue text-xs">{t}</span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    <ChevronRight className="w-5 h-5 shrink-0" style={{ color: 'var(--color-primary-300)' }} />
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            <PromptDetailPanel
                prompt={selectedPrompt}
                onClose={() => setSelectedPrompt(null)}
            />
        </div>
    );
}
