import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function Login({ onLogin }) {
    const [apiKey, setApiKey] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // DEMO MODE: Accept 'tp-demo' or 'tp-demo-1234567890abcdef' as a valid key
        if (apiKey === 'tp-demo' || apiKey === 'tp-demo-1234567890abcdef') {
            api.setApiKey(apiKey);
            // Optionally: set a flag in localStorage for demo mode
            localStorage.setItem('alfred_demo_mode', 'true');
            onLogin();
            navigate('/');
            setLoading(false);
            return;
        } else {
            localStorage.removeItem('alfred_demo_mode');
        }

        try {
            // Save API key and try to fetch dashboard to validate
            api.setApiKey(apiKey);
            await api.getOverview();
            onLogin();
            navigate('/');
        } catch (err) {
            api.clearApiKey();
            setError('Invalid API key. Please check and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (

        <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-[#1d3557] to-[#0f1f38] py-0 px-0">
            {/* Full-size Logo, no frame, no text */}
            <img
                src="/sidebar-big.png"
                alt="Alfred Logo"
                style={{ width: '100%', maxWidth: '30%', height: 'auto', display: 'block', objectFit: 'contain', margin: '0 auto 2.5rem auto', padding: 0 }}
            />

            {/* Login Card */}
                        <div className="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 mt-0">
                <div className="text-center mb-6">
                    <h2 className="text-xl font-semibold" style={{ color: '#1d3557', textAlign: 'center' }}>
                        Sign in to your account
                    </h2>
                    <p className="mt-1 text-sm text-gray-500" style={{ textAlign: 'center' }}>
                        Enter your API key to access the dashboard
                    </p>
                </div>

                <form className="space-y-5" onSubmit={handleSubmit}>
                    <div className="text-center">
                        <input
                            id="api-key"
                            name="apiKey"
                            type="password"
                            autoComplete="off"
                            required
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="appearance-none rounded-lg relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#1d3557] focus:border-[#1d3557] sm:text-sm"
                            placeholder="tp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                            style={{ marginTop: 0 }}
                        />
                    </div>

                    {error && (
                        <div className="rounded-md bg-red-50 p-4">
                            <div className="flex">
                                <div className="flex-shrink-0">
                                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                    </svg>
                                </div>
                                <div className="ml-3">
                                    <p className="text-sm font-medium text-red-800">{error}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-[#1d3557] hover:bg-[#2d4a6f] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1d3557] disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <span className="flex items-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Verifying...
                                </span>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </div>
                </form>

                <div className="mt-6">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-200"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-white text-gray-400">
                                Powered by Alfred
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
