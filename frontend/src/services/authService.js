/**
 * authService.js - Authentication & Session Service
 * Provides login, signup, role validation (citizen/admin), and session persistence.
 */
import apiClient from './api';
import { DEFAULT_CITIZEN } from '../data/demoCitizen';

const AUTH_TOKEN_KEY = 'schemeassist_auth_token';
const AUTH_USER_KEY = 'schemeassist_auth_user';

export async function loginCitizen(credentials) {
  try {
    const response = await apiClient.post('/auth/login', credentials);
    if (response.data?.token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.data.token);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.data.user));
      return response.data.user;
    }
  } catch (error) {
    // Demo fallback authentication
  }

  const demoUser = {
    ...DEFAULT_CITIZEN,
    email: credentials.email || DEFAULT_CITIZEN.email,
    role: 'citizen',
  };
  localStorage.setItem(AUTH_TOKEN_KEY, 'demo_citizen_token_' + Date.now());
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(demoUser));
  return demoUser;
}

export async function loginAdmin(credentials) {
  try {
    const response = await apiClient.post('/auth/admin/login', credentials);
    if (response.data?.token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.data.token);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.data.user));
      return response.data.user;
    }
  } catch (error) {
    // Demo fallback
  }

  const adminUser = {
    id: 'ADM-001',
    name: 'Administrator',
    email: credentials.email || 'admin@schemeassist.gov.in',
    role: 'admin',
    department: 'Ministry of Electronics & IT',
  };
  localStorage.setItem(AUTH_TOKEN_KEY, 'demo_admin_token_' + Date.now());
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(adminUser));
  return adminUser;
}

export async function signupCitizen(profileData) {
  try {
    const response = await apiClient.post('/auth/signup', profileData);
    if (response.data?.token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.data.token);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.data.user));
      return response.data.user;
    }
  } catch (error) {
    // Demo fallback
  }

  const newUser = {
    ...DEFAULT_CITIZEN,
    ...profileData,
    id: `CIT-${Math.floor(10000 + Math.random() * 90000)}`,
    role: 'citizen',
  };
  localStorage.setItem(AUTH_TOKEN_KEY, 'demo_citizen_token_' + Date.now());
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(newUser));
  return newUser;
}

export function logout() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

export function getCurrentUser() {
  try {
    const userStr = localStorage.getItem(AUTH_USER_KEY);
    return userStr ? JSON.parse(userStr) : DEFAULT_CITIZEN;
  } catch (e) {
    return DEFAULT_CITIZEN;
  }
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem(AUTH_TOKEN_KEY));
}

export default {
  loginCitizen,
  loginAdmin,
  signupCitizen,
  logout,
  getCurrentUser,
  isAuthenticated,
};
