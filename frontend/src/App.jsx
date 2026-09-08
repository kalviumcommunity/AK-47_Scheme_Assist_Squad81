import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Auth
import { ProtectedRoute, AdminRoute } from './components/auth/ProtectedRoute';

// Layouts
import PublicLayout from './layouts/PublicLayout';
import MainLayout from './layouts/MainLayout';
import AdminLayout from './layouts/AdminLayout';

// Public Pages
import LandingPage from './pages/public/LandingPage';
import OnboardingPage from './pages/public/OnboardingPage';

// Auth Pages
import UserLoginPage from './pages/auth/UserLoginPage';
import UserSignupPage from './pages/auth/UserSignupPage';
import AdminLoginPage from './pages/auth/AdminLoginPage';

// Citizen Pages
import DashboardPage from './pages/citizen/DashboardPage';
import SchemeDiscoveryPage from './pages/citizen/SchemeDiscoveryPage';
import SchemeDetailPage from './pages/citizen/SchemeDetailPage';
import AIAnalysisPage from './pages/citizen/AIAnalysisPage';
import ApplicationPage from './pages/citizen/ApplicationPage';
import ApplicationTrackingPage from './pages/citizen/ApplicationTrackingPage';
import DocumentsPage from './pages/citizen/DocumentsPage';
import AIAssistantPage from './pages/citizen/AIAssistantPage';
import HelpdeskPage from './pages/citizen/HelpdeskPage';
import SettingsPage from './pages/citizen/SettingsPage';

// Admin Pages
import AdminOverviewPage from './pages/admin/AdminOverviewPage';
import AdminSchemesPage from './pages/admin/AdminSchemesPage';
import AdminCitizensPage from './pages/admin/AdminCitizensPage';
import AdminApplicationsPage from './pages/admin/AdminApplicationsPage';
import AdminDocumentsPage from './pages/admin/AdminDocumentsPage';
import AdminHelpdeskPage from './pages/admin/AdminHelpdeskPage';
import AdminAnalyticsPage from './pages/admin/AdminAnalyticsPage';
import SystemLogsPage from './pages/admin/SystemLogsPage';
import AdminSettingsPage from './pages/admin/AdminSettingsPage';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ─── Public Routes ─── */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<LandingPage />} />
        </Route>

        {/* ─── Auth Routes (no layout) ─── */}
        <Route path="/login" element={<UserLoginPage />} />
        <Route path="/signup" element={<UserSignupPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />

        {/* ─── Onboarding (requires citizen auth) ─── */}
        <Route element={<ProtectedRoute />}>
          <Route path="/onboarding" element={<OnboardingPage />} />
        </Route>

        {/* ─── Protected Citizen Routes ─── */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/schemes" element={<SchemeDiscoveryPage />} />
            <Route path="/schemes/:id" element={<SchemeDetailPage />} />
            <Route path="/ai-analysis" element={<AIAnalysisPage />} />
            <Route path="/apply/:id" element={<ApplicationPage />} />
            <Route path="/applications" element={<ApplicationTrackingPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/ai-assistant" element={<AIAssistantPage />} />
            <Route path="/helpdesk" element={<HelpdeskPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        {/* ─── Protected Admin Routes with Dedicated Admin Layout & Sidebar ─── */}
        <Route element={<AdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<AdminOverviewPage />} />
            <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
            <Route path="/admin/schemes" element={<AdminSchemesPage />} />
            <Route path="/admin/citizens" element={<AdminCitizensPage />} />
            <Route path="/admin/applications" element={<AdminApplicationsPage />} />
            <Route path="/admin/documents" element={<AdminDocumentsPage />} />
            <Route path="/admin/helpdesk" element={<AdminHelpdeskPage />} />
            <Route path="/admin/logs" element={<SystemLogsPage />} />
            <Route path="/admin/settings" element={<AdminSettingsPage />} />
          </Route>
        </Route>

        {/* ─── Fallback ─── */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
