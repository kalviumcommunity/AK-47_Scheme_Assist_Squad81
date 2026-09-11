import React, { useState } from 'react';
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
  Plus,
  FileText,
  X,
  UploadCloud
} from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import Modal from '../ui/Modal';

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
                  className={`h-full rounded-full ${idx === 0 ? 'bg-primary' : idx === 1 ? 'bg-gov-success' : 'bg-navy-700'
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

export function SchemeManagementTable({ schemes, onAddScheme, onEditScheme, onDeleteScheme }) {
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [editScheme, setEditScheme] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newScheme, setNewScheme] = useState({
    id: '',
    name: '',
    category: 'Agriculture',
    government: 'Central Government',
    status: 'Active',
    applications: 0,
    budget: '₹0 Cr',
    documents: []
  });

  const handleView = (scheme) => setSelectedScheme({ ...scheme, documents: scheme.documents || [] });

  const handleRemoveDocument = (documentName) => {
    if (!selectedScheme) return;

    const updatedDocuments = (selectedScheme.documents || []).filter((doc) => doc !== documentName);
    const updatedScheme = { ...selectedScheme, documents: updatedDocuments };
    setSelectedScheme(updatedScheme);
    if (onEditScheme) onEditScheme(updatedScheme);
  };

  const handleSaveEdit = () => {
    if (!editScheme) return;

    const normalizedScheme = {
      ...editScheme,
      documents: (editScheme.documents || [])
        .split(',')
        .map((doc) => doc.trim())
        .filter(Boolean),
      name: editScheme.name.trim() || 'Untitled Scheme'
    };

    if (onEditScheme) onEditScheme(normalizedScheme);
    setSelectedScheme(normalizedScheme);
    setEditScheme(null);
  };

  const handleDelete = (schemeId) => {
    if (!onDeleteScheme) return;
    const scheme = schemes.find((item) => item.id === schemeId);

    if (window.confirm(`Delete ${scheme?.name || 'this scheme'}? This action cannot be undone.`)) {
      onDeleteScheme(schemeId);
      setSelectedScheme(null);
    }
  };

  const handleAdd = () => {
    const normalizedScheme = {
      ...newScheme,
      id: newScheme.id || `scheme-${Date.now()}`,
      name: newScheme.name.trim() || 'New Scheme',
      category: newScheme.category.trim() || 'General',
      government: newScheme.government.trim() || 'Central Government',
      status: newScheme.status || 'Active',
      applications: Number(newScheme.applications) || 0,
      budget: newScheme.budget.trim() || '₹0 Cr',
      documents: Array.isArray(newScheme.documents)
        ? newScheme.documents.filter(Boolean)
        : (newScheme.documents || '').split(',').map((doc) => doc.trim()).filter(Boolean)
    };

    if (onAddScheme) onAddScheme(normalizedScheme);
    setNewScheme({
      id: '',
      name: '',
      category: 'Agriculture',
      government: 'Central Government',
      status: 'Active',
      applications: 0,
      budget: '₹0 Cr',
      documents: []
    });
    setIsAddModalOpen(false);
  };

  const handleFilesSelected = (event) => {
    const files = Array.from(event.target.files || []);
    const names = files.map((file) => file.name);
    setNewScheme((prev) => ({ ...prev, documents: [...(prev.documents || []), ...names] }));
    event.target.value = '';
  };

  return (
    <>
      <Card className="mb-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-border mb-4">
          <div>
            <h3 className="text-sm font-bold text-navy">Government Welfare Schemes</h3>
            <p className="text-xs text-slate-muted">Manage active schemes and budget sanctions</p>
          </div>
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsAddModalOpen(true)}>
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
                      <button
                        className="p-1 hover:text-primary transition-colors"
                        title="View documents"
                        onClick={() => handleView(s)}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1 hover:text-navy transition-colors"
                        title="Edit"
                        onClick={() => setEditScheme({ ...s, documents: (s.documents || []).join(', ') })}
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        className="p-1 hover:text-red-600 transition-colors"
                        title="Delete"
                        onClick={() => handleDelete(s.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {isAddModalOpen && (
        <Modal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          title="Add New Scheme"
          subtitle="Create a scheme entry and attach related documents"
          maxWidth="max-w-2xl"
        >
          <div className="space-y-4">
            <div className="grid gap-4">
              <label className="space-y-1 text-xs text-slate-muted font-semibold">
                Scheme name
                <input
                  value={newScheme.name}
                  onChange={(event) => setNewScheme({ ...newScheme, name: event.target.value })}
                  className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="e.g. Digital Land Record Scheme"
                />
              </label>

              <div className="grid sm:grid-cols-2 gap-4">
                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Category
                  <input
                    value={newScheme.category}
                    onChange={(event) => setNewScheme({ ...newScheme, category: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>

                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Government
                  <input
                    value={newScheme.government}
                    onChange={(event) => setNewScheme({ ...newScheme, government: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Status
                  <select
                    value={newScheme.status}
                    onChange={(event) => setNewScheme({ ...newScheme, status: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  >
                    <option>Active</option>
                    <option>Paused</option>
                    <option>Draft</option>
                    <option>Archived</option>
                  </select>
                </label>

                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Applications
                  <input
                    type="number"
                    min="0"
                    value={newScheme.applications}
                    onChange={(event) => setNewScheme({ ...newScheme, applications: Number(event.target.value) || 0 })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>
              </div>

              <label className="space-y-1 text-xs text-slate-muted font-semibold">
                Sanction budget
                <input
                  value={newScheme.budget}
                  onChange={(event) => setNewScheme({ ...newScheme, budget: event.target.value })}
                  className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="₹25,000 Cr"
                />
              </label>

              <div className="space-y-2">
                <label className="text-xs text-slate-muted font-semibold">Related scheme documents</label>
                <label className="flex cursor-pointer items-center justify-center gap-2 rounded-card border-2 border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 hover:border-primary/50 hover:bg-primary/5">
                  <UploadCloud className="w-4 h-4 text-primary" />
                  <span>Upload files</span>
                  <input type="file" multiple className="hidden" onChange={handleFilesSelected} />
                </label>

                {newScheme.documents?.length > 0 && (
                  <div className="space-y-2">
                    {newScheme.documents.map((documentName) => (
                      <div key={documentName} className="flex items-center justify-between gap-3 rounded-card border border-slate-border bg-slate-50 p-2.5 text-xs">
                        <span className="truncate text-slate-700">{documentName}</span>
                        <button
                          type="button"
                          onClick={() => setNewScheme((prev) => ({
                            ...prev,
                            documents: prev.documents.filter((doc) => doc !== documentName)
                          }))}
                          className="text-red-500 hover:text-red-700"
                          aria-label={`Remove ${documentName}`}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setIsAddModalOpen(false)}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={handleAdd}>Save Scheme</Button>
            </div>
          </div>
        </Modal>
      )}

      {selectedScheme && (
        <Modal
          isOpen={Boolean(selectedScheme)}
          onClose={() => setSelectedScheme(null)}
          title={selectedScheme.name}
          subtitle="Scheme documents and sample records"
          maxWidth="max-w-2xl"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-50 p-3 rounded-card">
                <div className="text-slate-muted uppercase tracking-wider">Category</div>
                <div className="font-bold text-navy mt-1">{selectedScheme.category}</div>
              </div>
              <div className="bg-slate-50 p-3 rounded-card">
                <div className="text-slate-muted uppercase tracking-wider">Status</div>
                <div className="font-bold text-navy mt-1">{selectedScheme.status}</div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-bold text-navy">Sample Documents</h4>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-muted">
                  {selectedScheme.documents?.length || 0} files
                </span>
              </div>

              {(!selectedScheme.documents || selectedScheme.documents.length === 0) ? (
                <div className="border border-dashed border-slate-200 rounded-card p-4 text-center text-xs text-slate-muted">
                  No sample documents linked to this scheme.
                </div>
              ) : (
                <div className="space-y-2">
                  {selectedScheme.documents.map((documentName) => (
                    <div key={documentName} className="flex items-center justify-between gap-3 rounded-card border border-slate-border bg-slate-50 p-3">
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText className="w-4 h-4 text-primary shrink-0" />
                        <span className="text-sm text-slate-700 truncate">{documentName}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveDocument(documentName)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                        aria-label={`Remove ${documentName}`}
                        title="Remove document"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}

      {editScheme && (
        <Modal
          isOpen={Boolean(editScheme)}
          onClose={() => setEditScheme(null)}
          title="Edit Scheme"
          subtitle="Update scheme details and document list"
          maxWidth="max-w-xl"
        >
          <div className="space-y-4">
            <div className="grid gap-4">
              <label className="space-y-1 text-xs text-slate-muted font-semibold">
                Scheme name
                <input
                  value={editScheme.name}
                  onChange={(event) => setEditScheme({ ...editScheme, name: event.target.value })}
                  className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </label>

              <div className="grid sm:grid-cols-2 gap-4">
                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Category
                  <input
                    value={editScheme.category}
                    onChange={(event) => setEditScheme({ ...editScheme, category: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>

                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Government
                  <input
                    value={editScheme.government}
                    onChange={(event) => setEditScheme({ ...editScheme, government: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Status
                  <select
                    value={editScheme.status}
                    onChange={(event) => setEditScheme({ ...editScheme, status: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  >
                    <option>Active</option>
                    <option>Paused</option>
                    <option>Draft</option>
                    <option>Archived</option>
                  </select>
                </label>

                <label className="space-y-1 text-xs text-slate-muted font-semibold">
                  Budget
                  <input
                    value={editScheme.budget}
                    onChange={(event) => setEditScheme({ ...editScheme, budget: event.target.value })}
                    className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>
              </div>

              <label className="space-y-1 text-xs text-slate-muted font-semibold">
                Sample documents
                <textarea
                  value={editScheme.documents}
                  onChange={(event) => setEditScheme({ ...editScheme, documents: event.target.value })}
                  rows="4"
                  placeholder="Aadhaar Card, Income Certificate, Bank Details"
                  className="w-full border border-slate-200 rounded-btn px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </label>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" size="sm" onClick={() => setEditScheme(null)}>Cancel</Button>
              <Button variant="primary" size="sm" onClick={handleSaveEdit}>Save Changes</Button>
            </div>
          </div>
        </Modal>
      )}
    </>
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
            {citizens.length === 0 && (
              <tr>
                <td colSpan="6" className="py-10 text-center text-xs text-slate-muted">
                  No citizens have registered or logged in yet.
                </td>
              </tr>
            )}
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
                  <Badge variant={c.status === 'Verified' || c.status === 'Active' ? 'success' : 'warning'} size="sm" dot>
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
