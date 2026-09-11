import React, { useEffect, useState } from 'react';
import { CitizenManagementTable } from '../../components/admin/AdminComponents';
import { getRegisteredCitizens } from '../../context/AuthContext';
import { getAllApplications } from '../../services/applicationService';

export function AdminCitizensPage() {
  const [citizens, setCitizens] = useState([]);

  const loadCitizens = async () => {
    const users = getRegisteredCitizens();
    const applications = await getAllApplications();
    setCitizens(users.map((user) => {
      const userApplications = applications.filter((application) => application.citizenId === user.id || application.citizenEmail === user.email);
      return {
        id: user.id || user.email,
        name: user.name || 'Citizen',
        location: user.state || 'Not provided',
        applicationsCount: userApplications.length,
        eligibilityStatus: userApplications.length ? 'Application activity recorded' : 'Profile registered',
        profileCompletion: user.profileCompletion || 0,
        status: 'Active',
      };
    }));
  };

  useEffect(() => {
    loadCitizens();
    const refresh = () => loadCitizens();
    window.addEventListener('storage', refresh);
    const interval = setInterval(refresh, 5000);
    return () => { window.removeEventListener('storage', refresh); clearInterval(interval); };
  }, []);

  return (
    <div className="animate-fadeIn pb-10">
      <CitizenManagementTable citizens={citizens} />
    </div>
  );
}
export default AdminCitizensPage;
