/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       Complete routing overhaul to match UI.md spec. Adds
             missing routes: Cost Analytics, Wallets, Routing Rules,
             Security, Audit Log, Providers, API Keys, Experiments.
Root Cause:  UI spec defines 24 screens; only 14 existed.
Context:     All new routes lazy-loaded for code splitting.
Suitability: L3 model for SPA routing architecture.
──────────────────────────────────────────────────────────────
*/
import { lazy, Suspense, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/LayoutNew';
import NotificationCenter from './components/NotificationCenter';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { UserProvider } from './context/UserContext';
import { WebSocketProvider } from './context/WebSocketContext';
import api from './services/api';

// Lazy-loaded pages — code-split by route
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
const ImportExportAdmin = lazy(() => import('./pages/ImportExportAdmin'));
const CustomReportsAdmin = lazy(() => import('./pages/CustomReportsAdmin'));
const SafetyDashboard = lazy(() => import('./pages/SafetyDashboard'));

// New pages from UI spec
const CostAnalytics = lazy(() => import('./pages/CostAnalytics'));
const WalletManagement = lazy(() => import('./pages/WalletManagement'));
const RoutingRules = lazy(() => import('./pages/RoutingRules'));
const SecurityPolicies = lazy(() => import('./pages/SecurityPolicies'));
const AuditLog = lazy(() => import('./pages/AuditLog'));
const ProviderManagement = lazy(() => import('./pages/ProviderManagement'));
const ApiKeyManagement = lazy(() => import('./pages/ApiKeyManagement'));
const Experiments = lazy(() => import('./pages/Experiments'));
const PolicyManagement = lazy(() => import('./pages/PolicyManagement'));


function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-2 border-transparent"
           style={{ borderTopColor: 'var(--color-accent-500)' }}></div>
    </div>
  );
}


function ProtectedRoute({ children, isAuthenticated }) {
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(api.isAuthenticated());

  const handleLogin = () => setIsAuthenticated(true);
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
                  isAuthenticated
                    ? <Navigate to="/" replace />
                    : <Suspense fallback={<PageLoader />}><Login onLogin={handleLogin} /></Suspense>
                } />
                <Route path="/" element={
                  <ProtectedRoute isAuthenticated={isAuthenticated}>
                    <Layout onLogout={handleLogout} />
                  </ProtectedRoute>
                }>
                  {/* Overview */}
                  <Route index element={<Suspense fallback={<PageLoader />}><Dashboard /></Suspense>} />
                  <Route path="analytics/cost" element={<Suspense fallback={<PageLoader />}><CostAnalytics /></Suspense>} />

                  {/* Control */}
                  <Route path="wallets" element={<Suspense fallback={<PageLoader />}><WalletManagement /></Suspense>} />
                  <Route path="routing" element={<Suspense fallback={<PageLoader />}><RoutingRules /></Suspense>} />
                  <Route path="experiments" element={<Suspense fallback={<PageLoader />}><Experiments /></Suspense>} />
                  <Route path="policies" element={<Suspense fallback={<PageLoader />}><PolicyManagement /></Suspense>} />

                  {/* Security */}
                  <Route path="security" element={<Suspense fallback={<PageLoader />}><SecurityPolicies /></Suspense>} />
                  <Route path="audit" element={<Suspense fallback={<PageLoader />}><AuditLog /></Suspense>} />
                  <Route path="safety" element={<Suspense fallback={<PageLoader />}><SafetyDashboard /></Suspense>} />

                  {/* Product */}
                  <Route path="providers" element={<Suspense fallback={<PageLoader />}><ProviderManagement /></Suspense>} />

                  {/* Admin */}
                  <Route path="users" element={<Suspense fallback={<PageLoader />}><Users /></Suspense>} />
                  <Route path="teams" element={<Suspense fallback={<PageLoader />}><Teams /></Suspense>} />
                  <Route path="transfers" element={<Suspense fallback={<PageLoader />}><Transfers /></Suspense>} />
                  <Route path="keys" element={<Suspense fallback={<PageLoader />}><ApiKeyManagement /></Suspense>} />
                  <Route path="approvals" element={<Suspense fallback={<PageLoader />}><Approvals /></Suspense>} />
                  <Route path="notifications" element={<NotificationCenter isAdmin={true} />} />
                  <Route path="settings" element={<Suspense fallback={<PageLoader />}><Settings /></Suspense>} />

                  {/* Utilities */}
                  <Route path="integrations" element={<Suspense fallback={<PageLoader />}><Integrations /></Suspense>} />
                  <Route path="guide" element={<Suspense fallback={<PageLoader />}><UserGuide /></Suspense>} />
                  <Route path="profile" element={<Suspense fallback={<PageLoader />}><Profile /></Suspense>} />
                  <Route path="rbac-admin" element={<Suspense fallback={<PageLoader />}><RBACAdmin /></Suspense>} />
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
