/**
 * applicationService.js - Application Lifecycle & Tracking Service
 * Manages scheme applications, multi-step submissions, and status tracking.
 */
import apiClient from './api';
import {
  fetchSharedApplications,
  saveSharedApplication,
  updateSharedApplicationStatus as apiUpdateStatus,
  registerSharedCitizen,
} from './sharedStoreService';

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

function ensureAppDocuments(app) {
  if (!app) return app;
  if (!Array.isArray(app.documents) || app.documents.length === 0) {
    return {
      ...app,
      documents: generateDefaultDocuments(app.schemeName || app.scheme, app.citizenName)
    };
  }
  return app;
}

/**
 * Fetch all applications for the authenticated citizen.
 *
 * @returns {Promise<Array<object>>}
 */
export async function getApplications() {
  let list = [];
  try {
    const shared = await fetchSharedApplications();
    if (Array.isArray(shared) && shared.length > 0) list = shared;
  } catch (error) {
    // Fallback
  }
  if (!list.length) list = getStoredApplications();
  return list.map(ensureAppDocuments);
}

export async function getAllApplications() {
  let list = [];
  try {
    const shared = await fetchSharedApplications();
    if (Array.isArray(shared)) list = shared;
  } catch (error) {
    // Fallback
  }
  if (!list.length) list = getStoredApplications();
  return list.map(ensureAppDocuments);
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

export function generateDefaultDocuments(schemeName = '', citizenName = 'Applicant') {
  const s = (schemeName || '').toLowerCase();
  const base = [
    {
      id: 'doc-aadhaar',
      name: 'Aadhaar Card',
      category: 'Identity Proof',
      fileName: `Aadhaar_${(citizenName || 'Citizen').replace(/\s+/g, '_')}.pdf`,
      fileSize: '1.4 MB',
      fileType: 'application/pdf',
      status: 'Verified',
      verified: true,
      source: 'UIDAI / DigiLocker Verified',
      issuingAuthority: 'Unique Identification Authority of India',
      documentNumber: 'XXXX-XXXX-8665',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Official national biometric identity and domicile verification document.'
    },
    {
      id: 'doc-bank',
      name: 'Bank Passbook & DBT Mandate',
      category: 'Financial Record',
      fileName: 'Bank_Passbook_DBT_Linked.pdf',
      fileSize: '950 KB',
      fileType: 'application/pdf',
      status: 'Verified',
      verified: true,
      source: 'PFMS DBT Verified',
      issuingAuthority: 'Public Financial Management System',
      documentNumber: 'SBIN0004128-XXXX9012',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Aadhaar-seeded bank account statement for Direct Benefit Transfer sanction.'
    },
  ];

  if (s.includes('kisan') || s.includes('farmer') || s.includes('agriculture')) {
    base.push({
      id: 'doc-land',
      name: 'Land Ownership Record (Khatauni / 7/12 Extract)',
      category: 'Land & Revenue Record',
      fileName: 'Land_Title_Khatauni_ROR.pdf',
      fileSize: '2.1 MB',
      fileType: 'application/pdf',
      status: 'Verified',
      verified: true,
      source: 'State Revenue Department & Bhulekh Portal',
      issuingAuthority: 'Department of Land Resources & Revenue',
      documentNumber: 'ROR-2026-KH-44910',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Gazetted land record proving cultivable landholding under institutional threshold.'
    });
  } else if (s.includes('awas') || s.includes('housing')) {
    base.push({
      id: 'doc-income',
      name: 'Income & Asset Certificate',
      category: 'Income Certification',
      fileName: 'Income_Certificate_Verified.pdf',
      fileSize: '1.1 MB',
      fileType: 'application/pdf',
      status: 'Verified',
      verified: true,
      source: 'Revenue Office / Tahsildar',
      issuingAuthority: 'Revenue Divisional Office',
      documentNumber: 'INC-2026-98124',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Family income assessment certificate verifying EWS/LIG category eligibility.'
    });
  } else if (s.includes('ayushman') || s.includes('health') || s.includes('jay')) {
    base.push({
      id: 'doc-ration',
      name: 'Ration Card / SECC Household Match',
      category: 'Household Registry',
      fileName: 'Ration_Card_NFSA_Record.pdf',
      fileSize: '1.3 MB',
      fileType: 'application/pdf',
      status: 'Verified',
      verified: true,
      source: 'NFSA Portal / Food & Civil Supplies',
      issuingAuthority: 'Department of Food and Public Distribution',
      documentNumber: 'NFSA-TEL-889104',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Family entitlement document certifying Ayushman Bharat health insurance coverage.'
    });
  } else {
    base.push({
      id: 'doc-domicile',
      name: 'Domicile & Residence Certificate',
      category: 'Domicile Verification',
      fileName: 'Domicile_Certificate.pdf',
      fileSize: '820 KB',
      fileType: 'application/pdf',
      status: 'Verified',
      verified: true,
      source: 'E-Seva / MeeSeva Portal',
      issuingAuthority: 'Tahsildar / Sub-Divisional Magistrate',
      documentNumber: 'DOM-2026-00452',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Certified permanent residential proof within state jurisdiction.'
    });
  }

  return base;
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

  const applicantDocs = Array.isArray(applicationData.documents) && applicationData.documents.length > 0
    ? applicationData.documents
    : generateDefaultDocuments(applicationData.schemeName, applicationData.citizenName);

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
    documents: applicantDocs,
    timeline: [
      { step: 'Application Submitted', date: 'Just now', done: true },
      { step: 'Nodal Officer Review', date: 'In Progress', done: false },
      { step: 'Sanction Approval', date: 'Pending', done: false },
      { step: 'DBT Benefit Credited', date: 'Pending', done: false },
    ],
    ...applicationData,
    documents: applicantDocs,
  };

  // Register or update applicant citizen in users database so they appear in Citizen Registry
  try {
    const usersRaw = localStorage.getItem('schemeassist_users_db');
    const usersDb = usersRaw ? JSON.parse(usersRaw) : {};
    const key = (newApp.citizenEmail || newApp.citizenId || newApp.citizenName || '').toLowerCase();
    if (key && !usersDb[key]) {
      const citizenRecord = {
        id: newApp.citizenId,
        name: newApp.citizenName,
        email: newApp.citizenEmail,
        phone: newApp.phone || '',
        state: newApp.state || 'Not provided',
        role: 'citizen',
        registeredAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
      };
      usersDb[key] = citizenRecord;
      localStorage.setItem('schemeassist_users_db', JSON.stringify(usersDb));
      registerSharedCitizen(citizenRecord).catch(() => {});
    }
  } catch {
    // ignore
  }

  const list = getStoredApplications();
  const updated = [newApp, ...list];
  saveStoredApplications(updated);

  // Sync to shared backend server for multi-admin and cross-device visibility
  saveSharedApplication(newApp).catch(() => {});

  return newApp;
}

export async function updateApplicationStatus(applicationId, status) {
  // Sync to shared backend
  apiUpdateStatus(applicationId, status).catch(() => {});

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
