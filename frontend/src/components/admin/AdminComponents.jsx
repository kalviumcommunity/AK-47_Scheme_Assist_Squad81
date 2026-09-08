import React from 'react';
import {
  Users,
  BookOpen,
  FileCheck,
  Clock,
  TrendingUp,
  CheckCircle,
  XCircle,
  Edit2,
  Trash2,
  Eye,
  Plus
} from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export function AdminStatsGrid({ stats }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-card bg-primary-50 text-primary border border-primary/20 flex items-center justify-center shrink-0">
          <Users className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Total Citizens</p>
          <h3 className="text-2xl font-black text-navy mt-0.5">{stats.totalCitizens.toLocaleString()}</h3>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-card bg-navy/10 text-navy border border-navy/20 flex items-center justify-center shrink-0">
          <BookOpen className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Active Schemes</p>
          <h3 className="text-2xl font-black text-navy mt-0.5">{stats.activeSchemes}</h3>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-card bg-gov-success-light text-gov-success border border-gov-success/20 flex items-center justify-center shrink-0">
          <FileCheck className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Applications Processed</p>
          <h3 className="text-2xl font-black text-navy mt-0.5">{stats.totalApplications.toLocaleString()}</h3>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-card bg-gov-warning-light text-gov-warning border border-gov-warning/20 flex items-center justify-center shrink-0">
          <Clock className="w-6 h-6" />
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Pending Reviews</p>
          <h3 className="text-2xl font-black text-navy mt-0.5">{stats.pendingReviews}</h3>
        </div>
      </Card>
    </div>
  );
}

export function AnalyticsVisual({ analytics }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Applications Growth */}
      <Card>
        <div className="flex items-center justify-between pb-3 border-b border-slate-border mb-4">
          <div>
            <h3 className="text-sm font-bold text-navy">Monthly Application Inflow</h3>
            <p className="text-xs text-slate-muted">Growth across 2026 fiscal cycle</p>
          </div>
          <Badge variant="success" size="sm">+24% vs Last Qtr</Badge>
        </div>

        <div className="h-48 flex items-end justify-between gap-3 pt-4 px-2">
          {analytics.monthlyApplications.map((m, idx) => {
            const heightPct = Math.round((m.applications / 2500) * 100);
            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                <span className="text-[10px] font-bold text-navy">{m.applications}</span>
                <div
                  style={{ height: `${heightPct}%` }}
                  className="w-full bg-primary hover:bg-primary-dark rounded-t-btn transition-all duration-300"
                />
                <span className="text-[10px] font-semibold text-slate-500">{m.month}</span>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Scheme Popularity */}
      <Card>
        <div className="flex items-center justify-between pb-3 border-b border-slate-border mb-4">
          <div>
            <h3 className="text-sm font-bold text-navy">Scheme Popularity Breakdown</h3>
            <p className="text-xs text-slate-muted">Distribution by citizen application volume</p>
          </div>
        </div>

        <div className="space-y-3.5 pt-2">
          {analytics.schemePopularity.map((s, idx) => (
            <div key={idx}>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-navy">{s.name}</span>
                <span className="text-slate-500">{s.count} ({s.percentage}%)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  style={{ width: `${s.percentage}%` }}
                  className={`h-full rounded-full ${
                    idx === 0 ? 'bg-primary' : idx === 1 ? 'bg-gov-success' : 'bg-navy-700'
                  }`}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export function SchemeManagementTable({ schemes, onAddScheme }) {
  return (
    <Card className="mb-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-border mb-4">
        <div>
          <h3 className="text-sm font-bold text-navy">Government Welfare Schemes</h3>
          <p className="text-xs text-slate-muted">Manage active schemes and budget sanctions</p>
        </div>
        <Button variant="primary" size="sm" icon={Plus} onClick={onAddScheme}>
          Add New Scheme
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-text border-collapse">
          <thead>
            <tr className="border-b border-slate-border bg-slate-bg/70 text-slate-muted font-bold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-4">Scheme Name</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Government</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Applications</th>
              <th className="py-3 px-4">Sanction Budget</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {schemes.map((s) => (
              <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                <td className="py-3 px-4 font-bold text-navy">{s.name}</td>
                <td className="py-3 px-4 text-slate-500">{s.category}</td>
                <td className="py-3 px-4 text-slate-500">{s.government}</td>
                <td className="py-3 px-4">
                  <Badge variant="success" size="sm" dot>{s.status}</Badge>
                </td>
                <td className="py-3 px-4 font-semibold text-slate-700">{s.applications.toLocaleString()}</td>
                <td className="py-3 px-4 font-mono text-slate-600">{s.budget}</td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button className="p-1 hover:text-primary transition-colors" title="View"><Eye className="w-4 h-4" /></button>
                    <button className="p-1 hover:text-navy transition-colors" title="Edit"><Edit2 className="w-4 h-4" /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function CitizenManagementTable({ citizens }) {
  return (
    <Card className="mb-6">
      <div className="pb-4 border-b border-slate-border mb-4">
        <h3 className="text-sm font-bold text-navy">Registered Citizens & Eligibility Status</h3>
        <p className="text-xs text-slate-muted">Verification records across regional jurisdictions</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-text border-collapse">
          <thead>
            <tr className="border-b border-slate-border bg-slate-bg/70 text-slate-muted font-bold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-4">Citizen Name</th>
              <th className="py-3 px-4">Location</th>
              <th className="py-3 px-4">Applications</th>
              <th className="py-3 px-4">Eligibility Category</th>
              <th className="py-3 px-4">Profile Score</th>
              <th className="py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {citizens.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                <td className="py-3 px-4">
                  <span className="font-bold text-navy block">{c.name}</span>
                  <span className="text-[10px] text-slate-400 font-mono">{c.id}</span>
                </td>
                <td className="py-3 px-4 text-slate-500">{c.location}</td>
                <td className="py-3 px-4 font-semibold text-slate-700">{c.applicationsCount}</td>
                <td className="py-3 px-4 text-slate-600">{c.eligibilityStatus}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div style={{ width: `${c.profileCompletion}%` }} className="bg-primary h-full rounded-full" />
                    </div>
                    <span className="text-[10px] font-bold text-slate-600">{c.profileCompletion}%</span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <Badge variant={c.status === 'Verified' ? 'success' : 'warning'} size="sm" dot>
                    {c.status}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function ApplicationManagementTable({ applications, onApprove, onReject }) {
  return (
    <Card>
      <div className="pb-4 border-b border-slate-border mb-4">
        <h3 className="text-sm font-bold text-navy">Application Review & Verification Queue</h3>
        <p className="text-xs text-slate-muted">Nodal approval queue for Direct Benefit Transfer sanctioning</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-text border-collapse">
          <thead>
            <tr className="border-b border-slate-border bg-slate-bg/70 text-slate-muted font-bold uppercase tracking-wider text-[10px]">
              <th className="py-3 px-4">App ID</th>
              <th className="py-3 px-4">Citizen</th>
              <th className="py-3 px-4">Applied Scheme</th>
              <th className="py-3 px-4">State</th>
              <th className="py-3 px-4">Submitted</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Review Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {applications.map((app) => (
              <tr key={app.id} className="hover:bg-slate-50 transition-colors">
                <td className="py-3 px-4 font-mono font-bold text-navy">{app.id}</td>
                <td className="py-3 px-4 font-semibold text-slate-700">{app.citizenName}</td>
                <td className="py-3 px-4 text-slate-600">{app.scheme}</td>
                <td className="py-3 px-4 text-slate-500">{app.state}</td>
                <td className="py-3 px-4 text-slate-500">{app.submittedDate}</td>
                <td className="py-3 px-4">
                  <Badge
                    variant={
                      app.status === 'Approved'
                        ? 'success'
                        : app.status === 'Pending'
                        ? 'warning'
                        : app.status === 'Rejected'
                        ? 'danger'
                        : 'primary'
                    }
                    size="sm"
                    dot
                  >
                    {app.status}
                  </Badge>
                </td>
                <td className="py-3 px-4 text-right">
                  {app.status === 'Pending' || app.status === 'Under Review' ? (
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="success"
                        size="sm"
                        icon={CheckCircle}
                        onClick={() => onApprove(app.id)}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        icon={XCircle}
                        onClick={() => onReject(app.id)}
                      >
                        Reject
                      </Button>
                    </div>
                  ) : (
                    <span className="text-[11px] text-slate-400 font-medium">Decided</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
