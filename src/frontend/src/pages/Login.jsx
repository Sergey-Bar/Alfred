/*
 * [AI GENERATED - GOVERNANCE PROTOCOL]
 * ──────────────────────────────────────────────────────────────
 * Model:       Claude Opus 4.6
 * Tier:        L2
 * Logic:       Split-panel auth page per UI.md §3.1.
 *              Left: SSO buttons, email/password form.
 *              Right: hero stats panel with rotating quotes.
 * Root Cause:  UI.md compliance — Login page redesign.
 * Context:     Uses CSS custom properties from design system.
 * Suitability: L2 — standard UI, no financial logic.
 * ──────────────────────────────────────────────────────────────
 */
import { ExternalLink, Eye, EyeOff, Loader2, Shield } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const TESTIMONIALS = [
    {
        quote: 'Reduced AI spend by 43% in the first month',
        author: 'Head of Platform',
        company: 'Series B SaaS',
    },
    {
        quote: 'Finally, one dashboard for all our LLM costs',
        author: 'VP Engineering',
        company: 'Fortune 500 FinTech',
    },
    {
        quote: 'The routing engine alone paid for itself in a week',
        author: 'CTO',
        company: 'AI-First Startup',
    },
];

const STATS = [
    { value: '$2.4M+', label: 'Governed' },
    { value: '10B+', label: 'Tokens' },
    { value: '30%', label: 'Avg Savings' },
];

export default function Login({ onLogin }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [authMode, setAuthMode] = useState('credentials'); // 'credentials' | 'apikey'
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [quoteIndex, setQuoteIndex] = useState(0);
    const navigate = useNavigate();

    // Rotate testimonials
    useEffect(() => {
        const timer = setInterval(() => {
            setQuoteIndex((prev) => (prev + 1) % TESTIMONIALS.length);
        }, 5000);
        return () => clearInterval(timer);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const key = authMode === 'apikey' ? apiKey : `${email}:${password}`;

        // DEMO MODE — only available in development builds
        if (import.meta.env.DEV && (key === 'tp-demo' || key === 'tp-demo-1234567890abcdef')) {
            api.setApiKey(key);
            localStorage.setItem('alfred_demo_mode', 'true');
            onLogin();
            navigate('/');
            setLoading(false);
            return;
        } else {
            localStorage.removeItem('alfred_demo_mode');
        }

        try {
            api.setApiKey(authMode === 'apikey' ? apiKey : key);
            await api.getOverview();
            onLogin();
            navigate('/');
        } catch {
            api.clearApiKey();
            setError(
                authMode === 'apikey'
                    ? 'Invalid API key. Please check and try again.'
                    : 'Invalid credentials. Please try again.'
            );
        } finally {
            setLoading(false);
        }
    };

    const handleSSO = (provider) => {
        // Placeholder for SSO redirect
        setError(`${provider} SSO is not configured yet.`);
    };

    const quote = TESTIMONIALS[quoteIndex];

    return (
        <div className="min-h-screen flex" style={{ fontFamily: 'var(--font-sans, Inter, system-ui, sans-serif)' }}>
            {/* --- Left Panel (form) --- */}
            <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 sm:px-16 lg:px-20 py-12"
                 style={{ background: 'var(--color-bg-primary, #0d1117)' }}>
                <div className="max-w-md w-full mx-auto">
                    {/* Logo */}
                    <div className="flex items-center gap-3 mb-10">
                        <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                             style={{ background: 'var(--color-primary, #6366f1)' }}>
                            <Shield className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-bold" style={{ color: 'var(--color-text-primary, #f0f6fc)' }}>
                            Alfred
                        </span>
                    </div>

                    <h1 className="text-2xl font-semibold mb-1" style={{ color: 'var(--color-text-primary, #f0f6fc)' }}>
                        Sign in to your organization
                    </h1>
                    <p className="text-sm mb-8" style={{ color: 'var(--color-text-tertiary, #8b949e)' }}>
                        The enterprise AI control plane
                    </p>

                    {/* SSO Buttons */}
                    <div className="space-y-3 mb-6">
                        {[
                            { name: 'Okta SSO', icon: <ExternalLink className="w-4 h-4" /> },
                            { name: 'Google', icon: <span className="text-sm font-bold">G</span> },
                            { name: 'Microsoft', icon: <span className="text-sm font-bold">⊞</span> },
                        ].map((sso) => (
                            <button
                                key={sso.name}
                                type="button"
                                onClick={() => handleSSO(sso.name)}
                                className="w-full flex items-center justify-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
                                style={{
                                    background: 'var(--color-bg-secondary, #161b22)',
                                    color: 'var(--color-text-primary, #f0f6fc)',
                                    border: '1px solid var(--color-border, #30363d)',
                                }}
                            >
                                {sso.icon}
                                Continue with {sso.name}
                            </button>
                        ))}
                    </div>

                    {/* Divider */}
                    <div className="relative flex items-center my-6">
                        <div className="flex-grow h-px" style={{ background: 'var(--color-border, #30363d)' }} />
                        <span className="px-3 text-xs" style={{ color: 'var(--color-text-tertiary, #8b949e)' }}>
                            or
                        </span>
                        <div className="flex-grow h-px" style={{ background: 'var(--color-border, #30363d)' }} />
                    </div>

                    {/* Auth mode toggle */}
                    <div className="flex gap-1 p-1 rounded-lg mb-6"
                         style={{ background: 'var(--color-bg-secondary, #161b22)' }}>
                        {[
                            { id: 'credentials', label: 'Email & Password' },
                            { id: 'apikey', label: 'API Key' },
                        ].map((mode) => (
                            <button
                                key={mode.id}
                                type="button"
                                onClick={() => { setAuthMode(mode.id); setError(''); }}
                                className="flex-1 py-1.5 rounded-md text-xs font-medium transition-colors"
                                style={{
                                    background: authMode === mode.id
                                        ? 'var(--color-bg-tertiary, #21262d)'
                                        : 'transparent',
                                    color: authMode === mode.id
                                        ? 'var(--color-text-primary, #f0f6fc)'
                                        : 'var(--color-text-tertiary, #8b949e)',
                                }}
                            >
                                {mode.label}
                            </button>
                        ))}
                    </div>

                    {/* Form */}
                    <form className="space-y-4" onSubmit={handleSubmit}>
                        {authMode === 'credentials' ? (
                            <>
                                <div>
                                    <label htmlFor="email" className="block text-xs font-medium mb-1.5"
                                           style={{ color: 'var(--color-text-secondary, #c9d1d9)' }}>
                                        Email address
                                    </label>
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        autoComplete="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors"
                                        style={{
                                            background: 'var(--color-bg-secondary, #161b22)',
                                            color: 'var(--color-text-primary, #f0f6fc)',
                                            border: '1px solid var(--color-border, #30363d)',
                                        }}
                                        placeholder="you@company.com"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="password" className="block text-xs font-medium mb-1.5"
                                           style={{ color: 'var(--color-text-secondary, #c9d1d9)' }}>
                                        Password
                                    </label>
                                    <div className="relative">
                                        <input
                                            id="password"
                                            name="password"
                                            type={showPassword ? 'text' : 'password'}
                                            autoComplete="current-password"
                                            required
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            className="w-full px-3 py-2.5 pr-10 rounded-lg text-sm outline-none transition-colors"
                                            style={{
                                                background: 'var(--color-bg-secondary, #161b22)',
                                                color: 'var(--color-text-primary, #f0f6fc)',
                                                border: '1px solid var(--color-border, #30363d)',
                                            }}
                                            placeholder="••••••••"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-3 top-1/2 -translate-y-1/2"
                                            style={{ color: 'var(--color-text-tertiary, #8b949e)' }}
                                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                                        >
                                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div>
                                <label htmlFor="api-key" className="block text-xs font-medium mb-1.5"
                                       style={{ color: 'var(--color-text-secondary, #c9d1d9)' }}>
                                    API Key
                                </label>
                                <input
                                    id="api-key"
                                    name="apiKey"
                                    type="password"
                                    autoComplete="off"
                                    required
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    className="w-full px-3 py-2.5 rounded-lg text-sm outline-none transition-colors"
                                    style={{
                                        background: 'var(--color-bg-secondary, #161b22)',
                                        color: 'var(--color-text-primary, #f0f6fc)',
                                        border: '1px solid var(--color-border, #30363d)',
                                    }}
                                    placeholder="tp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                />
                            </div>
                        )}

                        {/* Error */}
                        {error && (
                            <div className="rounded-lg px-3 py-2.5 text-sm"
                                 style={{
                                     background: 'rgba(248, 81, 73, 0.1)',
                                     color: 'var(--color-danger, #f85149)',
                                     border: '1px solid rgba(248, 81, 73, 0.4)',
                                 }}>
                                {error}
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            style={{
                                background: 'var(--color-primary, #6366f1)',
                                color: '#ffffff',
                            }}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Verifying...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    {/* Footer links */}
                    <div className="flex items-center justify-center gap-2 mt-6 text-xs"
                         style={{ color: 'var(--color-text-tertiary, #8b949e)' }}>
                        <button type="button" className="hover:underline">Forgot password?</button>
                        <span>·</span>
                        <button type="button" className="hover:underline">Sign up</button>
                    </div>
                </div>
            </div>

            {/* --- Right Panel (hero stats) --- */}
            <div className="hidden lg:flex w-1/2 flex-col justify-center items-center px-16 py-12 relative overflow-hidden"
                 style={{ background: 'var(--color-primary-800, #1e1b4b)' }}>
                {/* Abstract background pattern */}
                <div className="absolute inset-0 opacity-10"
                     style={{
                         backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(99,102,241,0.3) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(139,92,246,0.3) 0%, transparent 50%)',
                     }}
                />

                <div className="relative z-10 max-w-lg text-center">
                    {/* Rotating quote */}
                    <div className="mb-12" style={{ minHeight: '120px' }}>
                        <p className="text-2xl font-semibold text-white leading-relaxed mb-4"
                           key={quoteIndex}>
                            &ldquo;{quote.quote}&rdquo;
                        </p>
                        <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                            — {quote.author}, {quote.company}
                        </p>
                    </div>

                    {/* Stats row */}
                    <div className="flex justify-center gap-6">
                        {STATS.map((stat) => (
                            <div key={stat.label}
                                 className="px-6 py-4 rounded-xl"
                                 style={{
                                     background: 'rgba(255,255,255,0.08)',
                                     backdropFilter: 'blur(8px)',
                                     border: '1px solid rgba(255,255,255,0.1)',
                                 }}>
                                <div className="text-2xl font-bold text-white">{stat.value}</div>
                                <div className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    {stat.label}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
