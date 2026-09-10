import { useState, useEffect, useCallback } from 'react';
import { getSystemHealth } from '../services/api';

/**
 * useHealthCheck hook to poll and report backend RAG service health.
 *
 * @param {number} intervalMs - Polling interval in ms (default 30000ms; pass 0 to disable polling)
 * @returns {{ health: object|null, loading: boolean, error: string|null, refetch: Function }}
 */
export function useHealthCheck(intervalMs = 30000) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkHealth = useCallback(async () => {
    try {
      const data = await getSystemHealth();
      setHealth(data);
      setError(null);
    } catch (err) {
      setError(err?.message || 'Backend unreachable');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();

    if (intervalMs > 0) {
      const interval = setInterval(checkHealth, intervalMs);
      return () => clearInterval(interval);
    }
  }, [checkHealth, intervalMs]);

  return { health, loading, error, refetch: checkHealth };
}

export default useHealthCheck;
