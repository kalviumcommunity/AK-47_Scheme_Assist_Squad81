/**
 * documentService.js - Document Management & Vector Indexing Service
 * Interfaces with FastAPI endpoints:
 *   - POST /documents : Ingest document into knowledge base (chunking & ChromaDB embedding)
 *   - GET /documents  : Retrieve uploaded knowledge base documents
 */
import apiClient from './api';

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
  return status;
}

/**
 * Upload a document file for runtime chunking, embedding, and vector indexing.
 *
 * @param {File} file - File object (.pdf, .txt, .md, .html)
 * @param {Function} [onUploadProgress] - Optional progress callback
 * @returns {Promise<{ status: string, filename: string, summary: { document: string, chunks: number, indexed: number } }>}
 */
export async function uploadDocumentFile(file, onUploadProgress) {
  if (!file) {
    throw new Error('Please select a valid document to upload.');
  }

  const formData = new FormData();
  formData.append('file', file);

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
    return response.data;
  } catch (error) {
    throw new Error(error.message || 'Failed to upload and index document.');
  }
}

/**
 * Fetch list of indexed documents in the knowledge base.
 *
 * @returns {Promise<{ documents: Array<{ filename: string, size_bytes: number, path: string }>, total: number }>}
 */
export async function fetchDocuments() {
  try {
    const response = await apiClient.get('/documents');
    const data = response.data || { documents: [], total: 0 };
    const statuses = getReviewStatuses();
    return {
      ...data,
      documents: (data.documents || []).map((document) => ({
        ...document,
        status: statuses[document.filename] || 'Pending Review',
      })),
    };
  } catch (error) {
    console.warn('Failed to fetch /documents from backend, falling back to empty list:', error.message);
    return { documents: [], total: 0 };
  }
}

export async function fetchDocumentFile(filename) {
  const response = await apiClient.get(`/documents/${encodeURIComponent(filename)}`, {
    responseType: 'blob',
  });
  return response.data;
}

export async function deleteDocumentFile(filename) {
  const response = await apiClient.delete(`/documents/${encodeURIComponent(filename)}`);
  return response.data || {};
}

export default {
  uploadDocumentFile,
  fetchDocuments,
  fetchDocumentFile,
  deleteDocumentFile,
  setDocumentReviewStatus,
};
