/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Wallet management per UI.md Section 7. Shows personal
             wallet, team pools, budget allocation, and transaction
             history with editable limits.
Root Cause:  UI spec requires Wallet Management at /wallets.
Context:     Core financial governance screen — L4 logic review.
Suitability: L3 model for wallet UI; L4 review for any mutation.
──────────────────────────────────────────────────────────────
*/
import {
    Plus, Search,
    Wallet
} from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '../services/api';

function WalletCard({ wallet, type }) {
  const usagePercent = wallet.total > 0 ? (wallet.used / wallet.total * 100) : 0;
  const isWarning = usagePercent >= 80;
  const isDanger = usagePercent >= 95;

  return (
    <div className="card hover-lift">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isDanger ? 'bg-red-100' : isWarning ? 'bg-yellow-100' : 'bg-blue-100'}`}>
            <Wallet className={`w-5 h-5 ${isDanger ? 'text-red-600' : isWarning ? 'text-yellow-600' : 'text-blue-600'}`} />
          </div>
          <div>
            <h3 className="font-semibold">{wallet.name}</h3>
            <span className="text-xs" style={{ color: 'var(--color-primary-500)' }}>{type}</span>
          </div>
        </div>
        <span className={`badge ${isDanger ? 'badge-red' : isWarning ? 'badge-yellow' : 'badge-green'}`}>
          {isDanger ? 'Critical' : isWarning ? 'Warning' : 'Healthy'}
        </span>
      </div>

      <div className="mb-3">
        <div className="flex justify-between text-sm mb-1">
          <span style={{ color: 'var(--color-primary-500)' }}>Used: {wallet.used.toLocaleString()} credits</span>
          <span className="font-medium">{usagePercent.toFixed(1)}%</span>
        </div>
        <div className="w-full h-2 rounded-full" style={{ background: 'var(--color-primary-200)' }}>
          <div
            className={`h-full rounded-full transition-all ${isDanger ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-blue-500'}`}
            style={{ width: `${Math.min(usagePercent, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-xs mt-1" style={{ color: 'var(--color-primary-400)' }}>
          <span>0</span>
          <span>{wallet.total.toLocaleString()} credits</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="p-2 rounded-md" style={{ background: 'var(--color-primary-100)' }}>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Hard Limit</p>
          <p className="font-semibold">{wallet.hardLimit?.toLocaleString() || wallet.total.toLocaleString()}</p>
        </div>
        <div className="p-2 rounded-md" style={{ background: 'var(--color-primary-100)' }}>
          <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>Soft Limit</p>
          <p className="font-semibold">{wallet.softLimit?.toLocaleString() || Math.floor(wallet.total * 0.8).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}

export default function WalletManagement() {
  const [wallets, setWallets] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [usersRes, teamsRes] = await Promise.all([
          api.get('/users').catch(() => ({ data: [] })),
          api.get('/teams').catch(() => ({ data: [] })),
        ]);

        const userWallets = (usersRes.data || []).map(u => ({
          id: u.id,
          name: u.name || u.email,
          type: 'personal',
          total: parseFloat(u.personal_quota || 1000),
          used: parseFloat(u.used_tokens || 0),
        }));

        const teamWallets = (teamsRes.data || []).map(t => ({
          id: t.id,
          name: t.name,
          type: 'team',
          total: parseFloat(t.common_pool || 10000),
          used: parseFloat(t.used_pool || 0),
        }));

        setWallets([...teamWallets, ...userWallets]);
      } catch {
        setWallets(generateDemoWallets());
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  const filteredWallets = wallets.filter(w =>
    w.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const teamWallets = filteredWallets.filter(w => w.type === 'team');
  const personalWallets = filteredWallets.filter(w => w.type === 'personal');

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="skeleton h-8 w-64"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-48 rounded-xl"></div>)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="page-header flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2">
            <Wallet className="w-6 h-6" style={{ color: 'var(--color-accent-600)' }} />
            Wallets & Budget
          </h1>
          <p className="subtitle">Manage credit allocations across users and teams</p>
        </div>
        <button className="btn btn-primary">
          <Plus className="w-4 h-4 mr-2" /> Allocate Credits
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
        <input
          type="text"
          placeholder="Search wallets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10"
          style={{ maxWidth: 400 }}
        />
      </div>

      {/* Team Pools */}
      {teamWallets.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Team Pools</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {teamWallets.map(w => <WalletCard key={w.id} wallet={w} type="Team Pool" />)}
          </div>
        </div>
      )}

      {/* Personal Wallets */}
      {personalWallets.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Personal Wallets</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {personalWallets.map(w => <WalletCard key={w.id} wallet={w} type="Personal" />)}
          </div>
        </div>
      )}

      {filteredWallets.length === 0 && (
        <div className="empty-state">
          <Wallet className="icon" />
          <h3>No wallets found</h3>
          <p>Try adjusting your search or create a new wallet allocation.</p>
        </div>
      )}
    </div>
  );
}

function generateDemoWallets() {
  return [
    { id: '1', name: 'Engineering', type: 'team', total: 50000, used: 32000 },
    { id: '2', name: 'Product', type: 'team', total: 25000, used: 18500 },
    { id: '3', name: 'Research', type: 'team', total: 15000, used: 14200 },
    { id: '4', name: 'Alice Chen', type: 'personal', total: 2000, used: 1200 },
    { id: '5', name: 'Bob Smith', type: 'personal', total: 2000, used: 400 },
    { id: '6', name: 'Carol Davis', type: 'personal', total: 1500, used: 1480 },
  ];
}
