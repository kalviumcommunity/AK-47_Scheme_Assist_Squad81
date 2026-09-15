/**
 * sharedStoreService.js
 * Centralized service to synchronize citizens and applications between the server
 * and localStorage, enabling real-time cross-browser, cross-device, and multi-admin visibility.
 */

const CITIZENS_ENDPOINT = '/api-shared/citizens';
const APPLICATIONS_ENDPOINT = '/api-shared/applications';
const LOCAL_USERS_KEY = 'schemeassist_users_db';
const LOCAL_APPS_KEY = 'schemeassist_local_applications';

// ─── CITIZENS ─────────────────────────────────────────────────────────────

export async function fetchSharedCitizens() {
  let serverCitizens = [];
  try {
    const res = await fetch(CITIZENS_ENDPOINT, { cache: 'no-store' });
    if (res.ok) {
      serverCitizens = await res.json();
    }
  } catch (err) {
    // Network or server fallback
  }

  // Also read local citizens
  let localCitizens = [];
  try {
    const raw = localStorage.getItem(LOCAL_USERS_KEY);
    const db = raw ? JSON.parse(raw) : {};
    localCitizens = Object.values(db).filter(
      (u) => u && u.role === 'citizen' && u.email !== 'rajesh.kumar@example.com' && u.id !== 'CIT-784920'
    );
  } catch (e) {
    // ignore
  }

  // Merge server and local citizens
  const map = new Map();

  // Add server citizens first
  serverCitizens.forEach((c) => {
    const key = (c.email || c.id || c.name || '').toLowerCase().trim();
    if (key && c.role === 'citizen') {
      map.set(key, c);
    }
  });

  // Merge any local citizens that might not have reached server yet
  localCitizens.forEach((c) => {
    const key = (c.email || c.id || c.name || '').toLowerCase().trim();
    if (key && !map.has(key)) {
      map.set(key, c);
      // Asynchronously upload local citizen to server
      registerSharedCitizen(c).catch(() => {});
    }
  });

  const merged = Array.from(map.values());

  // Keep local storage synchronized
  try {
    const currentRaw = localStorage.getItem(LOCAL_USERS_KEY);
    const currentDb = currentRaw ? JSON.parse(currentRaw) : {};
    merged.forEach((c) => {
      const key = (c.email || c.id).toLowerCase();
      if (key) currentDb[key] = { ...currentDb[key], ...c };
    });
    localStorage.setItem(LOCAL_USERS_KEY, JSON.stringify(currentDb));
  } catch {
    // ignore
  }

  return merged;
}

export async function registerSharedCitizen(citizen) {
  if (!citizen) return;
  try {
    await fetch(CITIZENS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(citizen),
    });
  } catch (err) {
    // Silently continue; localStorage already retains it
  }
}

// ─── APPLICATIONS ─────────────────────────────────────────────────────────

export async function fetchSharedApplications() {
  let serverApps = [];
  try {
    const res = await fetch(APPLICATIONS_ENDPOINT, { cache: 'no-store' });
    if (res.ok) {
      serverApps = await res.json();
    }
  } catch (err) {
    // Fallback to local
  }

  let localApps = [];
  try {
    const raw = localStorage.getItem(LOCAL_APPS_KEY);
    localApps = raw ? JSON.parse(raw) : [];
  } catch {
    // ignore
  }

  const map = new Map();

  // Server apps
  serverApps.forEach((a) => {
    if (a && a.id) map.set(a.id, a);
  });

  // Local apps not yet synced to server
  localApps.forEach((a) => {
    if (a && a.id && !map.has(a.id)) {
      map.set(a.id, a);
      saveSharedApplication(a).catch(() => {});
    }
  });

  const merged = Array.from(map.values());

  // Keep local storage synchronized
  try {
    localStorage.setItem(LOCAL_APPS_KEY, JSON.stringify(merged));
  } catch {
    // ignore
  }

  return merged;
}

export async function saveSharedApplication(application) {
  if (!application) return;
  try {
    await fetch(APPLICATIONS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(application),
    });
  } catch (err) {
    // Fallback handled in applicationService
  }
}

export async function updateSharedApplicationStatus(applicationId, status) {
  try {
    const res = await fetch(`${APPLICATIONS_ENDPOINT}/${applicationId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.application;
    }
  } catch (err) {
    // Fallback
  }
  return null;
}
