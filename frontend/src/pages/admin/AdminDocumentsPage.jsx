import React, { useState } from 'react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import { FolderOpen, FileCheck2, Search, Filter, Download, Eye, AlertCircle, CheckCircle } from 'lucide-react';

const MOCK_DOCS = [
  { id: 'DOC-101', citizen: 'Ramesh Kumar Sharma', name: 'Aadhaar Card', scheme: 'PM Vishwakarma', status: 'Verified', date: '2026-09-06', size: '1.8 MB' },
  { id: 'DOC-102', citizen: 'Sunita Devi Verma', name: 'Income Certificate', scheme: 'Ayushman Bharat', status: 'Verified', date: '2026-09-05', size: '2.4 MB' },
  { id: 'DOC-103', citizen: 'Anil Chandra Gowda', name: 'Land Record (RoR)', scheme: 'PM-KISAN', status: 'Verified', date: '2026-09-04', size: '3.1 MB' },
  { id: 'DOC-104', citizen: 'Meenakshi Sundaram', name: 'BPL Ration Card', scheme: 'PMAY Housing', status: 'Rejected', date: '2026-09-01', size: '850 KB', note: 'Blurry copy, re-upload needed' },
  { id: 'DOC-105', citizen: 'Gurpreet Singh Gill', name: 'Bank Passbook', scheme: 'PM-KISAN', status: 'Pending', date: '2026-08-30', size: '1.2 MB' },
];

export function AdminDocumentsPage() {
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('All');

  const filtered = MOCK_DOCS.filter(d => {
    const matchQ = d.citizen.toLowerCase().includes(search.toLowerCase()) || d.name.toLowerCase().includes(search.toLowerCase()) || d.scheme.toLowerCase().includes(search.toLowerCase());
    const matchS = filterStatus === 'All' || d.status === filterStatus;
    return matchQ && matchS;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <FolderOpen className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-black text-slate-800">Citizen Document Verification Vault</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">Review, verify, and validate KYC proofs submitted by citizens for scheme approvals</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="info" size="sm">{MOCK_DOCS.length} Documents Indexed</Badge>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by citizen, document name, or scheme..."
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 text-xs border border-slate-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
        >
          <option value="All">All Verification Statuses</option>
          <option value="Verified">Verified</option>
          <option value="Pending">Pending</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3.5 px-4">Doc ID</th>
                <th className="py-3.5 px-4">Citizen</th>
                <th className="py-3.5 px-4">Document Type</th>
                <th className="py-3.5 px-4">Scheme</th>
                <th className="py-3.5 px-4">Uploaded Date</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filtered.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500">{doc.id}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">{doc.citizen}</td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-1.5 font-semibold text-blue-700">
                      <FileCheck2 className="w-3.5 h-3.5 text-blue-500" />
                      {doc.name}
                    </div>
                    <span className="text-[10px] text-slate-400">{doc.size}</span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600">{doc.scheme}</td>
                  <td className="py-3.5 px-4 text-slate-500">{doc.date}</td>
                  <td className="py-3.5 px-4">
                    {doc.status === 'Verified' && <Badge variant="success" size="sm">Verified</Badge>}
                    {doc.status === 'Pending' && <Badge variant="warning" size="sm">Pending</Badge>}
                    {doc.status === 'Rejected' && <Badge variant="danger" size="sm">Rejected</Badge>}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="View Document">
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button className="p-1.5 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors" title="Download">
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminDocumentsPage;
