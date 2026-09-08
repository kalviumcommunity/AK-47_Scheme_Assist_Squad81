import React, { useState } from 'react';
import {
  AdminStatsGrid, AnalyticsVisual, ApplicationManagementTable
} from '../../components/admin/AdminComponents';
import {
  ADMIN_STATS, ADMIN_ANALYTICS, ADMIN_APPLICATIONS_LIST
} from '../../data/adminData';
import {
  Users, BookOpen, FileCheck2, TrendingUp, IndianRupee,
  Clock, ArrowUpRight, Activity, CheckCircle2, AlertCircle
} from 'lucide-react';

const STAT_CARDS = [
  {
    label: 'Total Citizens', value: '10,245', delta: '+128 this week',
    icon: Users, color: 'bg-blue-600', light: 'bg-blue-50', text: 'text-blue-700'
  },
  {
    label: 'Active Schemes', value: '450', delta: '+3 new this month',
    icon: BookOpen, color: 'bg-emerald-600', light: 'bg-emerald-50', text: 'text-emerald-700'
  },
  {
    label: 'Pending Applications', value: '324', delta: '18 urgent',
    icon: FileCheck2, color: 'bg-amber-500', light: 'bg-amber-50', text: 'text-amber-700'
  },
  {
    label: 'Benefits Disbursed', value: '₹18.4 Cr', delta: '↑ 12% vs last month',
    icon: IndianRupee, color: 'bg-violet-600', light: 'bg-violet-50', text: 'text-violet-700'
  },
];

export function AdminOverviewPage() {
  const [applications, setApplications] = useState(ADMIN_APPLICATIONS_LIST);

  const handleApprove = (id) =>
    setApplications((prev) => prev.map((a) => a.id === id ? { ...a, status: 'Approved' } : a));
  const handleReject = (id) =>
    setApplications((prev) => prev.map((a) => a.id === id ? { ...a, status: 'Rejected' } : a));

  return (
    <div className="space-y-6 animate-fadeIn pb-10">
      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {STAT_CARDS.map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl ${s.light} flex items-center justify-center`}>
                <s.icon className={`w-5 h-5 ${s.text}`} />
              </div>
              <ArrowUpRight className="w-4 h-4 text-slate-400" />
            </div>
            <p className="text-2xl font-black text-[#0F2B46]">{s.value}</p>
            <p className="text-xs font-semibold text-slate-600 mt-0.5">{s.label}</p>
            <p className="text-[10px] text-slate-400 mt-1">{s.delta}</p>
          </div>
        ))}
      </div>

      {/* Analytics */}
      <AnalyticsVisual analytics={ADMIN_ANALYTICS} />

      {/* Recent Applications Queue */}
      <ApplicationManagementTable
        applications={applications}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    </div>
  );
}

export default AdminOverviewPage;
