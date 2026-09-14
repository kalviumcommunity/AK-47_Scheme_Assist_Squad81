import React, { useEffect, useState } from 'react';
import { CitizenManagementTable } from '../../components/admin/AdminComponents';
import { getRegisteredCitizens } from '../../context/AuthContext';
import { getAllApplications } from '../../services/applicationService';

export function AdminCitizensPage() {
  const [citizens, setCitizens] = useState([]);

  const loadCitizens = async () => {
    const users = getRegisteredCitizens();
    const applications = await getAllApplications();

    // Map existing users
    const map = new Map();
    users.forEach((u) => {
      const key = (u.email || u.id || '').toLowerCase();
      if (key) map.set(key, u);
    });

    // Also include any citizens found in submitted applications
    applications.forEach((app) => {
      const key = (app.citizenEmail || app.citizenId || app.citizenName || '').toLowerCase();
      if (key && !map.has(key)) {
        map.set(key, {
          id: app.citizenId || `CIT-${Math.floor(100000 + Math.random() * 900000)}`,
          name: app.citizenName || 'Citizen',
          email: app.citizenEmail || '',
          state: app.state || 'Not provided',
          phone: app.phone || '',
          role: 'citizen',
          status: 'Active',
        });
      }
    });

    const citizenList = Array.from(map.values()).map((user) => {
      const userApplications = applications.filter(
        (app) =>
          (user.id && app.citizenId === user.id) ||
          (user.email && app.citizenEmail?.toLowerCase() === user.email.toLowerCase()) ||
          (user.name && app.citizenName?.toLowerCase() === user.name.toLowerCase())
      );

      // Score profile completion based on provided fields
      let score = 50;
      if (user.name && user.name !== 'Citizen') score += 15;
      if (user.phone) score += 15;
      if (user.state && user.state !== 'Not provided') score += 10;
      if (userApplications.length > 0) score += 10;

      return {
        id: user.id || user.email || `CIT-${Date.now().toString().slice(-6)}`,
        name: user.name || (user.email ? user.email.split('@')[0] : 'Citizen'),
        location: user.state || 'Not provided',
        applicationsCount: userApplications.length,
        eligibilityStatus: userApplications.length
          ? `${userApplications.length} Application${userApplications.length > 1 ? 's' : ''} Submitted`
          : 'Profile Registered',
        profileCompletion: user.profileCompletion || Math.min(score, 100),
        status: user.status || 'Active',
      };
    });

    setCitizens(citizenList);
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
