import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Users,
  FileCheck2,
  FolderOpen,
  Headphones,
  BarChart3,
  ScrollText,
  Settings,
  LogOut,
  ShieldAlert,
  ChevronRight,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_SECTIONS = [
  {
    label: 'Command Center',
    items: [
      { name: 'Overview', path: '/admin', icon: LayoutDashboard, end: true },
      { name: 'Analytics', path: '/admin/analytics', icon: BarChart3 },
      { name: 'System Logs', path: '/admin/logs', icon: ScrollText, badge: 'Live' },
    ],
  },
  {
    label: 'Management',
    items: [
      { name: 'Schemes', path: '/admin/schemes', icon: BookOpen },
      { name: 'Citizens', path: '/admin/citizens', icon: Users },
      { name: 'Applications', path: '/admin/applications', icon: FileCheck2 },
      { name: 'Documents', path: '/admin/documents', icon: FolderOpen },
    ],
  },
  {
    label: 'Support',
    items: [
      { name: 'Helpdesk Tickets', path: '/admin/helpdesk', icon: Headphones },
      { name: 'Settings', path: '/admin/settings', icon: Settings },
    ],
  },
];

export function AdminSidebar({ className = '', onCloseMobile }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  return (
    <aside className={`w-64 bg-[#0F2B46] flex flex-col h-screen shrink-0 ${className}`}>
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500 text-white flex items-center justify-center font-extrabold text-sm shadow">
            SA
          </div>
          <div>
            <h1 className="text-sm font-extrabold text-white tracking-tight leading-tight">
              SchemeAssist
            </h1>
            <div className="flex items-center gap-1 mt-0.5">
              <ShieldAlert className="w-2.5 h-2.5 text-amber-400" />
              <p className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">
                Admin Portal
              </p>
            </div>
          </div>
        </div>
        {onCloseMobile && (
          <button
            onClick={onCloseMobile}
            className="md:hidden p-1 rounded text-white/50 hover:text-white hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <p className="px-3 pb-1.5 text-[10px] font-bold text-white/40 uppercase tracking-widest">
              {section.label}
            </p>
            <div className="space-y-0.5">
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.end}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-150 group ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-white/60 hover:bg-white/8 hover:text-white'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <div className="flex items-center gap-2.5">
                        <item.icon
                          className={`w-4 h-4 transition-colors ${
                            isActive ? 'text-white' : 'text-white/40 group-hover:text-white/80'
                          }`}
                        />
                        <span>{item.name}</span>
                      </div>
                      {item.badge && (
                        <span
                          className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold uppercase tracking-wide ${
                            isActive
                              ? 'bg-white/20 text-white'
                              : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                      {!item.badge && (
                        <ChevronRight
                          className={`w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity ${
                            isActive ? 'opacity-60' : ''
                          }`}
                        />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom – Admin Info & Logout */}
      <div className="p-3 border-t border-white/10">
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-7 h-7 rounded-full bg-blue-500 flex items-center justify-center shrink-0 text-white text-xs font-bold">
              AD
            </div>
            <div className="truncate">
              <p className="text-xs font-bold text-white truncate">Administrator</p>
              <p className="text-[10px] text-white/40 truncate">Nodal Officer</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="text-white/40 hover:text-red-400 p-1.5 rounded-lg hover:bg-white/10 transition-colors shrink-0"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}

export default AdminSidebar;
