import { useState, useEffect } from 'react';

/**
 * useDebounce hook to delay updating value until after a specified delay.
 * Ideal for search bars, query inputs, and reactive filters.
 *
 * @param {any} value - The input value to debounce
 * @param {number} delay - Delay in milliseconds (default 300ms)
 * @returns {any} - The debounced value
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;
