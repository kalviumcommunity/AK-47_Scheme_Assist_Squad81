/**
 * api.js - Backend API client for SchemeAssist RAG & Ingestion service
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_RAG_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

/**
 * Fetch system health and vector index count
 */
export async function getSystemHealth() {
  try {
    const response = await client.get('/health');
    return response.data;
  } catch (error) {
    console.warn('Backend /health unreachable, falling back to simulated state:', error.message);
    return {
      status: 'offline',
      embedding_model: 'offline-mode',
      chat_model: 'gpt-4o-mini',
      vector_db_url: 'chroma_db',
      collection_name: 'schemeassist_chunks',
      openai_configured: false,
      indexed_chunks: 26,
    };
  }
}

/**
 * Ask question to SchemeAssist RAG pipeline
 * POST /query
 */
export async function askRagQuestion(question) {
  try {
    const response = await client.post('/query', { question });
    return response.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error(error.message || 'Failed to communicate with SchemeAssist RAG service.');
  }
}

/**
 * Ingest document into knowledge base
 * POST /documents
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await client.post('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error(error.message || 'Failed to upload document.');
  }
}

/**
 * List uploaded documents from backend
 * GET /documents
 */
export async function listUploadedDocuments() {
  try {
    const response = await client.get('/documents');
    return response.data;
  } catch (error) {
    console.warn('Failed to fetch /documents:', error.message);
    return { documents: [], total: 0 };
  }
}

export default client;
