import React, { useState } from 'react';
import { SchemeManagementTable } from '../../components/admin/AdminComponents';
import { ADMIN_SCHEMES_LIST } from '../../data/adminData';

export function AdminSchemesPage() {
  const [schemes, setSchemes] = useState(ADMIN_SCHEMES_LIST);
  const handleAddScheme = () => alert('New Scheme onboarding modal — coming soon.');
  return (
    <div className="animate-fadeIn pb-10">
      <SchemeManagementTable schemes={schemes} onAddScheme={handleAddScheme} />
    </div>
  );
}
export default AdminSchemesPage;
