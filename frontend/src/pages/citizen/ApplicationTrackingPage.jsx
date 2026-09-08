import React, { useState } from 'react';
import {
  FileCheck2,
  CheckCircle2,
  Clock,
  AlertCircle,
  Eye,
  Check,
  ChevronRight,
  Sparkles,
  ArrowUpRight
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import { MOCK_APPLICATIONS } from '../../data/mockCitizenData';

export function ApplicationTrackingPage() {
  const [applications, setApplications] = useState(MOCK_APPLICATIONS);
  const [selectedApp, setSelectedApp] = useState(null);

  const totalCount = applications.length;
  const approvedCount = applications.filter((a) => a.status === 'Approved').length;
  const inProgressCount = applications.filter((a) => a.status === 'In Progress' || a.status === 'Under Review').length;
  const pendingCount = applications.filter((a) => a.status === 'Pending').length;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Approved':
        return <Badge variant="success" size="sm" dot>Approved</Badge>;
      case 'Under Review':
      case 'In Progress':
        return <Badge variant="primary" size="sm" dot>{status}</Badge>;
      case 'Rejected':
        return <Badge variant="danger" size="sm" dot>Rejected</Badge>;
      default:
        return <Badge variant="warning" size="sm" dot>Pending</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
          My Applications
        </h1>
        <p className="text-xs sm:text-sm text-slate-muted mt-1">
          Track official sanctions, verification stages, and direct benefit disbursement.
        </p>
      </div>

      {/* Summary Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-card bg-navy/10 text-navy border border-navy/20 flex items-center justify-center shrink-0">
            <FileCheck2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-muted uppercase">Total Applied</p>
            <h3 className="text-xl font-black text-navy">{totalCount}</h3>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-card bg-gov-success-light text-gov-success border border-gov-success/20 flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-muted uppercase">Approved</p>
            <h3 className="text-xl font-black text-gov-success">{approvedCount}</h3>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-card bg-primary-50 text-primary border border-primary/20 flex items-center justify-center shrink-0">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-muted uppercase">In Progress</p>
            <h3 className="text-xl font-black text-primary">{inProgressCount}</h3>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-card bg-gov-warning-light text-gov-warning border border-gov-warning/20 flex items-center justify-center shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold text-slate-muted uppercase">Pending</p>
            <h3 className="text-xl font-black text-gov-warning">{pendingCount}</h3>
          </div>
        </Card>
      </div>

      {/* Applications List Table */}
      <Card>
        <div className="pb-4 border-b border-slate-border mb-4">
          <h2 className="text-base font-bold text-navy">Application Registry</h2>
          <p className="text-xs text-slate-muted">All government schemes you have submitted applications for</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-text border-collapse">
            <thead>
              <tr className="border-b border-slate-border bg-slate-bg/70 text-slate-muted font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Scheme</th>
                <th className="py-3 px-4">Application ID</th>
                <th className="py-3 px-4">Sanction Benefit</th>
                <th className="py-3 px-4">Submission Date</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {applications.map((app) => (
                <tr key={app.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-4 px-4">
                    <span className="font-bold text-navy block">{app.schemeName}</span>
                    <span className="text-[10px] text-slate-400">{app.category}</span>
                  </td>
                  <td className="py-4 px-4 font-mono font-bold text-slate-700">{app.id}</td>
                  <td className="py-4 px-4 font-bold text-primary">{app.benefit}</td>
                  <td className="py-4 px-4 text-slate-500">{app.submittedDate}</td>
                  <td className="py-4 px-4">{getStatusBadge(app.status)}</td>
                  <td className="py-4 px-4 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      icon={Eye}
                      onClick={() => setSelectedApp(app)}
                    >
                      Track Timeline
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Application Timeline Details Modal */}
      {selectedApp && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedApp(null)}
          title={`Application Details: ${selectedApp.id}`}
          subtitle={`${selectedApp.schemeName} (${selectedApp.benefit})`}
        >
          <div className="space-y-6">
            <div className="flex items-center justify-between p-3.5 rounded-btn bg-slate-bg border border-slate-border text-xs">
              <div>
                <span className="text-slate-muted block">Current Status:</span>
                <span className="font-bold text-navy text-sm">{selectedApp.status}</span>
              </div>
              <div>{getStatusBadge(selectedApp.status)}</div>
            </div>

            {/* Vertical Timeline */}
            <div>
              <h4 className="text-xs font-bold text-navy uppercase tracking-wider mb-4">
                Disbursal & Verification Stages
              </h4>
              <div className="space-y-4 relative pl-4 border-l-2 border-slate-200">
                {selectedApp.timeline.map((stage, idx) => (
                  <div key={idx} className="relative group">
                    <span
                      className={`absolute -left-[23px] top-0 w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-bold text-white ring-4 ring-white ${
                        stage.done ? 'bg-gov-success' : 'bg-slate-300'
                      }`}
                    >
                      {stage.done ? '✓' : idx + 1}
                    </span>
                    <div className="text-xs">
                      <p className={`font-bold ${stage.done ? 'text-navy' : 'text-slate-400'}`}>
                        {stage.step}
                      </p>
                      <p className="text-[11px] text-slate-muted">{stage.date}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-border">
              <Button variant="primary" size="sm" onClick={() => setSelectedApp(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

export default ApplicationTrackingPage;
