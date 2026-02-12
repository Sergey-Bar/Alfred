import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import api from '../services/api';

const INTEGRATION_META = {
    slack: { icon: '💬', description: 'Slack Webhooks' },
    teams: { icon: '👥', description: 'Microsoft Teams Webhooks' },
    telegram: { icon: '✈️', description: 'Telegram Bot' },
    whatsapp: { icon: '📱', description: 'WhatsApp Business API' },
};

export default function Integrations() {
    const [integrations, setIntegrations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getIntegrationsConfig()
            .then(data => {
                setIntegrations(data || []);
            })
            .catch(err => console.error("Failed to load integrations", err))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Integrations</h1>
                <p className="text-gray-400 mt-1">
                    System-wide integration status configured via server environment variables.
                </p>
            </div>

            <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 overflow-hidden">
                <div className="grid divide-y divide-gray-700">
                    {loading ? (
                        <div className="p-8 text-center text-gray-400">Loading configurations...</div>
                    ) : integrations.length === 0 ? (
                        <div className="p-8 text-center text-gray-400">
                            No integrations returned from server.
                        </div>
                    ) : (
                        integrations.map((config) => {
                            const meta = INTEGRATION_META[config.id] || { icon: '🔌', description: config.name };
                            return (
                                <div key={config.id} className="p-6 flex items-center justify-between hover:bg-gray-750 transition-colors">
                                    <div className="flex items-center space-x-4">
                                        <div className="text-3xl bg-gray-700 p-2 rounded-lg">
                                            {meta.icon}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-medium text-white">{config.name}</h3>
                                            <p className="text-sm text-gray-400">{meta.description}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center">
                                        {config.enabled ? (
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-900/30 text-green-400 border border-green-900/50">
                                                <CheckCircleIcon className="h-5 w-5 mr-1.5" />
                                                Active
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-700 text-gray-400 border border-gray-600">
                                                <XCircleIcon className="h-5 w-5 mr-1.5" />
                                                Not Configured
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </div>

            <div className="bg-blue-900/20 border border-blue-900/50 rounded-lg p-4">
                <div className="flex">
                    <div className="flex-shrink-0">
                        <span className="text-blue-400">ℹ️</span>
                    </div>
                    <div className="ml-3">
                        <h3 className="text-sm font-medium text-blue-400">Configuration Guide</h3>
                        <div className="mt-2 text-sm text-blue-300/80">
                            <p>
                                Integrations are managed by the server administrator for security.
                                To enable a new integration, update the <code>.env</code> file on the server with the required credits (e.g., <code>SLACK_WEBHOOK_URL</code>).
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
