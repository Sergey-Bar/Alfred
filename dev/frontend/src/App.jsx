import { lazy, Suspense, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/LayoutNew';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { UserProvider } from './context/UserContext';
import api from './services/api';

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/DashboardNew'));
const Users = lazy(() => import('./pages/Users'));
const Teams = lazy(() => import('./pages/Teams'));
const Transfers = lazy(() => import('./pages/Transfers'));
const Approvals = lazy(() => import('./pages/Approvals'));
const Integrations = lazy(() => import('./pages/Integrations'));
const UserGuide = lazy(() => import('./pages/UserGuide'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));
const Login = lazy(() => import('./pages/Login'));

// Loading spinner for lazy components
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
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
              </Route>
            </Routes>
          </BrowserRouter>
        </UserProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
