import React, { useEffect, useState } from 'react';
import { ApplicationManagementTable } from '../../components/admin/AdminComponents';
import { getAllApplications, updateApplicationStatus } from '../../services/applicationService';

export function AdminApplicationsPage() {
  const [applications, setApplications] = useState([]);

  const loadApplications = async () => setApplications(await getAllApplications());
  useEffect(() => {
    loadApplications();
    const refresh = () => loadApplications();
    window.addEventListener('storage', refresh);
    const interval = setInterval(refresh, 3000);
    return () => { window.removeEventListener('storage', refresh); clearInterval(interval); };
  }, []);

  const handleApprove = async (id) => { await updateApplicationStatus(id, 'Approved'); await loadApplications(); };
  const handleReject = async (id) => { await updateApplicationStatus(id, 'Rejected'); await loadApplications(); };
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
