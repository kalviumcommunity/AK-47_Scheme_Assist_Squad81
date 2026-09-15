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
    const interval = setInterval(refresh, 2000);
    return () => { window.removeEventListener('storage', refresh); clearInterval(interval); };
  }, []);

  const handleVerify = async (id) => { await updateApplicationStatus(id, 'Verified'); await loadApplications(); };
  const handleApprove = async (id) => { await updateApplicationStatus(id, 'Approved'); await loadApplications(); };
  const handleReject = async (id) => { await updateApplicationStatus(id, 'Rejected'); await loadApplications(); };
  return (
    <div className="animate-fadeIn pb-10">
      <ApplicationManagementTable
        applications={applications}
        onVerify={handleVerify}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    </div>
  );
}
export default AdminApplicationsPage;
