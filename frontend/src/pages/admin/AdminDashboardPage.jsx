import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/ui/Button';
import { Tabs } from '../../components/ui/Avatar';
import {
  AdminStatsGrid,
  AnalyticsVisual,
  SchemeManagementTable,
  CitizenManagementTable,
  ApplicationManagementTable
} from '../../components/admin/AdminComponents';
import { getAllApplications, updateApplicationStatus } from '../../services/applicationService';
import { getRegisteredCitizens } from '../../context/AuthContext';
import { SCHEMES } from '../../data/schemesData';
import { recordActivity } from '../../services/activityLogService';

const SCHEME_STORAGE_KEY = 'schemeassist_admin_schemes';

export function AdminDashboardPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [applications, setApplications] = useState([]);
  const [citizens, setCitizens] = useState([]);
  const [schemes, setSchemes] = useState(() => {
    try {
      const saved = localStorage.getItem(SCHEME_STORAGE_KEY);
      if (saved) return JSON.parse(saved);
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
      lastUpdated: new Date().toISOString().split('T')[0]
    }));
  });

  const loadData = useCallback(async () => {
    const apps = await getAllApplications();
    setApplications(apps);

    // Load registered citizens and merge any who submitted applications
    const users = getRegisteredCitizens();
    const citizenMap = new Map();
    users.forEach((u) => {
      const key = (u.email || u.id || '').toLowerCase();
      if (key) citizenMap.set(key, u);
    });

    apps.forEach((app) => {
      const key = (app.citizenEmail || app.citizenId || app.citizenName || '').toLowerCase();
      if (key && !citizenMap.has(key)) {
        citizenMap.set(key, {
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

    const citizenList = Array.from(citizenMap.values()).map((user) => {
      const userApps = apps.filter(
        (app) =>
          (user.id && app.citizenId === user.id) ||
          (user.email && app.citizenEmail?.toLowerCase() === user.email.toLowerCase()) ||
          (user.name && app.citizenName?.toLowerCase() === user.name.toLowerCase())
      );

      let score = 50;
      if (user.name && user.name !== 'Citizen') score += 15;
      if (user.phone) score += 15;
      if (user.state && user.state !== 'Not provided') score += 10;
      if (userApps.length > 0) score += 10;

      return {
        id: user.id || user.email || `CIT-${Date.now().toString().slice(-6)}`,
        name: user.name || (user.email ? user.email.split('@')[0] : 'Citizen'),
        location: user.state || 'Not provided',
        applicationsCount: userApps.length,
        eligibilityStatus: userApps.length
          ? `${userApps.length} Application${userApps.length > 1 ? 's' : ''} Submitted`
          : 'Profile Registered',
        profileCompletion: user.profileCompletion || Math.min(score, 100),
        status: user.status || 'Active',
      };
    });
    setCitizens(citizenList);

    // Sync scheme application counts
    setSchemes((prev) =>
      prev.map((s) => {
        const count = apps.filter(
          (a) => a.schemeId === s.id || a.schemeName === s.name || a.scheme === s.name
        ).length;
        return { ...s, applications: count };
      })
    );
  }, []);

  useEffect(() => {
    loadData();
    window.addEventListener('storage', loadData);
    const interval = setInterval(loadData, 3000);
    return () => {
      window.removeEventListener('storage', loadData);
      clearInterval(interval);
    };
  }, [loadData]);

  useEffect(() => {
    localStorage.setItem(SCHEME_STORAGE_KEY, JSON.stringify(schemes));
  }, [schemes]);

  const tabs = [
    { id: 'overview', label: 'Executive Overview' },
    { id: 'schemes', label: 'Scheme Management' },
    { id: 'citizens', label: 'Citizen Registry', count: citizens.length },
    {
      id: 'applications',
      label: 'Application Queue',
      count: applications.filter((a) => a.status === 'Pending' || a.status === 'Under Review').length
    },
  ];

  const handleApprove = async (id) => {
    await updateApplicationStatus(id, 'Approved');
    recordActivity({
      level: 'SUCCESS',
      source: 'APP',
      message: `Application ${id} approved by nodal officer`,
      details: `Status set to Approved`,
    });
    await loadData();
  };

  const handleReject = async (id) => {
    await updateApplicationStatus(id, 'Rejected');
    recordActivity({
      level: 'WARN',
      source: 'APP',
      message: `Application ${id} rejected by nodal officer`,
      details: `Status set to Rejected`,
    });
    await loadData();
  };

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

  // Derive live statistics
  const liveStats = {
    totalCitizens: citizens.length,
    activeSchemes: schemes.filter((s) => s.status === 'Active' || !s.status).length,
    totalApplications: applications.length,
    pendingReviews: applications.filter(
      (a) => a.status === 'Pending' || a.status === 'Under Review'
    ).length
  };

  // Derive live analytics
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const now = new Date();
  const months = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push({
      key: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      month: monthNames[d.getMonth()],
      applications: 0,
      approved: 0,
    });
  }

  applications.forEach((app) => {
    const dateStr = app.submittedDate || '';
    const prefix = dateStr.slice(0, 7);
    const target = months.find((m) => m.key === prefix);
    if (target) {
      target.applications += 1;
      if (app.status === 'Approved') target.approved += 1;
    } else if (months.length > 0) {
      months[months.length - 1].applications += 1;
      if (app.status === 'Approved') months[months.length - 1].approved += 1;
    }
  });

  const countsByScheme = {};
  applications.forEach((app) => {
    const name = app.schemeName || app.scheme || 'General Scheme';
    countsByScheme[name] = (countsByScheme[name] || 0) + 1;
  });

  const totalApps = applications.length;
  const liveSchemePopularity = Object.entries(countsByScheme)
    .map(([name, count]) => ({
      name,
      count,
      percentage: totalApps > 0 ? Math.round((count / totalApps) * 100) : 0,
    }))
    .sort((a, b) => b.count - a.count);

  const liveAnalytics = {
    monthlyApplications: months,
    schemePopularity: liveSchemePopularity,
    growthBadge: applications.length > 0 ? `${applications.length} Total Submissions` : 'Real-time Inflow',
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-3 border-b border-slate-border">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-gov-warning animate-pulse" />
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Nodal Administrative Operations
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight mt-0.5">
            Admin Command Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-muted">
            National Welfare Disbursement, Citizen Verification, and Scheme Lifecycle Management
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/dashboard')}
          >
            Switch to Citizen View
          </Button>
        </div>
      </div>

      {/* Admin Summary 4-Stats Grid */}
      <AdminStatsGrid stats={liveStats} />

      {/* Tabs */}
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <AnalyticsVisual analytics={liveAnalytics} />
          <ApplicationManagementTable
            applications={applications}
            onApprove={handleApprove}
            onReject={handleReject}
          />
        </div>
      )}

      {activeTab === 'schemes' && (
        <SchemeManagementTable
          schemes={schemes}
          onAddScheme={handleAddScheme}
          onEditScheme={handleEditScheme}
          onDeleteScheme={handleDeleteScheme}
        />
      )}

      {activeTab === 'citizens' && (
        <CitizenManagementTable
          citizens={citizens}
        />
      )}

      {activeTab === 'applications' && (
        <ApplicationManagementTable
          applications={applications}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  );
}

export default AdminDashboardPage;
