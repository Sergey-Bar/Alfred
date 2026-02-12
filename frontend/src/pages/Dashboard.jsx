import { useState, useEffect } from 'react';
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import {
    CurrencyDollarIcon,
    UsersIcon,
    ChartBarIcon,
    ArrowTrendingUpIcon,
    ClockIcon,
    CheckCircleIcon,
} from '@heroicons/react/24/outline';
import api from '../services/api';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

function StatCard({ title, value, icon: Icon, color = 'blue', trend }) {
    const colorClasses = {
        blue: 'bg-blue-100 text-blue-600',
        green: 'bg-green-100 text-green-600',
        yellow: 'bg-yellow-100 text-yellow-600',
        red: 'bg-red-100 text-red-600',
        purple: 'bg-purple-100 text-purple-600',
    };

    return (
        <div className="stat-card">
            <div className="flex items-center justify-between">
                <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
                    <Icon className="h-6 w-6" />
                </div>
                {trend && (
                    <span className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trend > 0 ? '+' : ''}{trend}%
                    </span>
                )}
            </div>
            <div className="mt-4">
                <p className="stat-value">{value}</p>
                <p className="stat-label">{title}</p>
            </div>
        </div>
    );
}

export default function Dashboard() {
    const [overview, setOverview] = useState(null);
    const [trends, setTrends] = useState([]);
    const [models, setModels] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);
    const [approvals, setApprovals] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                const [overviewData, trendsData, modelsData, leaderboardData, approvalsData] =
                    await Promise.all([
                        api.getOverview(),
                        api.getCostTrends(30),
                        api.getModelUsage(),
                        api.getLeaderboard(10),
                        api.getApprovalStats(),
                    ]);

                setOverview(overviewData);
                setTrends(trendsData);
                setModels(modelsData);
                setLeaderboard(leaderboardData);
                setApprovals(approvalsData);
            } catch (err) {
                setError(err.message);
                // Use mock data for demo
                setOverview({
                    total_users: 25,
                    total_teams: 5,
                    total_tokens_used: 150000,
                    total_cost: 1250.50,
                    active_users_today: 18,
                    pending_approvals: 3,
                });
                setTrends([
                    { date: '2024-01-01', total_tokens: 5000, total_cost: 42.50 },
                    { date: '2024-01-02', total_tokens: 7500, total_cost: 63.75 },
                    { date: '2024-01-03', total_tokens: 6200, total_cost: 52.70 },
                    { date: '2024-01-04', total_tokens: 8100, total_cost: 68.85 },
                    { date: '2024-01-05', total_tokens: 9500, total_cost: 80.75 },
                ]);
                setModels([
                    { model: 'gpt-4', request_count: 450, total_tokens: 90000, total_cost: 720 },
                    { model: 'gpt-3.5-turbo', request_count: 1200, total_tokens: 45000, total_cost: 67.50 },
                    { model: 'claude-3-opus', request_count: 200, total_tokens: 40000, total_cost: 480 },
                ]);
                setLeaderboard([
                    { user_id: '1', user_name: 'Alice Johnson', user_email: 'alice@example.com', efficiency_score: 0.95 },
                    { user_id: '2', user_name: 'Bob Smith', user_email: 'bob@example.com', efficiency_score: 0.88 },
                    { user_id: '3', user_name: 'Carol Williams', user_email: 'carol@example.com', efficiency_score: 0.82 },
                ]);
                setApprovals({
                    total_pending: 3,
                    total_approved: 45,
                    total_denied: 8,
                    avg_approval_time_hours: 2.5,
                });
            } finally {
                setLoading(false);
            }
        }

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-500 mt-1">Overview of your Alfred token usage and quotas</p>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-yellow-50 text-yellow-700 rounded-lg text-sm">
                    Using demo data - API connection failed: {error}
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Total Users"
                    value={overview?.total_users || 0}
                    icon={UsersIcon}
                    color="blue"
                />
                <StatCard
                    title="Tokens Used"
                    value={(overview?.total_tokens_used || 0).toLocaleString()}
                    icon={ChartBarIcon}
                    color="green"
                />
                <StatCard
                    title="Total Cost"
                    value={`$${(overview?.total_cost || 0).toFixed(2)}`}
                    icon={CurrencyDollarIcon}
                    color="yellow"
                />
                <StatCard
                    title="Pending Approvals"
                    value={overview?.pending_approvals || 0}
                    icon={ClockIcon}
                    color="purple"
                />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Usage Trends */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Token Usage Trend</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={trends}>
                            <defs>
                                <linearGradient id="colorTokens" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                            <YAxis tick={{ fontSize: 12 }} />
                            <Tooltip />
                            <Area
                                type="monotone"
                                dataKey="total_tokens"
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
                    <h3 className="text-lg font-semibold mb-4">Cost Trend</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={trends}>
                            <defs>
                                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
                            <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                            <Area
                                type="monotone"
                                dataKey="total_cost"
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
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Model Usage */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Model Usage</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={models}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="request_count"
                                nameKey="model"
                                label={({ model }) => model}
                            >
                                {models.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Leaderboard */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Efficiency Leaderboard</h3>
                    <div className="space-y-3">
                        {leaderboard.slice(0, 5).map((user, index) => (
                            <div key={user.user_id} className="flex items-center">
                                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-3 ${index === 0 ? 'bg-yellow-100 text-yellow-700' :
                                    index === 1 ? 'bg-gray-100 text-gray-700' :
                                        index === 2 ? 'bg-orange-100 text-orange-700' :
                                            'bg-gray-50 text-gray-500'
                                    }`}>
                                    {index + 1}
                                </span>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900">{user.user_name}</p>
                                    <p className="text-xs text-gray-500">{user.user_email}</p>
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
                    <h3 className="text-lg font-semibold mb-4">Approval Statistics</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <ClockIcon className="h-5 w-5 text-yellow-500 mr-2" />
                                <span className="text-sm text-gray-600">Pending</span>
                            </div>
                            <span className="text-lg font-semibold">{approvals?.total_pending || 0}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                                <span className="text-sm text-gray-600">Approved</span>
                            </div>
                            <span className="text-lg font-semibold">{approvals?.total_approved || 0}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center">
                                <span className="h-5 w-5 flex items-center justify-center text-red-500 mr-2">✕</span>
                                <span className="text-sm text-gray-600">Denied</span>
                            </div>
                            <span className="text-lg font-semibold">{approvals?.total_denied || 0}</span>
                        </div>
                        <div className="pt-3 border-t">
                            <p className="text-sm text-gray-500">
                                Avg. approval time: <span className="font-semibold">{approvals?.avg_approval_time_hours?.toFixed(1) || 0}h</span>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
