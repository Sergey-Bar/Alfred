const ImportExportAdmin = lazy(() => import('./pages/ImportExportAdmin'));
const CustomReportsAdmin = lazy(() => import('./pages/CustomReportsAdmin'));
import NotificationCenter from './components/NotificationCenter';
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Main SPA entry point. Sets up global providers (theme, toast, user, websocket), lazy-loads all pages, and configures protected routing for authentication.
// Why: Centralizes all app-wide context and routing logic for maintainability and performance.
// Root Cause: Without a single entry, context and routing would be fragmented and error-prone.
// Context: All new providers or routes should be registered here. Future: consider code splitting for large dashboards.
// Model Suitability: For React SPA patterns, GPT-4.1 is sufficient; for advanced state management, a more advanced model may be preferred.
import { lazy, Suspense, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/LayoutNew';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { UserProvider } from './context/UserContext';
import { WebSocketProvider } from './context/WebSocketContext';
import api from './services/api';

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Lazy-loads all major pages for code splitting and faster initial load.
// Why: Improves performance by only loading code when needed.
// Root Cause: Eager loading all pages increases bundle size and slows down the app.
// Context: Add new pages here for lazy loading.
const Dashboard = lazy(() => import('./pages/DashboardNew'));
const Users = lazy(() => import('./pages/Users'));
const Teams = lazy(() => import('./pages/Teams'));
const Transfers = lazy(() => import('./pages/Transfers'));
const Approvals = lazy(() => import('./pages/Approvals'));
const Integrations = lazy(() => import('./pages/Integrations'));
const UserGuide = lazy(() => import('./pages/UserGuide'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));

const RBACAdmin = lazy(() => import('./pages/RBACAdmin'));
const Login = lazy(() => import('./pages/Login'));


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Simple loading spinner for lazy-loaded components.
// Why: Provides user feedback during async page loads.
// Root Cause: No feedback leads to perceived slowness.
// Context: Used as Suspense fallback for all routes.
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
    </div>
  );
}


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Wrapper for protected routes, redirects to login if not authenticated.
// Why: Prevents unauthorized access to dashboard routes.
// Root Cause: Unprotected routes would expose sensitive data.
// Context: Use for all routes requiring authentication.
function ProtectedRoute({ children, isAuthenticated }) {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Main app component. Tracks authentication state, handles login/logout, and wires up all providers and routes.
// Why: Ensures global state and routing are always in sync.
// Root Cause: Fragmented state or routing leads to bugs and security issues.
// Context: All app-wide logic should be coordinated here.
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(api.isAuthenticated());

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    api.clearApiKey();
    setIsAuthenticated(false);
  };

  return (
    <ThemeProvider>
      <ToastProvider>
        <UserProvider>
          <WebSocketProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={
                  isAuthenticated ? <Navigate to="/" replace /> : <Suspense fallback={<PageLoader />}><Login onLogin={handleLogin} /></Suspense>
                } />
                <Route path="/" element={
                  <ProtectedRoute isAuthenticated={isAuthenticated}>
                    <Layout onLogout={handleLogout} />
                  </ProtectedRoute>
                }>
                  <Route index element={<Suspense fallback={<PageLoader />}><Dashboard /></Suspense>} />
                  <Route path="users" element={<Suspense fallback={<PageLoader />}><Users /></Suspense>} />
                  <Route path="teams" element={<Suspense fallback={<PageLoader />}><Teams /></Suspense>} />
                  <Route path="transfers" element={<Suspense fallback={<PageLoader />}><Transfers /></Suspense>} />
                  <Route path="approvals" element={<Suspense fallback={<PageLoader />}><Approvals /></Suspense>} />
                  <Route path="integrations" element={<Suspense fallback={<PageLoader />}><Integrations /></Suspense>} />
                  <Route path="guide" element={<Suspense fallback={<PageLoader />}><UserGuide /></Suspense>} />
                  <Route path="profile" element={<Suspense fallback={<PageLoader />}><Profile /></Suspense>} />
                  <Route path="settings" element={<Suspense fallback={<PageLoader />}><Settings /></Suspense>} />
                  <Route path="rbac-admin" element={<Suspense fallback={<PageLoader />}><RBACAdmin /></Suspense>} />
                  <Route path="notifications" element={<NotificationCenter isAdmin={true} />} />
                  <Route path="import-export-admin" element={<Suspense fallback={<PageLoader />}><ImportExportAdmin /></Suspense>} />
                  <Route path="custom-reports-admin" element={<Suspense fallback={<PageLoader />}><CustomReportsAdmin /></Suspense>} />
                </Route>
              </Routes>
            </BrowserRouter>
          </WebSocketProvider>
        </UserProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
