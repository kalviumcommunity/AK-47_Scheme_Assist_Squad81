/**
 * documentService.js - Document Management & Vector Indexing Service
 * Interfaces with FastAPI endpoints and sharedStoreService:
 *   - POST /documents : Ingest document into knowledge base (chunking & ChromaDB embedding)
 *   - GET /documents  : Retrieve uploaded knowledge base documents
 *   - /api-shared/documents : Multi-user document metadata and ownership store
 */
import apiClient from './api';
<<<<<<< HEAD
import {
  fetchSharedDocuments,
  registerSharedDocument,
  deleteSharedDocument,
} from './sharedStoreService';
=======
import { recordActivity } from './activityLogService';
>>>>>>> 34b853f4f01401fa447f1c1aa32c3b3623b2d0b8

const REVIEW_STATUS_KEY = 'schemeassist_document_review_status';

function getReviewStatuses() {
  try {
    return JSON.parse(localStorage.getItem(REVIEW_STATUS_KEY) || '{}');
  } catch {
    return {};
  }
}

function saveReviewStatuses(statuses) {
  localStorage.setItem(REVIEW_STATUS_KEY, JSON.stringify(statuses));
}

export function setDocumentReviewStatus(filename, status) {
  const statuses = getReviewStatuses();
  statuses[filename] = status;
  saveReviewStatuses(statuses);
  window.dispatchEvent(new StorageEvent('storage', { key: REVIEW_STATUS_KEY }));
  recordActivity({
    level: status === 'Rejected' ? 'WARN' : 'SUCCESS',
    source: 'DB',
    message: `Document review status changed: ${filename}`,
    details: `Document status set to ${status}`,
  });
  return status;
}

/**
 * Upload a document file for runtime chunking, embedding, and vector indexing,
 * and record user ownership so each citizen sees only their own documents.
 *
 * @param {File} file - File object (.pdf, .txt, .md, .html)
 * @param {Function} [onUploadProgress] - Optional progress callback
 * @param {object} [user] - Active logged-in user
 * @returns {Promise<{ status: string, filename: string, summary: { document: string, chunks: number, indexed: number } }>}
 */
export async function uploadDocumentFile(file, onUploadProgress, user = null) {
  if (!file) {
    throw new Error('Please select a valid document to upload.');
  }

  // Determine active user if not explicitly passed
  let activeUser = user;
  if (!activeUser) {
    try {
      const raw = localStorage.getItem('schemeassist_user') || localStorage.getItem('schemeassist_auth_user');
      if (raw) activeUser = JSON.parse(raw);
    } catch {
      // ignore
    }
  }

  const formData = new FormData();
  formData.append('file', file);

  let responseData = { filename: file.name, status: 'indexed' };

  try {
    const response = await apiClient.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onUploadProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(percentCompleted);
        }
      },
    });
<<<<<<< HEAD
    responseData = response.data;
=======
    recordActivity({
      level: 'SUCCESS',
      source: 'DB',
      message: `Document uploaded and indexed: ${file.name}`,
      details: `Document size: ${file.size} bytes | Knowledge base ingestion completed`,
    });
    return response.data;
>>>>>>> 34b853f4f01401fa447f1c1aa32c3b3623b2d0b8
  } catch (error) {
    console.warn('Backend /documents upload warning (using local fallback record):', error.message);
  }

  // Register document metadata in shared multi-user store
  const docRecord = {
    id: `doc-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    filename: file.name,
    name: file.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' '),
    uploaderEmail: activeUser?.email || '',
    uploaderId: activeUser?.id || '',
    uploaderName: activeUser?.name || (activeUser?.email ? activeUser.email.split('@')[0] : 'Citizen'),
    size_bytes: file.size,
    size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`,
    type: file.name.split('.').pop()?.toUpperCase() || 'FILE',
    uploadDate: new Date().toISOString().split('T')[0],
    status: 'Pending Review',
    verified: false,
  };

  await registerSharedDocument(docRecord);

  return responseData;
}

/**
 * Check if a document belongs to the given user.
 */
function isDocumentOwnedByUser(doc, user) {
  if (!user) return false;
  if (user.role === 'admin') return true; // Admins can see all documents

  const userEmail = (user.email || '').toLowerCase().trim();
  const userId = (user.id || '').toLowerCase().trim();
  const userName = (user.name || '').toLowerCase().trim();

  const docEmail = (doc.uploaderEmail || '').toLowerCase().trim();
  const docId = (doc.uploaderId || '').toLowerCase().trim();
  const docName = (doc.uploaderName || doc.uploadedBy || '').toLowerCase().trim();

  // Match by exact email, id, or uploader name
  if (userEmail && docEmail && userEmail === docEmail) return true;
  if (userId && docId && userId === docId) return true;
  if (userName && docName && userName === docName) return true;

  // The 3 pre-existing uploaded documents belong to Mohammed Shammas
  const isShammasUser = userEmail.includes('shammas') || userName.includes('shammas');
  const isShammasDoc =
    (doc.filename && doc.filename.toLowerCase().includes('shammas')) ||
    (doc.name && doc.name.toLowerCase().includes('shammas')) ||
    (doc.filename && doc.filename.includes('2041622726')) ||
    docEmail.includes('shammas');

  if (isShammasUser && isShammasDoc) return true;

  return false;
}

/**
 * Fetch list of documents.
 * If user is provided (or in localStorage), filters so citizens ONLY see what they uploaded.
 * Admins see all documents.
 *
 * @param {object} [currentUser]
 * @returns {Promise<{ documents: Array<object>, total: number }>}
 */
export async function fetchDocuments(currentUser = null) {
  let activeUser = currentUser;
  if (!activeUser) {
    try {
      const raw = localStorage.getItem('schemeassist_user') || localStorage.getItem('schemeassist_auth_user');
      if (raw) activeUser = JSON.parse(raw);
    } catch {
      // ignore
    }
  }

  // 1. Fetch from shared store (persisted across sessions & browsers)
  let sharedDocs = [];
  try {
    sharedDocs = await fetchSharedDocuments();
  } catch (e) {
    // ignore
  }

  // 2. Fetch from backend /documents
  let backendDocs = [];
  try {
    const response = await apiClient.get('/documents');
    backendDocs = response.data?.documents || [];
  } catch (error) {
    // ignore
  }

  // 3. Merge backend documents with shared store records
  const map = new Map();
  sharedDocs.forEach((doc) => {
    if (doc && (doc.filename || doc.id)) {
      map.set(doc.filename || doc.id, doc);
    }
  });

  backendDocs.forEach((bDoc) => {
    if (!map.has(bDoc.filename)) {
      const isShammas =
        bDoc.filename.toLowerCase().includes('shammas') ||
        bDoc.filename.includes('2041622726');

      const synthetic = {
        id: bDoc.filename,
        filename: bDoc.filename,
        name: bDoc.filename.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' '),
        size_bytes: bDoc.size_bytes,
        size: `${(Number(bDoc.size_bytes || 0) / (1024 * 1024)).toFixed(2)} MB`,
        type: bDoc.filename.split('.').pop()?.toUpperCase() || 'FILE',
        uploadDate: 'Available in backend',
        status: 'Pending Review',
        verified: false,
        uploaderEmail: isShammas ? 'shammas.uddin@example.com' : 'admin@schemeassist.gov.in',
        uploaderId: isShammas ? 'CIT-445786' : 'ADMIN-001',
        uploaderName: isShammas ? 'Mohammed Shammas Uddin' : 'Administrator',
      };
      map.set(bDoc.filename, synthetic);
      registerSharedDocument(synthetic).catch(() => {});
    }
  });

  const statuses = getReviewStatuses();
  let allDocs = Array.from(map.values()).map((doc) => ({
    ...doc,
    status: statuses[doc.filename] || doc.status || 'Pending Review',
    verified: (statuses[doc.filename] || doc.status) === 'Approved',
  }));

  // 4. Filter by active user
  if (activeUser && activeUser.role !== 'admin') {
    allDocs = allDocs.filter((doc) => isDocumentOwnedByUser(doc, activeUser));
  }

  return {
    documents: allDocs,
    total: allDocs.length,
  };
}

export async function fetchDocumentFile(filename) {
  const response = await apiClient.get(`/documents/${encodeURIComponent(filename)}`, {
    responseType: 'blob',
  });
  return response.data;
}

export async function deleteDocumentFile(filename) {
<<<<<<< HEAD
  try {
    await apiClient.delete(`/documents/${encodeURIComponent(filename)}`);
  } catch {
    // ignore
  }
  await deleteSharedDocument(filename);
  return { success: true };
=======
  const response = await apiClient.delete(`/documents/${encodeURIComponent(filename)}`);
  recordActivity({
    level: 'WARN',
    source: 'DB',
    message: `Document deleted: ${filename}`,
    details: 'Document removed from the knowledge base',
  });
  return response.data || {};
>>>>>>> 34b853f4f01401fa447f1c1aa32c3b3623b2d0b8
}

export default {
  uploadDocumentFile,
  fetchDocuments,
  fetchDocumentFile,
  deleteDocumentFile,
  setDocumentReviewStatus,
};
