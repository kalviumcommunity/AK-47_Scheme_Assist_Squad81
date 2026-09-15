import apiClient from './api';
import {
  fetchSharedApplications,
  saveSharedApplication,
  updateSharedApplicationStatus as apiUpdateStatus,
  registerSharedCitizen,
} from './sharedStoreService';
import { recordActivity } from './activityLogService';

const STORAGE_KEY = 'schemeassist_local_applications';

function getStoredApplications() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch {
    return [];
  }
}

function saveStoredApplications(applications) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(applications));
    window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
    window.dispatchEvent(new Event('storage'));
  } catch (error) {
    console.error('Failed to persist applications to localStorage:', error);
  }
}

function ensureAppDocuments(application) {
  if (!application) return application;
  if (!Array.isArray(application.documents) || application.documents.length === 0) {
    return {
      ...application,
      documents: generateDefaultDocuments(application.schemeName || application.scheme, application.citizenName),
    };
  }
  return application;
}

export async function getApplications() {
  let applications = [];
  try {
    const shared = await fetchSharedApplications();
    if (Array.isArray(shared) && shared.length > 0) applications = shared;
  } catch {
    // Fall back to local applications.
  }
  if (!applications.length) applications = getStoredApplications();
  return applications.map(ensureAppDocuments);
}

export async function getAllApplications() {
  let applications = [];
  try {
    const shared = await fetchSharedApplications();
    if (Array.isArray(shared)) applications = shared;
  } catch {
    // Fall back to local applications.
  }
  if (!applications.length) applications = getStoredApplications();
  return applications.map(ensureAppDocuments);
}

export async function getApplicationById(applicationId) {
  try {
    const response = await apiClient.get(`/applications/${applicationId}`);
    if (response.data) return response.data;
  } catch {
    // Fall back to local applications.
  }
  return getStoredApplications().find((application) => application.id === applicationId) || null;
}

export function generateDefaultDocuments(schemeName = '', citizenName = 'Applicant') {
  const scheme = (schemeName || '').toLowerCase();
  const base = [
    {
      id: 'doc-aadhaar', name: 'Aadhaar Card', category: 'Identity Proof',
      fileName: `Aadhaar_${(citizenName || 'Citizen').replace(/\s+/g, '_')}.pdf`, fileSize: '1.4 MB',
      fileType: 'application/pdf', status: 'Verified', verified: true,
      source: 'UIDAI / DigiLocker Verified', issuingAuthority: 'Unique Identification Authority of India',
      documentNumber: 'XXXX-XXXX-8665', uploadDate: new Date().toISOString().split('T')[0],
      description: 'Official national biometric identity and domicile verification document.',
    },
    {
      id: 'doc-bank', name: 'Bank Passbook & DBT Mandate', category: 'Financial Record',
      fileName: 'Bank_Passbook_DBT_Linked.pdf', fileSize: '950 KB', fileType: 'application/pdf',
      status: 'Verified', verified: true, source: 'PFMS DBT Verified',
      issuingAuthority: 'Public Financial Management System', documentNumber: 'SBIN0004128-XXXX9012',
      uploadDate: new Date().toISOString().split('T')[0],
      description: 'Aadhaar-seeded bank account statement for Direct Benefit Transfer sanction.',
    },
  ];

  const extra = scheme.includes('kisan') || scheme.includes('farmer') || scheme.includes('agriculture')
    ? { name: 'Land Ownership Record (Khatauni / 7/12 Extract)', category: 'Land & Revenue Record', fileName: 'Land_Title_Khatauni_ROR.pdf', fileSize: '2.1 MB', source: 'State Revenue Department & Bhulekh Portal', issuingAuthority: 'Department of Land Resources & Revenue', documentNumber: 'ROR-2026-KH-44910', description: 'Gazetted land record proving cultivable landholding under institutional threshold.' }
    : scheme.includes('awas') || scheme.includes('housing')
      ? { name: 'Income & Asset Certificate', category: 'Income Certification', fileName: 'Income_Certificate_Verified.pdf', fileSize: '1.1 MB', source: 'Revenue Office / Tahsildar', issuingAuthority: 'Revenue Divisional Office', documentNumber: 'INC-2026-98124', description: 'Family income assessment certificate verifying EWS/LIG category eligibility.' }
      : scheme.includes('ayushman') || scheme.includes('health') || scheme.includes('jay')
        ? { name: 'Ration Card / SECC Household Match', category: 'Household Registry', fileName: 'Ration_Card_NFSA_Record.pdf', fileSize: '1.3 MB', source: 'NFSA Portal / Food & Civil Supplies', issuingAuthority: 'Department of Food and Public Distribution', documentNumber: 'NFSA-TEL-889104', description: 'Family entitlement document certifying Ayushman Bharat health insurance coverage.' }
        : { name: 'Domicile & Residence Certificate', category: 'Domicile Verification', fileName: 'Domicile_Certificate.pdf', fileSize: '820 KB', source: 'E-Seva / MeeSeva Portal', issuingAuthority: 'Tahsildar / Sub-Divisional Magistrate', documentNumber: 'DOM-2026-00452', description: 'Certified permanent residential proof within state jurisdiction.' };

  base.push({ id: 'doc-required', ...extra, fileType: 'application/pdf', status: 'Verified', verified: true, uploadDate: new Date().toISOString().split('T')[0] });
  return base;
}

export async function submitApplication(applicationData) {
  try {
    const response = await apiClient.post('/applications', applicationData);
    if (response.data) {
      recordActivity({
        level: 'SUCCESS', source: 'APP',
        message: `Scheme application submitted: ${response.data.id || applicationData.schemeName || 'Application'}`,
        details: `Citizen: ${applicationData.citizenName || 'Citizen'} | Scheme: ${applicationData.schemeName || 'Not provided'}`,
      });
      return response.data;
    }
  } catch {
    // Fall back to local application storage when the API is unavailable.
  }

  const documents = Array.isArray(applicationData.documents) && applicationData.documents.length > 0
    ? applicationData.documents
    : generateDefaultDocuments(applicationData.schemeName, applicationData.citizenName);
  const newApplication = {
    id: applicationData.id || `APP-2026-${Math.floor(10000 + Math.random() * 90000)}`,
    schemeId: applicationData.schemeId || 'general-scheme', schemeName: applicationData.schemeName || 'Government Welfare Scheme',
    benefit: applicationData.benefit || 'Welfare Support', category: applicationData.category || 'General',
    submittedDate: new Date().toISOString().split('T')[0], citizenId: applicationData.citizenId || `CIT-${Math.floor(100000 + Math.random() * 900000)}`,
    citizenEmail: applicationData.citizenEmail || '', citizenName: applicationData.citizenName || 'Citizen',
    state: applicationData.state || '', phone: applicationData.phone || '', scheme: applicationData.schemeName || 'Government Welfare Scheme',
    status: applicationData.status || 'Pending', statusCode: (applicationData.status || 'pending').toLowerCase().replace(/\s+/g, '_'),
    currentStep: 2, totalSteps: 5, documents,
    timeline: [
      { step: 'Application Submitted', date: 'Just now', done: true },
      { step: 'Nodal Officer Review', date: 'In Progress', done: false },
      { step: 'Sanction Approval', date: 'Pending', done: false },
      { step: 'DBT Benefit Credited', date: 'Pending', done: false },
    ],
    ...applicationData,
    documents,
  };

  try {
    const usersDb = JSON.parse(localStorage.getItem('schemeassist_users_db') || '{}');
    const key = (newApplication.citizenEmail || newApplication.citizenId || newApplication.citizenName || '').toLowerCase();
    if (key && !usersDb[key]) {
      const citizen = { id: newApplication.citizenId, name: newApplication.citizenName, email: newApplication.citizenEmail, phone: newApplication.phone || '', state: newApplication.state || 'Not provided', role: 'citizen', registeredAt: new Date().toISOString(), lastLoginAt: new Date().toISOString() };
      usersDb[key] = citizen;
      localStorage.setItem('schemeassist_users_db', JSON.stringify(usersDb));
      registerSharedCitizen(citizen).catch(() => {});
    }
  } catch {
    // Ignore local registry failures.
  }

  saveStoredApplications([newApplication, ...getStoredApplications()]);
  saveSharedApplication(newApplication).catch(() => {});
  recordActivity({ level: 'SUCCESS', source: 'APP', message: `Scheme application submitted: ${newApplication.id}`, details: `Citizen: ${newApplication.citizenName} | Scheme: ${newApplication.schemeName} | Documents: ${documents.length}` });
  return newApplication;
}

export async function updateApplicationStatus(applicationId, status) {
  apiUpdateStatus(applicationId, status).catch(() => {});
  const applications = getStoredApplications();
  const currentApplication = applications.find((application) => application.id === applicationId);
  const updated = applications.map((application) => application.id === applicationId ? {
    ...application, status, statusCode: status.toLowerCase().replace(/\s+/g, '_'), reviewedAt: new Date().toISOString(),
    timeline: (application.timeline || []).map((stage, index) => ({
      ...stage,
      done: status === 'Approved' ? true : index === 0 || (status === 'Verified' && index < 2) || stage.done,
      date: index === 1 && status === 'Verified' ? new Date().toISOString().split('T')[0] : stage.date,
    })),
  } : application);
  saveStoredApplications(updated);
  const updatedApplication = updated.find((application) => application.id === applicationId) || null;
  recordActivity({ level: status === 'Rejected' ? 'WARN' : 'SUCCESS', source: 'APP', message: `Application ${applicationId} status changed to ${status}`, details: `Citizen: ${updatedApplication?.citizenName || currentApplication?.citizenName || 'Citizen'} | Previous status: ${currentApplication?.status || 'Pending'}` });
  return updatedApplication;
}

export default { getApplications, getAllApplications, getApplicationById, submitApplication, updateApplicationStatus };
