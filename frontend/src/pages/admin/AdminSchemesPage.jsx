import React, { useState, useEffect } from 'react';
import { SchemeManagementTable } from '../../components/admin/AdminComponents';
import { ADMIN_SCHEMES_LIST } from '../../data/adminData';

const STORAGE_KEY = 'schemeassist_admin_schemes';

export function AdminSchemesPage() {
  const [schemes, setSchemes] = useState(() => {
    const savedSchemes = localStorage.getItem(STORAGE_KEY);
    return savedSchemes ? JSON.parse(savedSchemes) : ADMIN_SCHEMES_LIST;
  });

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
