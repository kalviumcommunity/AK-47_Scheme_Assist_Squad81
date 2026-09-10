import { useState, useEffect } from 'react';

/**
 * useMediaQuery hook to listen to window media query changes.
 * Useful for adaptive layouts, drawer state, and mobile/desktop transitions.
 *
 * @param {string} query - CSS media query string (e.g. '(min-width: 768px)')
 * @returns {boolean} - Matches state
 */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const media = window.matchMedia(query);
    const listener = (event) => setMatches(event.matches);

    setMatches(media.matches);
    media.addEventListener('change', listener);

    return () => media.removeEventListener('change', listener);
  }, [query]);

  return matches;
}

export default useMediaQuery;
