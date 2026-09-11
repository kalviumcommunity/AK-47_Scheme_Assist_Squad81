/**
 * ragService.js - SchemeAssist AI Service
 * Connects React frontend with FastAPI + Gemini + ChromaDB RAG backend.
 *
 * Backend:
 * - POST /api/chat
 * - GET /api/health
 */

import apiClient from './api';
import { getHealth } from './healthService';

/**
 * Check SchemeAssist backend health.
 *
 * @returns {Promise<object>}
 */
export async function checkHealth() {
  try {
    return await getHealth();
  } catch (error) {
    console.warn('Backend health check failed:', error.message);

    return {
      status: 'offline',
      error: error.message || 'SchemeAssist backend is offline.',
      gemini_configured: false,
      indexed_chunks: 0,
    };
  }
}


/**
 * Chat with SchemeAssist AI.
 *
 * Flow:
 * React Frontend
 *      ↓
 * FastAPI
 *      ↓
 * Gemini Embeddings
 *      ↓
 * ChromaDB
 *      ↓
 * Hybrid Retrieval
 *      ↓
 * Gemini AI
 *      ↓
 * Answer + Sources
 *
 * @param {string} question
 * @returns {Promise<object>}
 */
export async function chatWithSchemeAssist(question) {

  const cleanQuestion = (question || '').trim();

  if (!cleanQuestion || cleanQuestion.length < 3) {
    throw new Error(
      'Question must be at least 3 characters long.'
    );
  }

  try {

    const response = await apiClient.post(
      '/api/chat',
      {
        question: cleanQuestion,
      }
    );

    const data = response.data || {};

    return {

      answer: data.answer || '',

      eligibility: data.eligibility || '',

      benefits: data.benefits || '',

      application_process:
        Array.isArray(data.application_process)
          ? data.application_process
          : [],

      documents_required:
        Array.isArray(data.documents_required)
          ? data.documents_required
          : [],

      sources:
        Array.isArray(data.sources)
          ? data.sources.map((source) => ({
            scheme:
              source.scheme ||
              'Government Welfare Scheme',

            source:
              source.source ||
              'Scheme Document',

            section:
              source.section ||
              'General Overview',

            chunk_id:
              source.chunk_id || '',

            score:
              source.score || 0,
          }))
          : [],

      status:
        data.status || 'answered',

      answer_mode:
        data.answer_mode || 'general_ai',
    };

  } catch (error) {

    console.error(
      'SchemeAssist API Error:',
      error
    );

    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Failed to connect to SchemeAssist AI.';

    throw new Error(errorMessage);
  }
}


/**
 * Query SchemeAssist RAG pipeline.
 *
 * @param {string} question
 * @returns {Promise<object>}
 */
export async function queryRag(question) {

  return chatWithSchemeAssist(question);

}


/**
 * Default Service Export
 */
export default {

  checkHealth,

  chatWithSchemeAssist,

  queryRag,

};