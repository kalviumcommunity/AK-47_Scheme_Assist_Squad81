import React, { useState } from 'react';
import { NavLink, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Bell,
  Search,
  HelpCircle,
  Menu,
  Sparkles,
  ChevronRight,
  ChevronDown,
  LogOut,
  UserRound,
  ClipboardCheck,
  FileText,
  Settings,
  X,
} from 'lucide-react';
import Avatar from '../ui/Avatar';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { name: 'Home', path: '/dashboard' },
  { name: 'Find Schemes', path: '/schemes' },
  { name: 'AI Analysis', path: '/ai-analysis' },
  { name: 'Applications', path: '/applications' },
  { name: 'Documents', path: '/documents' },
  { name: 'AI Assistant', path: '/ai-assistant' },
  { name: 'Helpdesk', path: '/helpdesk' },
];

export function TopNavbar({ onToggleNotifications, unreadCount = 2 }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const displayName = user?.name || 'Citizen';

  const getPageMeta = (pathname) => {
    switch (pathname) {
      case '/dashboard':
        return { title: 'Citizen Dashboard', breadcrumb: 'Home' };
      case '/schemes':
        return { title: 'Find Government Schemes', breadcrumb: 'Schemes' };
      case '/ai-analysis':
        return { title: 'AI Eligibility Analysis', breadcrumb: 'AI Analysis' };
      case '/applications':
        return { title: 'My Applications', breadcrumb: 'Applications' };
      case '/documents':
        return { title: 'Document Management', breadcrumb: 'Documents' };
      case '/ai-assistant':
        return { title: 'SchemeAssist AI Assistant', breadcrumb: 'AI Assistant' };
      case '/helpdesk':
        return { title: 'Citizen Helpdesk & Grievance', breadcrumb: 'Helpdesk' };
      case '/settings':
        return { title: 'Account & Preferences', breadcrumb: 'Settings' };
      default:
        if (pathname.startsWith('/schemes/')) return { title: 'Scheme Details', breadcrumb: 'Schemes' };
        if (pathname.startsWith('/apply/')) return { title: 'Apply for Scheme', breadcrumb: 'Applications' };
        return { title: 'SchemeAssist', breadcrumb: 'Home' };
    }
  };

  const { title, breadcrumb } = getPageMeta(location.pathname);

  const handleLogout = () => {
    logout();
    setProfileOpen(false);
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-border bg-white/95 shadow-subtle backdrop-blur-sm">
      <div className="mx-auto max-w-none px-0">
        <div className="flex h-20 items-center justify-between gap-3 px-4 md:px-6 lg:px-8">
          <div className="flex min-w-0 flex-shrink-0 items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              className="rounded-btn p-2 text-slate-text hover:bg-slate-100 md:hidden"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            <Link to="/dashboard" className="flex items-center -ml-1">
              <img
                src="https://i.ibb.co/kg8h6Zz7/image.png"
                alt="SchemeAssist logo"
                className="h-12 w-auto object-contain"
              />
            </Link>
          </div>

          <nav className="hidden min-w-0 flex-1 items-center justify-center md:flex">
            <div className="flex w-full items-center justify-center gap-1 rounded-full border border-slate-border bg-slate-50 p-1">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `whitespace-nowrap rounded-full px-3.5 py-2 text-sm font-semibold transition-all ${
                      isActive
                        ? 'bg-primary text-white shadow-sm'
                        : 'text-slate-text hover:bg-white hover:text-primary'
                    }`
                  }
                >
                  {item.name}
                </NavLink>
              ))}
            </div>
          </nav>

          <div className="flex flex-shrink-0 items-center gap-2 md:gap-3">
            <button
              onClick={() => navigate('/schemes')}
              className="hidden items-center gap-2 rounded-xl border border-slate-border bg-slate-bg px-3 py-2 text-xs font-semibold text-slate-muted transition-colors hover:border-slate-300 hover:text-navy sm:flex"
            >
              <Search className="h-3.5 w-3.5" />
              <span className="hidden lg:inline">Search schemes...</span>
              <kbd className="hidden rounded border border-slate-border bg-white px-1 py-0.5 text-[10px] text-slate-400 lg:inline-block">
                /
              </kbd>
            </button>

            <Link
              to="/ai-assistant"
              className="hidden items-center gap-1.5 rounded-xl border border-primary/20 bg-primary-50 px-3 py-2 text-xs font-semibold text-primary transition-colors hover:bg-primary-100 md:inline-flex"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Ask AI
            </Link>

            <button
              onClick={onToggleNotifications}
              className="relative rounded-xl p-2.5 text-slate-600 transition-colors hover:bg-slate-100 hover:text-navy"
              aria-label="View notifications"
            >
              <Bell className="h-4 w-4" />
              {unreadCount > 0 && (
                <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary ring-2 ring-white" />
              )}
            </button>

            <Link
              to="/helpdesk"
              className="rounded-xl p-2.5 text-slate-600 transition-colors hover:bg-slate-100 hover:text-navy"
              title="Helpdesk"
            >
              <HelpCircle className="h-4 w-4" />
            </Link>

            <div className="relative hidden sm:block">
              <button
                onClick={() => setProfileOpen((prev) => !prev)}
                className="flex items-center gap-2 rounded-xl border border-slate-border bg-white px-2 py-1.5 transition-colors hover:border-slate-300"
              >
                <Avatar name={displayName} size="sm" />
                <span className="hidden text-xs font-bold text-navy lg:block">{displayName.split(' ')[0]}</span>
                <ChevronDown className="h-4 w-4 text-slate-400" />
              </button>

              {profileOpen && (
                <div className="absolute right-0 top-full mt-3 w-64 overflow-hidden rounded-2xl border border-slate-border bg-white shadow-modal">
                  <div className="border-b border-slate-border bg-slate-50 p-3">
                    <div className="flex items-center gap-3">
                      <Avatar name={displayName} size="sm" />
                      <div>
                        <div className="text-sm font-bold text-navy">{displayName}</div>
                        <div className="text-[11px] text-slate-muted">{user?.email || 'Citizen'}</div>
                      </div>
                    </div>
                  </div>

                  <div className="p-2">
                    {[
                      { label: 'My Profile', icon: UserRound, path: '/settings' },
                      { label: 'My Applications', icon: ClipboardCheck, path: '/applications' },
                      { label: 'My Documents', icon: FileText, path: '/documents' },
                      { label: 'Settings', icon: Settings, path: '/settings' },
                    ].map(({ label, icon: Icon, path }) => (
                      <button
                        key={label}
                        onClick={() => {
                          setProfileOpen(false);
                          navigate(path);
                        }}
                        className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm font-medium text-slate-text transition-colors hover:bg-slate-50"
                      >
                        <Icon className="h-4 w-4 text-slate-500" />
                        {label}
                      </button>
                    ))}

                    <button
                      onClick={handleLogout}
                      className="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                    >
                      <LogOut className="h-4 w-4" />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="border-t border-slate-border bg-white md:hidden">
            <div className="space-y-2 px-4 py-4">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center justify-between rounded-xl px-3 py-2.5 text-sm font-semibold transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'bg-slate-50 text-slate-text'
                    }`
                  }
                >
                  <span>{item.name}</span>
                  <ChevronRight className="h-4 w-4" />
                </NavLink>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-slate-border bg-slate-50 px-4 py-2 md:hidden">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
          <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-muted">
            {breadcrumb}
          </div>
          <div className="text-sm font-bold text-navy">{title}</div>
        </div>
      </div>
    </header>
  );
}

export default TopNavbar;
