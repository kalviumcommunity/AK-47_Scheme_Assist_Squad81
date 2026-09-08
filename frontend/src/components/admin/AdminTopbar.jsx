import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Menu,
  Bell,
  Search,
  RefreshCw,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';

const PAGE_META = {
  '/admin': { title: 'Executive Overview', breadcrumb: 'Overview' },
  '/admin/analytics': { title: 'Analytics & Reports', breadcrumb: 'Analytics' },
  '/admin/logs': { title: 'System Activity Logs', breadcrumb: 'Logs' },
  '/admin/schemes': { title: 'Scheme Management', breadcrumb: 'Schemes' },
  '/admin/citizens': { title: 'Citizen Registry', breadcrumb: 'Citizens' },
  '/admin/applications': { title: 'Application Queue', breadcrumb: 'Applications' },
  '/admin/documents': { title: 'Document Repository', breadcrumb: 'Documents' },
  '/admin/helpdesk': { title: 'Helpdesk & Tickets', breadcrumb: 'Helpdesk' },
  '/admin/settings': { title: 'Admin Settings', breadcrumb: 'Settings' },
};

export function AdminTopbar({ onOpenMobileSidebar }) {
  const location = useLocation();
  const navigate = useNavigate();
  const meta = PAGE_META[location.pathname] || { title: 'Admin', breadcrumb: 'Admin' };
  const now = new Date().toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: true
  });

  return (
    <header className="h-14 bg-white border-b border-slate-200 px-4 md:px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      {/* Left */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
          aria-label="Open menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center gap-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
            <span>Admin</span>
            <ChevronRight className="w-3 h-3 text-slate-300" />
            <span className="text-blue-600">{meta.breadcrumb}</span>
          </div>
          <h2 className="text-sm md:text-base font-bold text-[#0F2B46] leading-none mt-0.5">
            {meta.title}
          </h2>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        {/* Date/Time */}
        <span className="hidden lg:block text-[10px] text-slate-400 font-mono bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-lg">
          {now}
        </span>

        {/* Refresh */}
        <button
          onClick={() => window.location.reload()}
          className="p-2 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition-colors"
          title="Refresh page"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Notifications placeholder */}
        <button className="relative p-2 rounded-lg text-slate-500 hover:text-[#0F2B46] hover:bg-slate-100 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white animate-pulse" />
        </button>

        {/* Back to citizen view */}
        <button
          onClick={() => navigate('/dashboard')}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-[#0F2B46] border border-slate-200 hover:border-slate-300 rounded-lg bg-white hover:bg-slate-50 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Citizen View
        </button>
      </div>
    </header>
  );
}

export default AdminTopbar;
