import { Activity, AlertTriangle, Settings, Shield, TrendingDown, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';

/**
 * Safety Dashboard Component
 * 
 * Displays:
 * - Safety violation statistics (today, week, month)
 * - Breakdown by category (PII, secrets, injection)
 * - Trends and patterns
 * - Recent incidents
 * - Policy configuration
 */
export const SafetyDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d'); // 1d, 7d, 30d
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchSafetyStats();
  }, [timeRange, selectedCategory]);

  const fetchSafetyStats = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/v1/safety/stats?range=${timeRange}&category=${selectedCategory}`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch safety stats:', error);
      // Mock data for demonstration
      setStats({
        totalIncidents: 247,
        blockedRequests: 189,
        redactedRequests: 34,
        warnedRequests: 24,
        trend: 12, // percentage change
        byCategory: {
          pii: { count: 156, trend: 8 },
          secret: { count: 58, trend: -15 },
          injection: { count: 28, trend: 45 },
          blocklist: { count: 5, trend: 0 }
        },
        bySeverity: {
          critical: 42,
          high: 98,
          medium: 67,
          low: 40
        },
        recentIncidents: [
          {
            id: '1',
            timestamp: '2026-02-16T10:30:00Z',
            userId: 'user_123',
            category: 'pii',
            type: 'ssn',
            severity: 'high',
            action: 'blocked'
          },
          {
            id: '2',
            timestamp: '2026-02-16T09:15:00Z',
            userId: 'user_456',
            category: 'secret',
            type: 'openai_api_key',
            severity: 'critical',
            action: 'blocked'
          },
          {
            id: '3',
            timestamp: '2026-02-16T08:45:00Z',
            userId: 'user_789',
            category: 'injection',
            type: 'ignore_instructions',
            severity: 'high',
            action: 'blocked'
          }
        ],
        topUsers: [
          { userId: 'user_123', userName: 'Alice Chen', incidents: 12 },
          { userId: 'user_456', userName: 'Bob Smith', incidents: 8 },
          { userId: 'user_789', userName: 'Carol Lee', incidents: 6 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'pii': return 'text-purple-600 bg-purple-100';
      case 'secret': return 'text-red-600 bg-red-100';
      case 'injection': return 'text-orange-600 bg-orange-100';
      case 'blocklist': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Shield className="w-8 h-8 text-blue-600" />
              Safety Dashboard
            </h1>
            <p className="text-gray-600 mt-2">
              Monitor safety violations and enforce security policies
            </p>
          </div>
          <div className="flex gap-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
            </select>
            <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Settings className="w-4 h-4" />
              Configure Policies
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            {stats?.trend !== undefined && (
              <div className={`flex items-center gap-1 text-sm font-medium ${stats.trend >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                {stats.trend >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                {Math.abs(stats.trend)}%
              </div>
            )}
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats?.totalIncidents || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Total Incidents</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats?.blockedRequests || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Blocked Requests</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats?.redactedRequests || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Auto-Redacted</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats?.warnedRequests || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Warnings</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* By Category */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Violations by Category</h2>
          <div className="space-y-3">
            {Object.entries(stats?.byCategory || {}).map(([category, data]) => (
              <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getCategoryColor(category)}`}>
                    {category.toUpperCase()}
                  </span>
                  <span className="text-sm font-medium text-gray-900">{data.count}</span>
                </div>
                {data.trend !== 0 && (
                  <div className={`flex items-center gap-1 text-xs font-medium ${data.trend > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {data.trend > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {Math.abs(data.trend)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* By Severity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Violations by Severity</h2>
          <div className="space-y-3">
            {Object.entries(stats?.bySeverity || {}).map(([severity, count]) => (
              <div key={severity} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(severity)}`}>
                    {severity.toUpperCase()}
                  </span>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${severity === 'critical' ? 'bg-red-600' : severity === 'high' ? 'bg-orange-600' : severity === 'medium' ? 'bg-yellow-600' : 'bg-blue-600'}`}
                    style={{ width: `${(count / stats.totalIncidents) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Incidents */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Incidents</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats?.recentIncidents?.map((incident) => (
                <tr key={incident.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {formatTimestamp(incident.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {incident.userId}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getCategoryColor(incident.category)}`}>
                      {incident.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {incident.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(incident.severity)}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">
                    {incident.action}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top Users with Violations */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Users with Most Violations</h2>
        </div>
        <div className="p-6">
          <div className="space-y-3">
            {stats?.topUsers?.map((user, index) => (
              <div key={user.userId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-bold">
                    {index + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-900">{user.userName}</span>
                  <span className="text-xs text-gray-500">({user.userId})</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{user.incidents} incidents</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SafetyDashboard;
