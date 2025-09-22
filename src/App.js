import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import authService from './services/authService';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import TouristProfile from './pages/TouristProfile';
import PanicButton from './pages/PanicButton';
import PoliceDashboard from './pages/PoliceDashboard';

// Loading Spinner Component
const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-gray-600 text-lg font-medium">Loading Smart Tourist Safety...</p>
    </div>
  </div>
);

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuth = authService.isAuthenticated();
  return isAuth ? children : <Navigate to="/login" replace />;
};

// Role-protected route
const RoleRoute = ({ allowedRole, children }) => {
  const isAuth = authService.isAuthenticated();
  const role = authService.getRole();
  if (!isAuth) return <Navigate to="/login" replace />;
  if (role !== allowedRole) {
    // Redirect to the appropriate dashboard based on current role
    const target = role === 'police' ? '/police-dashboard' : '/dashboard';
    return <Navigate to={target} replace />;
  }
  return children;
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const isAuth = authService.isAuthenticated();
  const role = authService.getRole();
  if (!isAuth) return children;
  return <Navigate to={role === 'police' ? '/police-dashboard' : '/dashboard'} replace />;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication status on app load
    const checkAuth = async () => {
      try {
        const authenticated = authService.isAuthenticated();
        setIsAuthenticated(authenticated);
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    // Listen for auth state changes
    const handleAuthChange = () => {
      const authenticated = authService.isAuthenticated();
      setIsAuthenticated(authenticated);
    };

    // Add event listener for auth state changes
    window.addEventListener('authStateChanged', handleAuthChange);
    
    // Cleanup event listener on component unmount
    return () => {
      window.removeEventListener('authStateChanged', handleAuthChange);
    };
  }, []);

  // Show loading spinner while checking authentication
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="App min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
            borderRadius: '8px',
            fontSize: '14px',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      {/* Show navbar only when authenticated */}
      {isAuthenticated && <Navbar />}

      {/* Main content area */}
      <main className={isAuthenticated ? 'pt-16' : ''}>
        <Routes>
          {/* Public Routes - accessible only when not authenticated */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />

          {/* Protected Routes - role-based */}
          <Route
            path="/dashboard"
            element={
              <RoleRoute allowedRole="user">
                <DashboardPage />
              </RoleRoute>
            }
          />
          <Route
            path="/police-dashboard"
            element={
              <RoleRoute allowedRole="police">
                <PoliceDashboard />
              </RoleRoute>
            }
          />

          {/* Routes accessible to any authenticated role */}
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <TouristProfile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/panic"
            element={
              <ProtectedRoute>
                <PanicButton />
              </ProtectedRoute>
            }
          />

          {/* Default route - redirect based on auth status and role */}
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate to={authService.getRole() === 'police' ? '/police-dashboard' : '/dashboard'} replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          
          {/* Catch-all route - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {/* Show footer only when authenticated */}
      {isAuthenticated && <Footer />}
    </div>
  );
}

export default App;