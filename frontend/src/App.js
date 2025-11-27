import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AdminTraining from './pages/AdminTraining';
import Settings from './pages/Settings';
import ForgotPassword from './pages/ForgotPassword';
import SafetyGuidelines from './pages/SafetyGuidelines';
import Crowdsourcing from './pages/Crowdsourcing';
import About from './pages/About';
import Navigation from './components/Navigation';
import AlertBanner from './components/AlertBanner';
import Footer from './components/Footer';
import PageTransition from './components/PageTransition';
import './App.css';

// Private Route Component
const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-cyan-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" />;
};

// Main App Content
const AppContent = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 flex flex-col">
      <AlertBanner />
      <Navigation />
      <div className="flex-grow pt-24 pb-10"> {/* Added padding-top for fixed nav/banner */}
        <PageTransition>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/training"
              element={
                <PrivateRoute>
                  <AdminTraining />
                </PrivateRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <PrivateRoute>
                  <Settings />
                </PrivateRoute>
              }
            />
            <Route path="/guidelines" element={<SafetyGuidelines />} />
            <Route path="/report" element={<Crowdsourcing />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </PageTransition>
      </div>
      <Footer />
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
};

export default App;