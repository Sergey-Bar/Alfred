
/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Main dashboard layout per UI.md Section 2. Restructured
             sidebar with navigation groups (OVERVIEW, CONTROL,
             SECURITY, PRODUCT, ADMIN). Migrated from Heroicons to
             Lucide React. Updated color palette to CSS custom properties.
Root Cause:  Sidebar used old nav structure and Heroicons, misaligned
             with UI.md spec.
Context:     All dashboard pages render inside this layout. Sidebar
             bg: --color-primary-800 (#1E293B). Active state uses
             left border with --color-accent-500.
Suitability: L3 for layout restructuring with nav group logic.
──────────────────────────────────────────────────────────────
*/
import {
    ArrowRightLeft, Bell, BookOpen, ChevronDown, ChevronLeft,
    ChevronRight, ClipboardCheck, FlaskConical, GitBranch, Key,
    LayoutDashboard, Link as LinkIcon, LogOut, Menu, Plug,
    ScrollText, Search, Settings, ShieldCheck, TrendingUp,
    User, Users, Wallet, X
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

const navigationGroups = [
    {
        label: 'OVERVIEW',
        items: [
            { name: 'Dashboard', href: '/', icon: LayoutDashboard },
            { name: 'Cost Analytics', href: '/analytics/cost', icon: TrendingUp },
        ],
    },
    {
        label: 'CONTROL',
        items: [
            { name: 'Wallets & Budget', href: '/wallets', icon: Wallet },
            { name: 'Routing Rules', href: '/routing', icon: GitBranch },
            { name: 'Experiments', href: '/experiments', icon: FlaskConical },
            { name: 'Credit Reallocation', href: '/transfers', icon: ArrowRightLeft },
            { name: 'Approvals', href: '/approvals', icon: ClipboardCheck },
        ],
    },
    {
        label: 'SECURITY',
        items: [
            { name: 'Security & Policies', href: '/security', icon: ShieldCheck },
            { name: 'Audit Log', href: '/audit', icon: ScrollText },
            { name: 'Safety Pipeline', href: '/safety', icon: ShieldCheck },
        ],
    },
    {
        label: 'PRODUCT',
        items: [
            { name: 'Providers', href: '/providers', icon: Plug },
            { name: 'Integrations', href: '/integrations', icon: LinkIcon },
        ],
    },
    {
        label: 'ADMIN',
        items: [
            { name: 'Team Management', href: '/teams', icon: Users },
            { name: 'Manage Users', href: '/users', icon: Users },
            { name: 'API Keys', href: '/keys', icon: Key },
        ],
    },
];

const bottomNavigation = [
    { name: 'User Guide', href: '/guide', icon: BookOpen },
    { name: 'Settings', href: '/settings', icon: Settings },
];

const getBreadcrumbs = (pathname) => {
    const paths = {
        '/': [{ name: 'Dashboard', current: true }],
        '/analytics/cost': [{ name: 'Dashboard', href: '/' }, { name: 'Cost Analytics', current: true }],
        '/wallets': [{ name: 'Dashboard', href: '/' }, { name: 'Wallets & Budget', current: true }],
        '/routing': [{ name: 'Dashboard', href: '/' }, { name: 'Routing Rules', current: true }],
        '/experiments': [{ name: 'Dashboard', href: '/' }, { name: 'Experiments', current: true }],
        '/transfers': [{ name: 'Dashboard', href: '/' }, { name: 'Credit Reallocation', current: true }],
        '/approvals': [{ name: 'Dashboard', href: '/' }, { name: 'Approvals', current: true }],
        '/security': [{ name: 'Dashboard', href: '/' }, { name: 'Security & Policies', current: true }],
        '/audit': [{ name: 'Dashboard', href: '/' }, { name: 'Audit Log', current: true }],
        '/safety': [{ name: 'Dashboard', href: '/' }, { name: 'Safety Pipeline', current: true }],
        '/providers': [{ name: 'Dashboard', href: '/' }, { name: 'Providers', current: true }],
        '/integrations': [{ name: 'Dashboard', href: '/' }, { name: 'Integrations', current: true }],
        '/teams': [{ name: 'Dashboard', href: '/' }, { name: 'Team Management', current: true }],
        '/users': [{ name: 'Dashboard', href: '/' }, { name: 'Manage Users', current: true }],
        '/keys': [{ name: 'Dashboard', href: '/' }, { name: 'API Keys', current: true }],
        '/guide': [{ name: 'Dashboard', href: '/' }, { name: 'User Guide', current: true }],
        '/profile': [{ name: 'Dashboard', href: '/' }, { name: 'My Profile', current: true }],
        '/settings': [{ name: 'Dashboard', href: '/' }, { name: 'Settings', current: true }],
    };
    return paths[pathname] || [{ name: 'Dashboard', current: true }];
};

function NavTooltip({ children, text, show }) {
    if (!show) return children;

    return (
        <div className="relative group">
            {children}
            <div className="absolute left-full ml-2 top-1/2 -translate-y-1/2 px-2 py-1 text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50"
                style={{ background: 'var(--color-primary-900)', color: 'white' }}>
                {text}
                <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent"
                    style={{ borderRightColor: 'var(--color-primary-900)' }} />
            </div>
        </div>
    );
}

function UserMenu({ user, onLogout, onNavigateProfile }) {
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div className="relative" ref={menuRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors"
                style={{ color: 'var(--color-primary-700)' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--color-primary-100)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
                <div className="h-8 w-8 rounded-full flex items-center justify-center text-sm font-bold text-white"
                    style={{ background: 'var(--color-accent-600)' }}>
                    {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="text-left hidden md:block">
                    <p className="text-sm font-medium" style={{ color: 'var(--color-primary-900)' }}>
                        {user?.name || 'User'}
                    </p>
                    <p className="text-xs" style={{ color: 'var(--color-primary-500)' }}>
                        {user?.role || 'Member'}
                    </p>
                </div>
                <ChevronDown className={`h-4 w-4 transition-transform hidden md:block ${isOpen ? 'rotate-180' : ''}`}
                    style={{ color: 'var(--color-primary-400)' }} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded-lg py-1 z-50 animate-scale-in"
                    style={{
                        background: 'white',
                        boxShadow: 'var(--shadow-lg)',
                        border: '1px solid var(--color-border)'
                    }}>
                    <div className="px-4 py-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
                        <p className="text-sm font-medium" style={{ color: 'var(--color-primary-900)' }}>{user?.name}</p>
                        <p className="text-xs truncate" style={{ color: 'var(--color-primary-500)' }}>{user?.email}</p>
                    </div>

                    <button
                        onClick={() => { onNavigateProfile(); setIsOpen(false); }}
                        className="w-full flex items-center px-4 py-2 text-sm transition-colors"
                        style={{ color: 'var(--color-primary-700)' }}
                        onMouseEnter={e => e.currentTarget.style.background = 'var(--color-primary-100)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                        <User className="h-4 w-4 mr-3" style={{ color: 'var(--color-primary-400)' }} />
                        My Profile
                    </button>

                    <div style={{ borderTop: '1px solid var(--color-border)' }} className="mt-1 pt-1">
                        <button
                            onClick={() => { onLogout(); setIsOpen(false); }}
                            className="w-full flex items-center px-4 py-2 text-sm transition-colors"
                            style={{ color: 'var(--color-danger-600)' }}
                            onMouseEnter={e => e.currentTarget.style.background = 'rgba(239,68,68,0.08)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                            <LogOut className="h-4 w-4 mr-3" />
                            Log out
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

function NotificationsBell() {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState([
        { id: 1, text: 'Your quota is 80% used', time: '5 min ago', type: 'warning', read: false },
        { id: 2, text: 'New team member added', time: '1 hour ago', type: 'info', read: false },
        { id: 3, text: 'Weekly report available', time: '1 day ago', type: 'success', read: false },
    ]);
    const bellRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (bellRef.current && !bellRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const unreadCount = notifications.filter(n => !n.read).length;

    const markAsRead = (id) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
    };

    const markAllAsRead = () => {
        setNotifications(prev =>
            prev.map(n => ({ ...n, read: true }))
        );
    };

    const typeColors = {
        warning: { bg: 'rgba(245,158,11,0.12)', color: 'var(--color-warning-600)' },
        info: { bg: 'rgba(37,99,235,0.12)', color: 'var(--color-accent-600)' },
        success: { bg: 'rgba(16,185,129,0.12)', color: 'var(--color-success-600)' },
    };

    return (
        <div className="relative" ref={bellRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 rounded-lg transition-colors"
                style={{ color: 'var(--color-primary-500)' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--color-primary-100)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 h-2 w-2 rounded-full animate-pulse"
                        style={{ background: 'var(--color-danger-600)' }} />
                )}
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 rounded-lg z-50 animate-scale-in"
                    style={{
                        background: 'white',
                        boxShadow: 'var(--shadow-lg)',
                        border: '1px solid var(--color-border)'
                    }}>
                    <div className="px-4 py-3 flex items-center justify-between"
                        style={{ borderBottom: '1px solid var(--color-border)' }}>
                        <h3 className="font-semibold" style={{ color: 'var(--color-primary-900)' }}>Notifications</h3>
                        <div className="flex items-center space-x-3">
                            <span className="text-xs" style={{ color: 'var(--color-primary-400)' }}>{unreadCount} new</span>
                            {unreadCount > 0 && (
                                <button
                                    onClick={markAllAsRead}
                                    className="text-xs font-medium hover:underline"
                                    style={{ color: 'var(--color-accent-600)' }}
                                >
                                    Mark all read
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                        {notifications.map((notif) => (
                            <div
                                key={notif.id}
                                className={`px-4 py-3 cursor-pointer transition-colors ${notif.read ? 'opacity-60' : ''}`}
                                style={{ borderBottom: '1px solid var(--color-border)' }}
                                onMouseEnter={e => e.currentTarget.style.background = 'var(--color-primary-50)'}
                                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <p className={`text-sm ${!notif.read ? 'font-medium' : ''}`}
                                            style={{ color: 'var(--color-primary-800)' }}>{notif.text}</p>
                                        <p className="text-xs mt-1" style={{ color: 'var(--color-primary-400)' }}>{notif.time}</p>
                                    </div>
                                    <div className="flex items-center space-x-2 ml-2">
                                        <span className="text-xs px-2 py-0.5 rounded-full"
                                            style={{
                                                background: typeColors[notif.type]?.bg,
                                                color: typeColors[notif.type]?.color
                                            }}>
                                            {notif.type}
                                        </span>
                                        {!notif.read && (
                                            <button
                                                onClick={(e) => { e.stopPropagation(); markAsRead(notif.id); }}
                                                className="text-xs hover:opacity-80"
                                                style={{ color: 'var(--color-primary-400)' }}
                                                title="Mark as read"
                                            >
                                                ✓
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {notifications.length === 0 && (
                            <div className="px-4 py-8 text-center text-sm"
                                style={{ color: 'var(--color-primary-400)' }}>
                                No notifications
                            </div>
                        )}
                    </div>
                    <div className="px-4 py-2" style={{ borderTop: '1px solid var(--color-border)' }}>
                        <button className="text-sm font-medium hover:underline"
                            style={{ color: 'var(--color-accent-600)' }}>
                            View all notifications
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}


function SearchBar() {
    const [isExpanded, setIsExpanded] = useState(false);
    const [query, setQuery] = useState('');
    const inputRef = useRef(null);

    useEffect(() => {
        if (isExpanded && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isExpanded]);

    useEffect(() => {
        function handleKeyDown(event) {
            if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                event.preventDefault();
                setIsExpanded(true);
            }
            if (event.key === 'Escape') {
                setIsExpanded(false);
                setQuery('');
            }
        }
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, []);

    return (
        <div className="relative">
            {isExpanded ? (
                <div className="flex items-center animate-fade-in">
                    <input
                        ref={inputRef}
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search users, teams, transfers..."
                        className="input w-64"
                        onBlur={() => !query && setIsExpanded(false)}
                    />
                    <button
                        onClick={() => { setIsExpanded(false); setQuery(''); }}
                        className="ml-2 p-1.5 rounded transition-colors"
                        style={{ color: 'var(--color-primary-400)' }}
                        onMouseEnter={e => e.currentTarget.style.background = 'var(--color-primary-100)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                        <X className="h-4 w-4" />
                    </button>
                </div>
            ) : (
                <button
                    onClick={() => setIsExpanded(true)}
                    className="flex items-center px-3 py-2 rounded-lg transition-colors"
                    style={{
                        background: 'var(--color-primary-100)',
                        border: '1px solid var(--color-border)',
                        color: 'var(--color-primary-500)'
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--color-primary-200)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'var(--color-primary-100)'}
                >
                    <Search className="h-5 w-5" />
                    <span className="ml-2 text-sm hidden md:inline">
                        Search
                    </span>
                    <kbd className="ml-2 hidden md:inline-flex items-center px-2 py-0.5 text-xs font-sans font-medium rounded"
                        style={{
                            color: 'var(--color-primary-400)',
                            background: 'var(--color-primary-200)',
                            border: '1px solid var(--color-border)'
                        }}>
                        Ctrl+K
                    </kbd>
                </button>
            )}
        </div>
    );
}

export default function Layout({ onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, clearUser } = useUser();
    const breadcrumbs = getBreadcrumbs(location.pathname);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
        const saved = localStorage.getItem('alfred_sidebar_collapsed');
        return saved === 'true';
    });

    useEffect(() => {
        localStorage.setItem('alfred_sidebar_collapsed', sidebarCollapsed.toString());
    }, [sidebarCollapsed]);

    const handleLogout = () => {
        clearUser();
        onLogout();
        navigate('/login');
    };

    const handleNavigateProfile = () => {
        navigate('/profile');
    };

    const toggleSidebar = () => {
        setSidebarCollapsed(!sidebarCollapsed);
    };

    return (
        <div className="min-h-screen flex" style={{ background: 'var(--color-primary-50)' }}>
            {/* Mobile menu overlay */}
            {mobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar */}
            <div className={`
                sidebar fixed inset-y-0 left-0 z-50 flex flex-col
                transform transition-all duration-300 ease-in-out
                ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
                ${sidebarCollapsed ? 'w-[56px]' : 'w-[var(--sidebar-width)]'}
            `}>
                {/* Logo Area */}
                <div className={`flex justify-center ${sidebarCollapsed ? 'p-2' : 'p-4'}`}
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', height: 'var(--topbar-height)' }}>
                    <div className="flex items-center justify-center relative w-full">
                        <img
                            src={sidebarCollapsed ? '/sidebar-mini.png' : '/sidebar-big.png'}
                            alt="Alfred"
                            className={`object-contain transition-all duration-300 ${sidebarCollapsed ? 'h-10 w-10' : 'h-10 w-auto max-w-[180px]'}`}
                        />
                        <button
                            onClick={() => setMobileMenuOpen(false)}
                            className="lg:hidden p-1 rounded absolute right-0 top-0"
                            style={{ color: 'white' }}
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>
                </div>

                {/* Navigation Groups */}
                <nav className="flex-1 py-3 overflow-y-auto overflow-x-hidden flex flex-col">
                    {navigationGroups.map((group, groupIdx) => (
                        <div key={group.label} className={groupIdx > 0 ? 'mt-4' : ''}>
                            {/* Group Label */}
                            {!sidebarCollapsed && (
                                <div className="px-4 py-1.5">
                                    <span className="text-[10px] font-semibold tracking-widest uppercase"
                                        style={{ color: 'var(--color-primary-500)' }}>
                                        {group.label}
                                    </span>
                                </div>
                            )}
                            {sidebarCollapsed && groupIdx > 0 && (
                                <div className="mx-2 my-2" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }} />
                            )}

                            {/* Group Items */}
                            <div className="space-y-0.5">
                                {group.items.map((item) => (
                                    <NavTooltip key={item.name} text={item.name} show={sidebarCollapsed}>
                                        <NavLink
                                            to={item.href}
                                            onClick={() => setMobileMenuOpen(false)}
                                            className={({ isActive }) =>
                                                `nav-link flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'px-4'} py-2 text-sm transition-all border-l-2 ${isActive
                                                    ? 'active'
                                                    : 'border-transparent'
                                                }`
                                            }
                                        >
                                            <item.icon className={`h-[18px] w-[18px] flex-shrink-0 ${sidebarCollapsed ? '' : 'mr-3'}`} />
                                            {!sidebarCollapsed && <span>{item.name}</span>}
                                        </NavLink>
                                    </NavTooltip>
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* Spacer */}
                    <div className="flex-1" />

                    {/* Bottom Navigation */}
                    <div className="pt-3 mt-auto" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                        {bottomNavigation.map((item) => (
                            <NavTooltip key={item.name} text={item.name} show={sidebarCollapsed}>
                                <NavLink
                                    to={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={({ isActive }) =>
                                        `nav-link flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'px-4'} py-2 text-sm transition-all border-l-2 ${isActive
                                            ? 'active'
                                            : 'border-transparent'
                                        }`
                                    }
                                >
                                    <item.icon className={`h-[18px] w-[18px] flex-shrink-0 ${sidebarCollapsed ? '' : 'mr-3'}`} />
                                    {!sidebarCollapsed && <span>{item.name}</span>}
                                </NavLink>
                            </NavTooltip>
                        ))}
                    </div>
                </nav>

                {/* Collapse Toggle + Version */}
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <button
                        onClick={(e) => { e.stopPropagation(); toggleSidebar(); }}
                        className={`hidden lg:flex w-full items-center ${sidebarCollapsed ? 'justify-center' : 'px-4'} py-3 transition-colors cursor-pointer`}
                        style={{ color: 'var(--color-primary-400)' }}
                        onMouseEnter={e => { e.currentTarget.style.color = 'white'; e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; }}
                        onMouseLeave={e => { e.currentTarget.style.color = 'var(--color-primary-400)'; e.currentTarget.style.background = 'transparent'; }}
                        title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                        type="button"
                    >
                        {sidebarCollapsed ? (
                            <ChevronRight className="h-5 w-5" />
                        ) : (
                            <>
                                <ChevronLeft className="h-5 w-5 mr-3" />
                                <span className="text-sm">Collapse</span>
                            </>
                        )}
                    </button>
                    {!sidebarCollapsed && (
                        <div className="px-4 py-2 text-xs"
                            style={{ color: 'var(--color-primary-500)', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                            Alfred v1.0.0
                        </div>
                    )}
                </div>
            </div>

            {/* Main Content Area */}
            <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${sidebarCollapsed ? 'lg:ml-[56px]' : 'lg:ml-[var(--sidebar-width)]'}`}>
                {/* Topbar */}
                <header className="topbar sticky top-0 z-30">
                    <div className="flex items-center justify-between px-4 md:px-6 py-0" style={{ height: 'var(--topbar-height)' }}>
                        {/* Left — Mobile menu + Breadcrumbs */}
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => setMobileMenuOpen(true)}
                                className="lg:hidden p-2 rounded-lg transition-colors"
                                style={{ color: 'var(--color-primary-500)' }}
                            >
                                <Menu className="h-5 w-5" />
                            </button>

                            {/* Breadcrumbs */}
                            <nav className="hidden sm:flex items-center space-x-2 text-sm">
                                {breadcrumbs.map((crumb, index) => (
                                    <span key={crumb.name} className="flex items-center">
                                        {index > 0 && (
                                            <ChevronRight className="h-4 w-4 mx-1"
                                                style={{ color: 'var(--color-primary-400)' }} />
                                        )}
                                        {crumb.current ? (
                                            <span className="font-medium"
                                                style={{ color: 'var(--color-primary-900)' }}>{crumb.name}</span>
                                        ) : (
                                            <NavLink
                                                to={crumb.href}
                                                className="hover:underline"
                                                style={{ color: 'var(--color-accent-600)' }}
                                            >
                                                {crumb.name}
                                            </NavLink>
                                        )}
                                    </span>
                                ))}
                            </nav>
                        </div>

                        {/* Right — Actions */}
                        <div className="flex items-center space-x-2 md:space-x-4">
                            <SearchBar />
                            <NotificationsBell />
                            <div className="hidden md:block w-px h-6" style={{ background: 'var(--color-border)' }} />
                            <UserMenu
                                user={user}
                                onLogout={handleLogout}
                                onNavigateProfile={handleNavigateProfile}
                            />
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 overflow-auto" style={{ background: 'var(--color-primary-50)' }}>
                    <Outlet />
                </main>

                {/* Footer */}
                <footer className="px-4 md:px-6 py-2" style={{
                    background: 'white',
                    borderTop: '1px solid var(--color-border)',
                    color: 'var(--color-primary-400)'
                }}>
                    <div className="flex items-center justify-between text-xs">
                        <span>Alfred — AI Token Quota Manager</span>
                        <span className="hidden sm:inline font-medium">
                            {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '.')}
                        </span>
                    </div>
                </footer>
            </div>
        </div>
    );
}
