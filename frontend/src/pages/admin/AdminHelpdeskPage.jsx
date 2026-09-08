import React, { useState } from 'react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { Headphones, Search, CheckCircle2, Clock, AlertTriangle, MessageSquare } from 'lucide-react';

const MOCK_TICKETS = [
  { id: 'TKT-9912', citizen: 'Ramesh Kumar Sharma', subject: 'PM Vishwakarma Aadhaar verification failed on OTP step', priority: 'High', status: 'Open', date: '2026-09-07 14:32' },
  { id: 'TKT-9854', citizen: 'Sunita Devi Verma', subject: 'Ayushman Card hospital empanelment list not showing local district', priority: 'Medium', status: 'In Progress', date: '2026-09-06 10:15' },
  { id: 'TKT-9801', citizen: 'Anil Chandra Gowda', subject: 'PM-KISAN 16th installment credit confirmation SMS not received', priority: 'Low', status: 'Resolved', date: '2026-09-05 16:40' },
  { id: 'TKT-9762', citizen: 'Meenakshi Sundaram', subject: 'Eligibility evaluation query regarding single woman criteria', priority: 'Medium', status: 'Open', date: '2026-09-04 11:20' },
];

export function AdminHelpdeskPage() {
  const [tickets, setTickets] = useState(MOCK_TICKETS);
  const [filterPriority, setFilterPriority] = useState('All');

  const filtered = tickets.filter(t => filterPriority === 'All' || t.priority === filterPriority);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <Headphones className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-black text-slate-800">Citizen Helpdesk & Grievance Redressal</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">Manage citizen inquiries, technical disputes, and scheme application complaints</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="warning" size="sm">2 Open Escalations</Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase">Pending Resolution</p>
            <h4 className="text-lg font-bold text-slate-800">2 Tickets</h4>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase">In Progress</p>
            <h4 className="text-lg font-bold text-slate-800">1 Ticket</h4>
          </div>
        </Card>
        <Card className="p-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-semibold uppercase">Resolved (This Week)</p>
            <h4 className="text-lg font-bold text-slate-800">14 Tickets</h4>
          </div>
        </Card>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3.5 px-4">Ticket ID</th>
                <th className="py-3.5 px-4">Citizen</th>
                <th className="py-3.5 px-4">Subject & Details</th>
                <th className="py-3.5 px-4">Priority</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Created</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filtered.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500">{t.id}</td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">{t.citizen}</td>
                  <td className="py-3.5 px-4 max-w-xs truncate text-slate-800 font-semibold">{t.subject}</td>
                  <td className="py-3.5 px-4">
                    {t.priority === 'High' && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700">High</span>}
                    {t.priority === 'Medium' && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700">Medium</span>}
                    {t.priority === 'Low' && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">Low</span>}
                  </td>
                  <td className="py-3.5 px-4">
                    {t.status === 'Open' && <Badge variant="warning" size="sm">Open</Badge>}
                    {t.status === 'In Progress' && <Badge variant="info" size="sm">In Progress</Badge>}
                    {t.status === 'Resolved' && <Badge variant="success" size="sm">Resolved</Badge>}
                  </td>
                  <td className="py-3.5 px-4 text-slate-500">{t.date}</td>
                  <td className="py-3.5 px-4 text-right">
                    <button className="px-3 py-1 text-xs font-bold text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                      Respond
                    </button>
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

export default AdminHelpdeskPage;
