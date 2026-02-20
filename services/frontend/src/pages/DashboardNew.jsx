import {
    ArrowRight,
    BarChart3,
    CheckCircle2,
    Clock,
    DollarSign,
    TrendingUp,
    Users,
    XCircle,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Area,
    AreaChart,
    CartesianGrid,
    Cell,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis, YAxis
} from 'recharts';
import DateRangePicker from '../components/DateRangePicker';
import SpendTicker from '../components/SpendTicker';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

// Interactive Stat Card with click navigation
function StatCard({ title, value, icon: Icon, color = 'blue', trend, onClick, subtitle, clickable = true }) {
    const colorClasses = {
        blue: 'bg-blue-900/50 text-blue-400',
        green: 'bg-green-900/50 text-green-400',
        yellow: 'bg-yellow-900/50 text-yellow-400',
        red: 'bg-red-900/50 text-red-400',
        purple: 'bg-purple-900/50 text-purple-400',
    };

    const hoverClasses = clickable
        ? 'cursor-pointer hover:shadow-lg hover:scale-[1.02] hover:border-blue-500'
        : '';

    return (
        <div
            onClick={clickable ? onClick : undefined}
            className={`stat-card transition-all duration-200 border-2 border-transparent ${hoverClasses} group`}
        >
            <div className="flex items-center justify-between">
                <div className={`p-2 rounded-lg ${colorClasses[color]} transition-transform group-hover:scale-110`}>
                    <Icon className="h-6 w-6" />
                </div>
                <div className="flex items-center space-x-2">
                    {trend !== undefined && (
                        <span className={`text-sm font-medium ${trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                            {trend > 0 ? '+' : ''}{trend}%
                        </span>
                    )}
                    {clickable && (
                        <ArrowRight className="h-4 w-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    )}
                </div>
            </div>
            <div className="mt-4">
                <p className="stat-value">{value}</p>
                <p className="stat-label">{title}</p>
                {subtitle && (
                    <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
                )}
            </div>
        </div>
    );
}

// Quick Action Button
function QuickAction({ icon: Icon, label, onClick, color = 'blue' }) {
    const colorClasses = {
        blue: 'bg-blue-900/40 text-blue-300 hover:bg-blue-900/60 border border-blue-800',
        green: 'bg-green-900/40 text-green-300 hover:bg-green-900/60 border border-green-800',
        purple: 'bg-purple-900/40 text-purple-300 hover:bg-purple-900/60 border border-purple-800',
    };

    return (
        <button
            onClick={onClick}
            className={`flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm ${colorClasses[color]}`}
        >
            <Icon className="h-4 w-4 mr-2" />
            {label}
        </button>
    );
}

// Format date as DD.MM for chart display
function formatDateShort(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    return `${day}.${month}`;
}

// Format date as DD.MM.YYYY for full display
function formatDateFull(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
}

export default function Dashboard() {
    const navigate = useNavigate();
    const { darkMode } = useTheme();
    const [overview, setOverview] = useState(null);
    const [trends, setTrends] = useState([]);
    const [models, setModels] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);
    const [approvals, setApprovals] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [dateRange, setDateRange] = useState({ range: 'year', year: new Date().getFullYear() });

    // Calculate trends
    const usersTrend = overview?.users_trend || 0;
    const tokensTrend = overview?.tokens_trend || 0;
    const costTrend = overview?.cost_trend || 0;

    // StatCard drag-and-drop state
    const initialCards = [
        {
            id: 'users',
            title: 'Total Users',
            value: overview?.total_users || 0,
            icon: Users,
            color: 'blue',
            trend: usersTrend,
            subtitle: 'Click to manage users',
            onClick: () => navigate('/users'),
        },
        {
            id: 'tokens',
            title: 'Tokens Used',
            value: (overview?.total_tokens_used || 0).toLocaleString(),
            icon: BarChart3,
            color: 'green',
            trend: tokensTrend,
            subtitle: 'Click for detailed breakdown',
            onClick: () => navigate('/transfers'),
        },
        {
            id: 'cost',
            title: 'Total Cost',
            value: `$${(overview?.total_credits_spent || 0).toFixed(2)}`,
            icon: DollarSign,
            color: 'yellow',
            trend: costTrend,
            subtitle: 'Click for cost analysis',
            onClick: () => navigate('/transfers'),
        },
        {
            id: 'teams',
            title: 'Active Teams',
            value: overview?.total_teams || 0,
            icon: Users,
            color: 'purple',
            subtitle: 'Click to manage teams',
            onClick: () => navigate('/teams'),
        },
    ];

    const [cards, setCards] = useState(initialCards);

    useEffect(() => {
        setCards(initialCards);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [overview]);

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [dateRange]);

    async function fetchData() {
        try {
            setLoading(true);
            const days = dateRange.range === '7d' ? 7 : dateRange.range === '30d' ? 30 : 365;

            const [overviewRes, trendsRes, modelsRes, leaderboardRes, approvalsRes] = await Promise.all([
                api.getOverview().catch((err) => { console.error('getOverview failed:', err); throw err; }),
                api.getCostTrends(days).catch((err) => { console.error('getCostTrends failed:', err); throw err; }),
                api.getModelUsage().catch((err) => { console.error('getModelUsage failed:', err); throw err; }),
                api.getLeaderboard(10).catch((err) => { console.error('getLeaderboard failed:', err); throw err; }),
                api.getApprovalStats().catch((err) => { console.error('getApprovalStats failed:', err); throw err; }),
            ]);

            setOverview(overviewRes);
            setTrends(
                (trendsRes || []).map((t) => ({
                    ...t,
                    displayDate: formatDateShort(t.date),
                    fullDate: formatDateFull(t.date),
                }))
            );
            setModels(modelsRes || []);
            setLeaderboard(leaderboardRes || []);
            setApprovals(approvalsRes);
        } catch (err) {
            console.error('fetchData error:', err);
            setError(err);
        } finally {
            setLoading(false);
        }
    }

    // Drag-and-drop removed due to React 19 incompatibility with react-beautiful-dnd
    // Future: implement with @dnd-kit/core when upgrading

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center text-red-500 p-8">
                <p>Error loading dashboard: {error.message}</p>
                <button
                    onClick={fetchData}
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header with Quick Actions */}
            <div className="flex flex-wrap items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                <div className="flex flex-wrap items-center gap-3">
                    <DateRangePicker value={dateRange} onChange={setDateRange} />
                    <QuickAction
                        icon={Users}
                        label="Add User"
                        onClick={() => navigate('/users')}
                        color="blue"
                    />
                    <QuickAction
                        icon={Users}
                        label="Create Team"
                        onClick={() => navigate('/teams')}
                        color="green"
                    />
                    <QuickAction
                        icon={TrendingUp}
                        label="View Reports"
                        onClick={() => navigate('/transfers')}
                        color="purple"
                    />
                </div>
            </div>

            {/* Interactive Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                {cards.map((card) => (
                    <StatCard key={card.id} {...card} />
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
                {/* Spend Ticker */}
                <SpendTicker />

                {/* Usage Trends */}
                <div className="card lg:col-span-2">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Token Usage Trend</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={trends}>
                            <defs>
                                <linearGradient id="colorTokens" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#374151' : '#f0f0f0'} />
                            <XAxis
                                dataKey="displayDate"
                                tick={{ fontSize: 12, fill: darkMode ? '#9CA3AF' : '#6B7280' }}
                            />
                            <YAxis tick={{ fontSize: 12, fill: darkMode ? '#9CA3AF' : '#6B7280' }} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: darkMode ? '#1F2937' : '#ffffff',
                                    border: `1px solid ${darkMode ? '#374151' : '#E5E7EB'}`,
                                    borderRadius: '8px',
                                    color: darkMode ? '#F3F4F6' : '#111827',
                                }}
                                labelStyle={{ color: darkMode ? '#F3F4F6' : '#111827', fontWeight: 600 }}
                                itemStyle={{ color: darkMode ? '#9CA3AF' : '#4B5563' }}
                                formatter={(value) => [value.toLocaleString(), 'Tokens']}
                                labelFormatter={(label, payload) => {
                                    if (payload?.[0]?.payload?.fullDate) {
                                        return payload[0].payload.fullDate;
                                    }
                                    return label;
                                }}
                            />
                            <Area
                                type="monotone"
                                dataKey="tokens"
                                stroke="#3B82F6"
                                fillOpacity={1}
                                fill="url(#colorTokens)"
                                name="Tokens"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Cost Trends */}
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Cost Trend</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={trends}>
                            <defs>
                                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#374151' : '#f0f0f0'} />
                            <XAxis
                                dataKey="displayDate"
                                tick={{ fontSize: 12, fill: darkMode ? '#9CA3AF' : '#6B7280' }}
                            />
                            <YAxis
                                tick={{ fontSize: 12, fill: darkMode ? '#9CA3AF' : '#6B7280' }}
                                tickFormatter={(v) => `$${v}`}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: darkMode ? '#1F2937' : '#ffffff',
                                    border: `1px solid ${darkMode ? '#374151' : '#E5E7EB'}`,
                                    borderRadius: '8px',
                                    color: darkMode ? '#F3F4F6' : '#111827',
                                }}
                                labelStyle={{ color: darkMode ? '#F3F4F6' : '#111827', fontWeight: 600 }}
                                itemStyle={{ color: darkMode ? '#9CA3AF' : '#4B5563' }}
                                formatter={(value) => [`$${value.toFixed(2)}`, 'Cost']}
                                labelFormatter={(label, payload) => {
                                    if (payload?.[0]?.payload?.fullDate) {
                                        return payload[0].payload.fullDate;
                                    }
                                    return label;
                                }}
                            />
                            <Area
                                type="monotone"
                                dataKey="cost"
                                stroke="#10B981"
                                fillOpacity={1}
                                fill="url(#colorCost)"
                                name="Cost"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
                {/* Model Usage */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4">Model Usage</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={models}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="requests"
                                nameKey="model"
                                label={({ model }) => model}
                            >
                                {models.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: darkMode ? '#1F2937' : '#ffffff',
                                    border: `1px solid ${darkMode ? '#374151' : '#E5E7EB'}`,
                                    borderRadius: '8px',
                                    color: darkMode ? '#F3F4F6' : '#111827',
                                }}
                                labelStyle={{ color: darkMode ? '#F3F4F6' : '#111827', fontWeight: 600 }}
                                itemStyle={{ color: darkMode ? '#9CA3AF' : '#4B5563' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Leaderboard - Clickable */}
                <div className="card">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-white">Efficiency Leaderboard</h3>
                        <button
                            onClick={() => navigate('/users')}
                            className="text-xs text-blue-400 hover:underline"
                        >
                            View all
                        </button>
                    </div>
                    <div className="space-y-3">
                        {leaderboard.slice(0, 5).map((user, index) => (
                            <div
                                key={user.user_id}
                                className="flex items-center p-2 rounded-lg hover:bg-gray-700 cursor-pointer transition-colors"
                                onClick={() => navigate('/users')}
                            >
                                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-3 ${index === 0 ? 'bg-yellow-900/50 text-yellow-400' :
                                    index === 1 ? 'bg-gray-600 text-gray-200' :
                                        index === 2 ? 'bg-orange-900/50 text-orange-400' :
                                            'bg-gray-700 text-gray-400'
                                    }`}>
                                    {index + 1}
                                </span>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-white truncate">{user.name}</p>
                                </div>
                                <span className="text-sm font-semibold text-green-600">
                                    {(user.efficiency_score * 100).toFixed(0)}%
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Approval Stats */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-white mb-4">Approval Statistics</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-700 transition-colors">
                            <div className="flex items-center">
                                <Clock className="h-5 w-5 text-yellow-500 mr-2" />
                                <span className="text-sm text-gray-300">Pending</span>
                            </div>
                            <span className="text-lg font-semibold text-white">{approvals?.total_pending || 0}</span>
                        </div>
                        <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-700 transition-colors">
                            <div className="flex items-center">
                                <CheckCircle2 className="h-5 w-5 text-green-500 mr-2" />
                                <span className="text-sm text-gray-300">Approved (7d)</span>
                            </div>
                            <span className="text-lg font-semibold text-white">{approvals?.total_approved_7d || 0}</span>
                        </div>
                        <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-700 transition-colors">
                            <div className="flex items-center">
                                <XCircle className="h-5 w-5 text-red-500 mr-2" />
                                <span className="text-sm text-gray-300">Denied (7d)</span>
                            </div>
                            <span className="text-lg font-semibold text-white">{approvals?.total_rejected_7d || 0}</span>
                        </div>
                        <div className="pt-3 border-t border-gray-700">
                            <p className="text-sm text-gray-400">
                                Avg. approval time: <span className="font-semibold text-white">{approvals?.avg_approval_time_hours?.toFixed(1) || 0}h</span>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
