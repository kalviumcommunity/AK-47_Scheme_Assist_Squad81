import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  Sparkles,
  FileCheck2,
  FolderLock,
  BotMessageSquare,
  HelpCircle,
  Settings,
  LogOut,
} from 'lucide-react';
import Avatar from '../ui/Avatar';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Find Schemes', path: '/schemes', icon: Search },
  { name: 'AI Analysis', path: '/ai-analysis', icon: Sparkles, badge: 'AI' },
  { name: 'Applications', path: '/applications', icon: FileCheck2 },
  { name: 'Documents', path: '/documents', icon: FolderLock },
  { name: 'AI Assistant', path: '/ai-assistant', icon: BotMessageSquare, badge: 'Active' },
  { name: 'Helpdesk', path: '/helpdesk', icon: HelpCircle },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export function Sidebar({ className = '', onCloseMobile }) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className={`w-64 bg-white border-r border-slate-border flex flex-col h-screen shrink-0 ${className}`}>
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-border gap-3">
        <div className="w-9 h-9 rounded-btn bg-navy text-white flex items-center justify-center font-extrabold text-lg shadow-sm">
          SA
        </div>
        <div>
          <h1 className="text-base font-extrabold text-navy tracking-tight leading-tight">
            SchemeAssist
          </h1>
          <p className="text-[11px] font-medium text-slate-muted leading-tight">
            Citizen Portal
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          Main Menu
        </div>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={onCloseMobile}
            className={({ isActive }) =>
              `flex items-center justify-between px-3.5 py-2.5 rounded-btn text-xs font-semibold transition-all duration-150 group ${
                isActive
                  ? 'bg-navy text-white shadow-sm'
                  : 'text-slate-text hover:bg-slate-50 hover:text-navy'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className="flex items-center gap-3">
                  <item.icon
                    className={`w-4 h-4 transition-colors ${
                      isActive ? 'text-primary-light' : 'text-slate-400 group-hover:text-primary'
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold uppercase ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'bg-primary-50 text-primary border border-primary/20'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </div>

      {/* Bottom Profile */}
      <div className="p-3 border-t border-slate-border bg-slate-50/70">
        <div className="flex items-center justify-between p-2 rounded-btn hover:bg-white transition-colors border border-transparent hover:border-slate-border">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <Avatar name={user?.name || 'User'} size="sm" status="online" />
            <div className="truncate">
              <p className="text-xs font-bold text-navy truncate">{user?.name || 'Citizen'}</p>
              <p className="text-[11px] text-slate-muted truncate">{user?.email || ''}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="text-slate-400 hover:text-red-500 p-1.5 rounded-btn hover:bg-slate-100 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
