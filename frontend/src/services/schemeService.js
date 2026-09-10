/**
 * schemeService.js - Scheme Discovery, Retrieval, and Filtering Service
 * Cleanly separates real backend API readiness from local demo fallback data.
 */
import apiClient from './api';
import { SCHEMES, SCHEME_CATEGORIES, GOVERNMENT_TYPES } from '../data/demoSchemes';

/**
 * Fetch all welfare schemes.
 * Attempts backend /api/schemes first; falls back gracefully to demo data.
 *
 * @param {object} [params] - { category, governmentType, search, eligibility }
 * @returns {Promise<Array<object>>}
 */
export async function getSchemes(params = {}) {
  try {
    const response = await apiClient.get('/schemes', { params });
    if (Array.isArray(response.data) && response.data.length > 0) {
      return response.data;
    }
  } catch (error) {
    // Expected during UI development when /schemes is served locally
  }

  // Local fallback with filtering
  let results = [...SCHEMES];

  if (params.category && params.category !== 'All Categories') {
    results = results.filter((s) => s.category.toLowerCase() === params.category.toLowerCase());
  }

  if (params.governmentType && params.governmentType !== 'All Governments') {
    results = results.filter((s) => s.governmentType.toLowerCase() === params.governmentType.toLowerCase());
  }

  if (params.search) {
    const query = params.search.toLowerCase();
    results = results.filter(
      (s) =>
        s.name.toLowerCase().includes(query) ||
        s.fullName?.toLowerCase().includes(query) ||
        s.description?.toLowerCase().includes(query) ||
        s.category?.toLowerCase().includes(query)
    );
  }

  return results;
}

/**
 * Fetch a single scheme by its ID.
 *
 * @param {string} schemeId
 * @returns {Promise<object|null>}
 */
export async function getSchemeById(schemeId) {
  try {
    const response = await apiClient.get(`/schemes/${schemeId}`);
    if (response.data) return response.data;
  } catch (error) {
    // Fallback to demo dataset
  }

  const found = SCHEMES.find((s) => s.id === schemeId);
  return found || null;
}

/**
 * Get available scheme categories.
 */
export function getSchemeCategories() {
  return SCHEME_CATEGORIES;
}

/**
 * Get available government types.
 */
export function getGovernmentTypes() {
  return GOVERNMENT_TYPES;
}

export default {
  getSchemes,
  getSchemeById,
  getSchemeCategories,
  getGovernmentTypes,
};
