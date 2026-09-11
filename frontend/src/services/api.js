/**
 * api.js - Core API Client for SchemeAssist
 * Connects React frontend with FastAPI + Gemini + ChromaDB backend.
 */

import axios from 'axios';


/**
 * FastAPI Backend URL
 *
 * Development:
 * http://127.0.0.1:8000
 *
 * Production:
 * Configure VITE_RAG_API_URL in .env
 */
export const API_BASE_URL =
  import.meta.env.VITE_RAG_API_URL ||
  'http://127.0.0.1:8000';


/**
 * Axios API Client
 */
const apiClient = axios.create({

  baseURL: API_BASE_URL,

  headers: {
    'Content-Type': 'application/json',
  },

  timeout: 60000,

});


/**
 * Request Interceptor
 *
 * Adds authentication token if available.
 */
apiClient.interceptors.request.use(

  (config) => {

    const token =
      localStorage.getItem(
        'schemeassist_auth_token'
      );

    if (
      token &&
      !config.headers.Authorization
    ) {

      config.headers.Authorization =
        `Bearer ${token}`;

    }

    return config;

  },

  (error) => {

    return Promise.reject(error);

  }

);


/**
 * Response Interceptor
 *
 * Normalizes backend errors.
 */
apiClient.interceptors.response.use(

  (response) => response,

  (error) => {

    const normalizedError = {

      status:
        error.response?.status ||
        500,

      message:

        error.response?.data?.detail ||

        error.response?.data?.message ||

        error.message ||

        'Unable to connect to SchemeAssist server.',

      data:
        error.response?.data ||
        null,

    };


    return Promise.reject(
      normalizedError
    );

  }

);


/**
 * Backend Health Check
 */
export async function getSystemHealth() {

  const { checkHealth } =
    await import('./ragService');

  return checkHealth();

}


/**
 * Ask SchemeAssist AI
 *
 * Uses:
 * FastAPI
 * ↓
 * Gemini
 * ↓
 * ChromaDB
 * ↓
 * Hybrid Retrieval
 */
export async function askRagQuestion(question) {

  const { queryRag } =
    await import('./ragService');

  return queryRag(question);

}


/**
 * Chat with SchemeAssist
 */
export async function chatWithSchemeAssist(
  question
) {

  const {
    chatWithSchemeAssist: chatFn
  } =
    await import('./ragService');

  return chatFn(question);

}


/**
 * Upload Document
 */
export async function uploadDocument(file) {

  const {
    uploadDocumentFile
  } =
    await import('./documentService');

  return uploadDocumentFile(file);

}


/**
 * Get Uploaded Documents
 */
export async function listUploadedDocuments() {

  const {
    fetchDocuments
  } =
    await import('./documentService');

  return fetchDocuments();

}


export default apiClient;