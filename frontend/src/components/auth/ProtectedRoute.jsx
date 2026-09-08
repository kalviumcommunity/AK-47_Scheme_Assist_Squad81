import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

// Protects citizen routes — redirects to /login if not authenticated as citizen
export function ProtectedRoute() {
  const { isAuthenticated, isCitizen } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!isCitizen) return <Navigate to="/login" replace />;
  return <Outlet />;
}

// Protects admin routes — redirects to /admin/login if not authenticated as admin
export function AdminRoute() {
  const { isAuthenticated, isAdmin } = useAuth();
  if (!isAuthenticated) return <Navigate to="/admin/login" replace />;
  if (!isAdmin) return <Navigate to="/admin/login" replace />;
  return <Outlet />;
}

export default ProtectedRoute;
