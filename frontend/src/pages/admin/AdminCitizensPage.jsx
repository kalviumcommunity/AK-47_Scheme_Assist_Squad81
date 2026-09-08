import React from 'react';
import { CitizenManagementTable } from '../../components/admin/AdminComponents';
import { ADMIN_CITIZENS_LIST } from '../../data/adminData';

export function AdminCitizensPage() {
  return (
    <div className="animate-fadeIn pb-10">
      <CitizenManagementTable citizens={ADMIN_CITIZENS_LIST} />
    </div>
  );
}
export default AdminCitizensPage;
