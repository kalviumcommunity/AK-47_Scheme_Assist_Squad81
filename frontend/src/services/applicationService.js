/**
 * applicationService.js - Application Lifecycle & Tracking Service
 * Manages scheme applications, multi-step submissions, and status tracking.
 */
import apiClient from './api';

const STORAGE_KEY = 'schemeassist_local_applications';

function getStoredApplications() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveStoredApplications(apps) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(apps));
    try {
      window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
      window.dispatchEvent(new Event('storage'));
    } catch {
      // ignore
    }
  } catch (e) {
    console.error('Failed to persist applications to localStorage:', e);
  }
}

/**
 * Fetch all applications for the authenticated citizen.
 *
 * @returns {Promise<Array<object>>}
 */
export async function getApplications() {
  try {
    const response = await apiClient.get('/applications');
    if (Array.isArray(response.data)) return response.data;
  } catch (error) {
    // Fallback to local storage / demo dataset
  }

  return getStoredApplications();
}

export async function getAllApplications() {
  return getStoredApplications();
}

/**
 * Fetch application details by application ID.
 *
 * @param {string} applicationId
 * @returns {Promise<object|null>}
 */
export async function getApplicationById(applicationId) {
  try {
    const response = await apiClient.get(`/applications/${applicationId}`);
    if (response.data) return response.data;
  } catch (error) {
    // Fallback
  }

  const list = getStoredApplications();
  return list.find((a) => a.id === applicationId) || null;
}

/**
 * Submit a new scheme application.
 *
 * @param {object} applicationData
 * @returns {Promise<object>}
 */
export async function submitApplication(applicationData) {
  try {
    const response = await apiClient.post('/applications', applicationData);
    if (response.data) return response.data;
  } catch (error) {
    // Generate standard simulated application response if backend endpoint not active
  }

  const newApp = {
    id: applicationData.id || `APP-2026-${Math.floor(10000 + Math.random() * 90000)}`,
    schemeId: applicationData.schemeId || 'general-scheme',
    schemeName: applicationData.schemeName || 'Government Welfare Scheme',
    benefit: applicationData.benefit || 'Welfare Support',
    category: applicationData.category || 'General',
    submittedDate: new Date().toISOString().split('T')[0],
    citizenId: applicationData.citizenId || `CIT-${Math.floor(100000 + Math.random() * 900000)}`,
    citizenEmail: applicationData.citizenEmail || '',
    citizenName: applicationData.citizenName || 'Citizen',
    state: applicationData.state || '',
    phone: applicationData.phone || '',
    scheme: applicationData.schemeName || 'Government Welfare Scheme',
    status: applicationData.status || 'Pending',
    statusCode: (applicationData.status || 'pending').toLowerCase().replace(/\s+/g, '_'),
    currentStep: 2,
    totalSteps: 5,
    timeline: [
      { step: 'Application Submitted', date: 'Just now', done: true },
      { step: 'Nodal Officer Review', date: 'In Progress', done: false },
      { step: 'Sanction Approval', date: 'Pending', done: false },
      { step: 'DBT Benefit Credited', date: 'Pending', done: false },
    ],
    ...applicationData,
  };

  // Register or update applicant citizen in users database so they appear in Citizen Registry
  try {
    const usersRaw = localStorage.getItem('schemeassist_users_db');
    const usersDb = usersRaw ? JSON.parse(usersRaw) : {};
    const key = (newApp.citizenEmail || newApp.citizenId || newApp.citizenName || '').toLowerCase();
    if (key && !usersDb[key]) {
      usersDb[key] = {
        id: newApp.citizenId,
        name: newApp.citizenName,
        email: newApp.citizenEmail,
        phone: newApp.phone || '',
        state: newApp.state || 'Not provided',
        role: 'citizen',
        registeredAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
      };
      localStorage.setItem('schemeassist_users_db', JSON.stringify(usersDb));
    }
  } catch {
    // ignore
  }

  const list = getStoredApplications();
  const updated = [newApp, ...list];
  saveStoredApplications(updated);

  return newApp;
}

export async function updateApplicationStatus(applicationId, status) {
  const applications = getStoredApplications();
  const updated = applications.map((application) => (
    application.id === applicationId
      ? {
        ...application,
        status,
        statusCode: status.toLowerCase().replace(/\s+/g, '_'),
        reviewedAt: new Date().toISOString(),
        timeline: (application.timeline || []).map((stage, index) => ({
          ...stage,
          done: status === 'Approved' ? true : index === 0 || stage.done,
          date: index === 2 && status !== 'Under Review' ? new Date().toISOString().split('T')[0] : stage.date,
        })),
      }
      : application
  ));
  saveStoredApplications(updated);
  return updated.find((application) => application.id === applicationId) || null;
}

export default {
  getApplications,
  getAllApplications,
  getApplicationById,
  submitApplication,
  updateApplicationStatus,
};
