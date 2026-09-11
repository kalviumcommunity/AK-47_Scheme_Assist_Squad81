const STORAGE_KEY = 'schemeassist_activity_logs';

function readLogs() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch {
        return [];
    }
}

function writeLogs(logs) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(logs.slice(0, 500)));
    window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
}

export function recordActivity({ level = 'INFO', source = 'SYSTEM', message, details = '' }) {
    const entry = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        level,
        source,
        message,
        details,
        timestamp: new Date().toISOString(),
    };
    writeLogs([entry, ...readLogs()]);
    return entry;
}

export function getActivityLogs() {
    return readLogs();
}

export function clearActivityLogs() {
    writeLogs([]);
}

export default { recordActivity, getActivityLogs, clearActivityLogs };
