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
    id: `APP-2026-${Math.floor(10000 + Math.random() * 90000)}`,
    schemeId: applicationData.schemeId || 'general-scheme',
    schemeName: applicationData.schemeName || 'Government Welfare Scheme',
    benefit: applicationData.benefit || 'Welfare Support',
    category: applicationData.category || 'General',
    submittedDate: new Date().toISOString().split('T')[0],
    citizenId: applicationData.citizenId || '',
    citizenEmail: applicationData.citizenEmail || '',
    citizenName: applicationData.citizenName || 'Citizen',
    state: applicationData.state || '',
    scheme: applicationData.schemeName || 'Government Welfare Scheme',
    status: 'Under Review',
    statusCode: 'under_review',
    currentStep: 2,
    totalSteps: 5,
    timeline: [
      { step: 'Application Submitted', date: 'Just now', done: true },
      { step: 'Documents Verification', date: 'In progress', done: false },
      { step: 'Nodal Officer Review', date: 'Pending', done: false },
      { step: 'Department Approval', date: 'Pending', done: false },
      { step: 'DBT Benefit Credited', date: 'Pending', done: false },
    ],
    ...applicationData,
  };

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
