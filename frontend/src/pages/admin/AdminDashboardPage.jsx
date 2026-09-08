import React, { useState } from 'react';
import {
  ShieldAlert,
  Users,
  BookOpen,
  FileCheck,
  Clock,
  Plus,
  Search,
  Filter,
  ArrowLeft
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { Tabs } from '../../components/ui/Avatar';
import {
  AdminStatsGrid,
  AnalyticsVisual,
  SchemeManagementTable,
  CitizenManagementTable,
  ApplicationManagementTable
} from '../../components/admin/AdminComponents';
import {
  ADMIN_STATS,
  ADMIN_ANALYTICS,
  ADMIN_SCHEMES_LIST,
  ADMIN_CITIZENS_LIST,
  ADMIN_APPLICATIONS_LIST
} from '../../data/adminData';

export function AdminDashboardPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [applications, setApplications] = useState(ADMIN_APPLICATIONS_LIST);
  const [schemes, setSchemes] = useState(ADMIN_SCHEMES_LIST);

  const tabs = [
    { id: 'overview', label: 'Executive Overview' },
    { id: 'schemes', label: 'Scheme Management' },
    { id: 'citizens', label: 'Citizen Registry' },
    { id: 'applications', label: 'Application Queue', count: applications.filter(a => a.status === 'Pending').length },
  ];

  const handleApprove = (id) => {
    setApplications((prev) =>
      prev.map((app) => (app.id === id ? { ...app, status: 'Approved' } : app))
    );
  };

  const handleReject = (id) => {
    setApplications((prev) =>
      prev.map((app) => (app.id === id ? { ...app, status: 'Rejected' } : app))
    );
  };

  const handleAddScheme = () => {
    alert("New Scheme onboarding modal initialized.");
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
      <AdminStatsGrid stats={ADMIN_STATS} />

      {/* Tabs */}
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <AnalyticsVisual analytics={ADMIN_ANALYTICS} />
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
        />
      )}

      {activeTab === 'citizens' && (
        <CitizenManagementTable
          citizens={ADMIN_CITIZENS_LIST}
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
