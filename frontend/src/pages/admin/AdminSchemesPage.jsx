import React, { useState, useEffect } from 'react';
import { SchemeManagementTable } from '../../components/admin/AdminComponents';
import { SCHEMES } from '../../data/schemesData';
import { getAllApplications } from '../../services/applicationService';

const STORAGE_KEY = 'schemeassist_admin_schemes';

export function AdminSchemesPage() {
  const [schemes, setSchemes] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        // Clean out legacy mock applications count if from demoAdmin
        return parsed.map((s) => ({
          ...s,
          applications: typeof s.applications === 'number' ? s.applications : 0,
        }));
      }
    } catch {
      // ignore
    }
    return SCHEMES.map((s) => ({
      id: s.id,
      name: s.name,
      category: s.category || 'General',
      government: s.governmentType || 'Central Government',
      status: 'Active',
      applications: 0,
      budget: s.budget || '₹10,000 Cr',
      documents: s.documentsRequired || ['Aadhaar Card'],
      lastUpdated: new Date().toISOString().split('T')[0],
    }));
  });

  const syncApplicationCounts = async () => {
    const apps = await getAllApplications();
    setSchemes((prev) =>
      prev.map((s) => {
        const count = apps.filter(
          (a) => a.schemeId === s.id || a.schemeName === s.name || a.scheme === s.name
        ).length;
        return { ...s, applications: count };
      })
    );
  };

  useEffect(() => {
    syncApplicationCounts();
    window.addEventListener('storage', syncApplicationCounts);
    const interval = setInterval(syncApplicationCounts, 3000);
    return () => {
      window.removeEventListener('storage', syncApplicationCounts);
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(schemes));
  }, [schemes]);

  const handleAddScheme = (newScheme) => {
    setSchemes((prev) => [
      {
        id: newScheme.id || `scheme-${Date.now()}`,
        name: newScheme.name,
        category: newScheme.category,
        government: newScheme.government,
        status: newScheme.status,
        applications: Number(newScheme.applications || 0),
        budget: newScheme.budget,
        documents: newScheme.documents || [],
        lastUpdated: new Date().toISOString().split('T')[0]
      },
      ...prev
    ]);
  };

  const handleEditScheme = (updatedScheme) => {
    setSchemes((prev) =>
      prev.map((scheme) => (scheme.id === updatedScheme.id ? updatedScheme : scheme))
    );
  };

  const handleDeleteScheme = (schemeId) => {
    setSchemes((prev) => prev.filter((scheme) => scheme.id !== schemeId));
  };

  return (
    <div className="animate-fadeIn pb-10">
      <SchemeManagementTable
        schemes={schemes}
        onAddScheme={handleAddScheme}
        onEditScheme={handleEditScheme}
        onDeleteScheme={handleDeleteScheme}
      />
    </div>
  );
}
export default AdminSchemesPage;
