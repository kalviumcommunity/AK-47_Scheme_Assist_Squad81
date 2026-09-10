import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const USERS_DB_KEY = 'schemeassist_users_db';
const USER_KEY = 'schemeassist_user';
const AUTH_USER_KEY = 'schemeassist_auth_user';
const AUTH_TOKEN_KEY = 'schemeassist_auth_token';

// Seed default users if not already present
function getStoredUsersDb() {
  try {
    const raw = localStorage.getItem(USERS_DB_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) {
    console.warn('Failed to parse users database:', e);
  }

  const initialDb = {
    'rajesh.kumar@example.com': {
      id: 'CIT-784920',
      name: 'Rajesh Kumar',
      email: 'rajesh.kumar@example.com',
      phone: '+91 98765 43210',
      state: 'Uttar Pradesh',
      role: 'citizen',
    },
    'admin@schemeassist.gov.in': {
      id: 'ADM-001',
      name: 'System Administrator',
      email: 'admin@schemeassist.gov.in',
      role: 'admin',
      department: 'Ministry of Electronics & IT',
    },
  };
  localStorage.setItem(USERS_DB_KEY, JSON.stringify(initialDb));
  return initialDb;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  // Login handler
  const login = (userData) => {
    if (!userData) return;
    const cleanUser = {
      ...userData,
      name: userData.name?.trim() || 'Citizen',
      email: userData.email?.trim() || '',
      role: userData.role || 'citizen',
    };

    localStorage.setItem(USER_KEY, JSON.stringify(cleanUser));
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(cleanUser));
    localStorage.setItem(AUTH_TOKEN_KEY, 'token_' + Date.now());

    // Update users database with this user
    if (cleanUser.email) {
      const db = getStoredUsersDb();
      const normalizedEmail = cleanUser.email.toLowerCase();
      db[normalizedEmail] = {
        ...db[normalizedEmail],
        ...cleanUser,
      };
      localStorage.setItem(USERS_DB_KEY, JSON.stringify(db));
    }

    setUser(cleanUser);
  };

  // Register new citizen
  const register = (newUserData) => {
    const db = getStoredUsersDb();
    const normalizedEmail = newUserData.email.toLowerCase().trim();
    const fullUser = {
      id: 'CIT-' + Math.floor(100000 + Math.random() * 900000),
      name: newUserData.name.trim(),
      email: newUserData.email.trim(),
      phone: newUserData.phone?.trim() || '',
      state: newUserData.state || '',
      role: newUserData.role || 'citizen',
      registeredAt: new Date().toISOString(),
    };

    db[normalizedEmail] = fullUser;
    localStorage.setItem(USERS_DB_KEY, JSON.stringify(db));

    login(fullUser);
    return fullUser;
  };

  // Find user by email from database
  const findUserByEmail = (email) => {
    if (!email) return null;
    const db = getStoredUsersDb();
    return db[email.toLowerCase().trim()] || null;
  };

  // Update profile
  const updateProfile = (updates) => {
    if (!user) return;
    const updated = { ...user, ...updates };
    login(updated);
  };

  // Logout handler
  const logout = () => {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setUser(null);
  };

  const isAuthenticated = !!user;
  const isAdmin = user?.role === 'admin';
  const isCitizen = user?.role === 'citizen';

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        updateProfile,
        findUserByEmail,
        isAuthenticated,
        isAdmin,
        isCitizen,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
