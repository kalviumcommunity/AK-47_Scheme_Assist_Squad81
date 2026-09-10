/**
 * ragService.js - Dedicated RAG Pipeline Service
 * Communicates directly with the FastAPI RAG backend on POST /query, POST /query_stream, and GET /health.
 *
 * Backend Contract:
 * - POST /query
 *     Request:  { question: string (3-1000 chars) }
 *     Response: {
 *       answer: string,
 *       sources: Array<{ source: string, chunk_id: string|null, score: number|null }>,
 *       status: "answered" | "refused_weak_context" | string
 *     }
 * - GET /health
 *     Response: {
 *       status: string,
 *       embedding_model: string,
 *       chat_model: string,
 *       vector_db_url: string,
 *       collection_name: string,
 *       openai_configured: boolean,
 *       indexed_chunks: number
 *     }
 */
import apiClient, { API_BASE_URL } from './api';

/**
 * Check backend liveness and index status.
 * Calls GET /api/health directly on FastAPI backend.
 * @returns {Promise<object>}
 */
export async function checkHealth() {
  try {
    const response = await apiClient.get('/api/health');
    return response.data;
  } catch (err) {
    // Try /health alias if /api/health fails
    try {
      const fallback = await apiClient.get('/health');
      return fallback.data;
    } catch (error) {
      console.warn('Backend health check failed:', error.message);
      return {
        status: 'offline',
        error: error.message || 'FastAPI backend is offline.',
        openai_configured: false,
        indexed_chunks: 0,
      };
    }
  }
}

/**
 * Chat with SchemeAssist AI via POST /api/chat.
 * Connects frontend to FastAPI backend, RAG vector retrieval, and live OpenAI API.
 * Never uses mock data or static responses.
 *
 * @param {string} question - User's query about government schemes
 * @returns {Promise<{
 *   answer: string,
 *   eligibility: string,
 *   benefits: string,
 *   application_process: string[],
 *   documents_required: string[],
 *   sources: Array<{ scheme: string, source: string, section: string }>,
 *   status: string
 * }>}
 */
export async function chatWithSchemeAssist(question) {
  const cleanQuestion = (question || '').trim();
  if (!cleanQuestion || cleanQuestion.length < 3) {
    throw new Error('Question must be at least 3 characters long.');
  }

  try {
    const response = await apiClient.post('/api/chat', { question: cleanQuestion });
    const data = response.data || {};
    return {
      answer: data.answer || '',
      eligibility: data.eligibility || '',
      benefits: data.benefits || '',
      application_process: Array.isArray(data.application_process) ? data.application_process : [],
      documents_required: Array.isArray(data.documents_required) ? data.documents_required : [],
      sources: (data.sources || []).map((src) => ({
        scheme: src.scheme || 'Government Welfare Scheme',
        source: src.source || 'Official Scheme Document',
        section: src.section || 'General Overview',
      })),
      status: data.status || 'answered',
    };
  } catch (error) {
    // Pass live backend error message directly (e.g. 429 quota, 401 auth, 500 error)
    const errDetail = error.message || error.data?.detail || 'Failed to connect to SchemeAssist AI service.';
    throw new Error(errDetail);
  }
}

/**
 * Ask a question to the SchemeAssist FastAPI RAG pipeline.
 * Delegates to chatWithSchemeAssist to ensure live OpenAI API execution.
 *
 * @param {string} question - User's query about government schemes
 * @returns {Promise<object>}
 */
export async function queryRag(question) {
  return chatWithSchemeAssist(question);
}

/**
 * SSE Progressive Streaming for RAG Query
 * Consumes /query_stream for real-time progressive word streaming.
 *
 * @param {string} question
 * @param {object} callbacks - { onMetadata, onToken, onDone, onError }
 * @returns {() => void} - Cancel/Abort function
 */
export function streamRagQuery(question, { onMetadata, onToken, onDone, onError }) {
  const cleanQuestion = (question || '').trim();
  if (!cleanQuestion || cleanQuestion.length < 3) {
    onError && onError(new Error('Question must be at least 3 characters long.'));
    return () => {};
  }

  const controller = new AbortController();

  fetch(`${API_BASE_URL}/query_stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question: cleanQuestion }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Streaming failed with status ${response.status}`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const block of parts) {
          if (!block.trim()) continue;
          const eventMatch = block.match(/event:\s*([a-zA-Z0-9_-]+)/);
          const dataMatch = block.match(/data:\s*(.+)/);
          const eventType = eventMatch ? eventMatch[1] : 'message';
          const dataStr = dataMatch ? dataMatch[1] : '';

          if (dataStr) {
            try {
              const parsed = JSON.parse(dataStr);
              if (eventType === 'metadata' && onMetadata) {
                onMetadata(parsed);
              } else if (eventType === 'token' && onToken) {
                onToken(parsed.token || '');
              } else if (eventType === 'done' && onDone) {
                onDone(parsed);
              } else if (eventType === 'error' && onError) {
                onError(new Error(parsed.error || 'Streaming error'));
              }
            } catch (e) {
              console.warn('Failed to parse SSE event JSON:', dataStr);
            }
          }
        }
      }
      onDone && onDone({ status: 'complete' });
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError && onError(err);
      }
    });

  return () => controller.abort();
}

export default {
  checkHealth,
  queryRag,
  streamRagQuery,
};
