import React, { useState } from 'react';
import { ApplicationManagementTable } from '../../components/admin/AdminComponents';
import { ADMIN_APPLICATIONS_LIST } from '../../data/adminData';

export function AdminApplicationsPage() {
  const [applications, setApplications] = useState(ADMIN_APPLICATIONS_LIST);
  const handleApprove = (id) =>
    setApplications((prev) => prev.map((a) => a.id === id ? { ...a, status: 'Approved' } : a));
  const handleReject = (id) =>
    setApplications((prev) => prev.map((a) => a.id === id ? { ...a, status: 'Rejected' } : a));
  return (
    <div className="animate-fadeIn pb-10">
      <ApplicationManagementTable
        applications={applications}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    </div>
  );
}
export default AdminApplicationsPage;
