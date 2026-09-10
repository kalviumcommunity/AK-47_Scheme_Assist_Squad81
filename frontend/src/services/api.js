/**
 * api.js - Core Axios Client for SchemeAssist Services
 * Handles baseURL configuration, auth token injection, and unified error handling.
 */
import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_RAG_API_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor: attach bearer token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('schemeassist_auth_token');
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: normalize error messages
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const normalizedError = {
      status: error.response?.status || 500,
      message:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'An unexpected network error occurred.',
      data: error.response?.data || null,
      raw: error,
    };
    return Promise.reject(normalizedError);
  }
);

// Backwards-compatible utility wrappers that delegate to specialized services
export async function getSystemHealth() {
  const { checkHealth } = await import('./ragService');
  return checkHealth();
}

export async function askRagQuestion(question) {
  const { queryRag } = await import('./ragService');
  return queryRag(question);
}

export async function chatWithSchemeAssist(question) {
  const { chatWithSchemeAssist: chatFn } = await import('./ragService');
  return chatFn(question);
}

export async function uploadDocument(file) {
  const { uploadDocumentFile } = await import('./documentService');
  return uploadDocumentFile(file);
}

export async function listUploadedDocuments() {
  const { fetchDocuments } = await import('./documentService');
  return fetchDocuments();
}

export default apiClient;
