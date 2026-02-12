import { useState, useRef, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import {
    HomeIcon,
    UsersIcon,
    UserGroupIcon,
    ArrowsRightLeftIcon,
    ArrowRightOnRectangleIcon,
    ChevronRightIcon,
    ChevronDoubleLeftIcon,
    ChevronDoubleRightIcon,
    BookOpenIcon,
    BellIcon,
    MagnifyingGlassIcon,
    UserCircleIcon,
    Cog6ToothIcon,
    ChevronDownIcon,
    Bars3Icon,
    XMarkIcon,
    ClipboardDocumentCheckIcon,
    LinkIcon,
} from '@heroicons/react/24/outline';

const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Manage Users', href: '/users', icon: UsersIcon },
    { name: 'Manage Teams', href: '/teams', icon: UserGroupIcon },
    { name: 'Credit Reallocation', href: '/transfers', icon: ArrowsRightLeftIcon },
    { name: 'Approvals', href: '/approvals', icon: ClipboardDocumentCheckIcon },
    { name: 'Integrations', href: '/integrations', icon: LinkIcon },
];

const bottomNavigation = [
    { name: 'User Guide', href: '/guide', icon: BookOpenIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

const getBreadcrumbs = (pathname) => {
    const paths = {
        '/': [{ name: 'Dashboard', current: true }],
        '/users': [{ name: 'Dashboard', href: '/' }, { name: 'Manage Users', current: true }],
        '/teams': [{ name: 'Dashboard', href: '/' }, { name: 'Manage Teams', current: true }],
        '/transfers': [{ name: 'Dashboard', href: '/' }, { name: 'Token Transfers', current: true }],
        '/approvals': [{ name: 'Dashboard', href: '/' }, { name: 'Approvals', current: true }],
        '/integrations': [{ name: 'Dashboard', href: '/' }, { name: 'Integrations', current: true }],
        '/guide': [{ name: 'Dashboard', href: '/' }, { name: 'User Guide', current: true }],
        '/profile': [{ name: 'Dashboard', href: '/' }, { name: 'My Profile', current: true }],
        '/settings': [{ name: 'Dashboard', href: '/' }, { name: 'Settings', current: true }],
    };
    return paths[pathname] || [{ name: 'Dashboard', current: true }];
};

// Tooltip Component for collapsed sidebar
function NavTooltip({ children, text, show }) {
    if (!show) return children;

    return (
        <div className="relative group">
            {children}
            <div className="absolute left-full ml-2 top-1/2 -translate-y-1/2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                {text}
                <div className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900" />
            </div>
        </div>
    );
}

// User Menu Component
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
                className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
                <div className="h-8 w-8 rounded-full bg-[#1d3557] flex items-center justify-center text-sm font-bold text-white">
                    {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="text-left hidden md:block">
                    <p className="text-sm font-medium text-white">
                        {user?.name || 'User'}
                    </p>
                    <p className="text-xs text-gray-400">
                        {user?.role || 'Member'}
                    </p>
                </div>
                <ChevronDownIcon className={`h-4 w-4 text-gray-400 transition-transform hidden md:block ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-1 z-50 animate-scale-in">
                    <div className="px-4 py-3 border-b border-gray-700">
                        <p className="text-sm font-medium text-white">{user?.name}</p>
                        <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                    </div>

                    <button
                        onClick={() => { onNavigateProfile(); setIsOpen(false); }}
                        className="w-full flex items-center px-4 py-2 text-sm text-gray-200 hover:bg-gray-700"
                    >
                        <UserCircleIcon className="h-4 w-4 mr-3 text-gray-400" />
                        My Profile
                    </button>

                    <div className="border-t border-gray-700 mt-1 pt-1">
                        <button
                            onClick={() => { onLogout(); setIsOpen(false); }}
                            className="w-full flex items-center px-4 py-2 text-sm text-red-400 hover:bg-red-900/20"
                        >
                            <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                            Log out
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

// Notifications Component
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
        warning: 'bg-yellow-900/40 text-yellow-400',
        info: 'bg-blue-900/40 text-blue-400',
        success: 'bg-green-900/40 text-green-400',
    };

    return (
        <div className="relative" ref={bellRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
                <BellIcon className="h-5 w-5 text-gray-300" />
                {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full animate-pulse" />
                )}
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-gray-800 rounded-lg shadow-lg border border-gray-700 z-50 animate-scale-in">
                    <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
                        <h3 className="font-semibold text-white">Notifications</h3>
                        <div className="flex items-center space-x-3">
                            <span className="text-xs text-gray-400">{unreadCount} new</span>
                            {unreadCount > 0 && (
                                <button
                                    onClick={markAllAsRead}
                                    className="text-xs text-blue-400 hover:underline font-medium"
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
                                className={`px-4 py-3 hover:bg-gray-700 border-b border-gray-700 last:border-b-0 cursor-pointer transition-colors ${notif.read ? 'opacity-60' : ''
                                    }`}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <p className={`text-sm text-gray-200 ${!notif.read ? 'font-medium' : ''}`}>{notif.text}</p>
                                        <p className="text-xs text-gray-400 mt-1">{notif.time}</p>
                                    </div>
                                    <div className="flex items-center space-x-2 ml-2">
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${typeColors[notif.type]}`}>
                                            {notif.type}
                                        </span>
                                        {!notif.read && (
                                            <button
                                                onClick={(e) => { e.stopPropagation(); markAsRead(notif.id); }}
                                                className="text-xs text-gray-400 hover:text-blue-400"
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
                            <div className="px-4 py-8 text-center text-gray-400 text-sm">
                                No notifications
                            </div>
                        )}
                    </div>
                    <div className="px-4 py-2 border-t border-gray-700">
                        <button className="text-sm text-blue-400 hover:underline font-medium">
                            View all notifications
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

// Search Component
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
                        className="w-64 px-4 py-2 text-sm bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400 shadow-sm"
                        onBlur={() => !query && setIsExpanded(false)}
                    />
                    <button
                        onClick={() => { setIsExpanded(false); setQuery(''); }}
                        className="ml-2 p-1.5 rounded hover:bg-gray-700"
                    >
                        <XMarkIcon className="h-4 w-4 text-gray-400" />
                    </button>
                </div>
            ) : (
                <button
                    onClick={() => setIsExpanded(true)}
                    className="flex items-center px-3 py-2 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-colors border border-gray-600"
                >
                    <MagnifyingGlassIcon className="h-5 w-5 text-gray-300" />
                    <span className="ml-2 text-sm text-gray-300 hidden md:inline">
                        Search
                    </span>
                    <kbd className="ml-2 hidden md:inline-flex items-center px-2 py-0.5 text-xs font-sans font-medium text-gray-400 bg-gray-600 border border-gray-500 rounded">
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
        <div className="min-h-screen flex dark bg-gray-900">
            {/* Mobile menu overlay */}
            {mobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar - Fixed position, no scroll */}
            <div className={`
                fixed inset-y-0 left-0 z-50 bg-[#1d3557] flex flex-col shadow-xl
                transform transition-all duration-300 ease-in-out
                ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
                ${sidebarCollapsed ? 'w-16' : 'w-56'}
            `}>
                {/* Logo Area */}
                <div className={`border-b border-[#2d4a6f] flex justify-center ${sidebarCollapsed ? 'p-2' : 'p-4'}`}>
                    <div className="flex items-center justify-center relative w-full">
                        <img
                            src={sidebarCollapsed ? '/sidebar-mini.png' : '/sidebar-big.png'}
                            alt="Alfred"
                            className={`object-contain transition-all duration-300 ${sidebarCollapsed ? 'h-10 w-10' : 'h-20 w-auto max-w-[180px]'}`}
                        />
                        <button
                            onClick={() => setMobileMenuOpen(false)}
                            className="lg:hidden p-1 rounded hover:bg-[#2d4a6f] absolute right-0 top-0"
                        >
                            <XMarkIcon className="h-5 w-5 text-white" />
                        </button>
                    </div>
                </div>

                {/* Navigation - No scroll */}
                <nav className="flex-1 py-4 overflow-hidden flex flex-col">
                    <div className="space-y-1">
                        {navigation.map((item) => (
                            <NavTooltip key={item.name} text={item.name} show={sidebarCollapsed}>
                                <NavLink
                                    to={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'px-4'} py-2.5 text-sm transition-colors border-l-4 ${isActive
                                            ? 'bg-[#2d4a6f] text-white border-[#4a90d9] font-medium'
                                            : 'text-gray-300 hover:bg-[#2d4a6f] hover:text-white border-transparent'
                                        }`
                                    }
                                >
                                    <item.icon className={`h-5 w-5 flex-shrink-0 ${sidebarCollapsed ? '' : 'mr-3'}`} />
                                    {!sidebarCollapsed && <span>{item.name}</span>}
                                </NavLink>
                            </NavTooltip>
                        ))}
                    </div>

                    {/* Spacer - pushes bottom nav down */}
                    <div className="flex-1"></div>

                    {/* Bottom Navigation - Guide & Settings */}
                    <div className="pt-4 mt-auto border-t border-[#2d4a6f]">
                        {bottomNavigation.map((item) => (
                            <NavTooltip key={item.name} text={item.name} show={sidebarCollapsed}>
                                <NavLink
                                    to={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center ${sidebarCollapsed ? 'justify-center px-2' : 'px-4'} py-2.5 text-sm transition-colors border-l-4 ${isActive
                                            ? 'bg-[#2d4a6f] text-white border-[#4a90d9] font-medium'
                                            : 'text-gray-300 hover:bg-[#2d4a6f] hover:text-white border-transparent'
                                        }`
                                    }
                                >
                                    <item.icon className={`h-5 w-5 flex-shrink-0 ${sidebarCollapsed ? '' : 'mr-3'}`} />
                                    {!sidebarCollapsed && <span>{item.name}</span>}
                                </NavLink>
                            </NavTooltip>
                        ))}
                    </div>
                </nav>

                {/* Collapse Toggle & Version */}
                <div className="border-t border-[#2d4a6f]">
                    <button
                        onClick={(e) => { e.stopPropagation(); toggleSidebar(); }}
                        className={`hidden lg:flex w-full items-center ${sidebarCollapsed ? 'justify-center' : 'px-4'} py-3 text-gray-300 hover:text-white hover:bg-[#2d4a6f] transition-colors cursor-pointer`}
                        title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                        type="button"
                    >
                        {sidebarCollapsed ? (
                            <ChevronDoubleRightIcon className="h-5 w-5" />
                        ) : (
                            <>
                                <ChevronDoubleLeftIcon className="h-5 w-5 mr-3" />
                                <span className="text-sm">Collapse</span>
                            </>
                        )}
                    </button>
                    {!sidebarCollapsed && (
                        <div className="px-4 py-2 text-xs text-gray-400 border-t border-[#2d4a6f]">
                            Alfred v1.0.0
                        </div>
                    )}
                </div>
            </div>

            {/* Main content area - offset by sidebar width */}
            <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-56'}`}>
                {/* Top Header Bar */}
                <header className="bg-gray-800 border-gray-700 border-b shadow-sm sticky top-0 z-30">
                    <div className="flex items-center justify-between px-4 md:px-6 py-3">
                        {/* Left side - Mobile menu + Breadcrumbs */}
                        <div className="flex items-center space-x-4">
                            {/* Mobile menu button */}
                            <button
                                onClick={() => setMobileMenuOpen(true)}
                                className="lg:hidden p-2 rounded-lg hover:bg-gray-700"
                            >
                                <Bars3Icon className="h-5 w-5 text-gray-300" />
                            </button>

                            {/* Breadcrumbs */}
                            <nav className="hidden sm:flex items-center space-x-2 text-sm">
                                {breadcrumbs.map((crumb, index) => (
                                    <span key={crumb.name} className="flex items-center">
                                        {index > 0 && (
                                            <ChevronRightIcon className="h-4 w-4 text-gray-500 mx-1" />
                                        )}
                                        {crumb.current ? (
                                            <span className="font-medium text-white">{crumb.name}</span>
                                        ) : (
                                            <NavLink
                                                to={crumb.href}
                                                className="text-blue-400 hover:underline"
                                            >
                                                {crumb.name}
                                            </NavLink>
                                        )}
                                    </span>
                                ))}
                            </nav>
                        </div>

                        {/* Right side - Actions */}
                        <div className="flex items-center space-x-2 md:space-x-4">
                            {/* Search */}
                            <SearchBar />

                            {/* Notifications */}
                            <NotificationsBell />

                            {/* Divider */}
                            <div className="hidden md:block w-px h-6 bg-gray-600" />

                            {/* User Menu */}
                            <UserMenu
                                user={user}
                                onLogout={handleLogout}
                                onNavigateProfile={handleNavigateProfile}
                            />
                        </div>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1 p-4 md:p-6 overflow-auto bg-gray-900">
                    <Outlet />
                </main>

                {/* Footer */}
                <footer className="bg-gray-800 border-gray-700 text-gray-400 border-t px-4 md:px-6 py-2">
                    <div className="flex items-center justify-between text-xs">
                        <span>Alfred - AI Token Quota Manager</span>
                        <span className="hidden sm:inline font-medium">
                            {(() => {
                                const today = new Date();
                                const isToday = true; // Always today for the footer
                                return isToday ? 'Today' : today.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '.');
                            })()}
                        </span>
                    </div>
                </footer>
            </div>
        </div>
    );
}
