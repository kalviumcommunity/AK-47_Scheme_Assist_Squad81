import React from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import {
  Bell,
  Search,
  HelpCircle,
  Menu,
  Sparkles,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import Avatar from '../ui/Avatar';
import { useAuth } from '../../context/AuthContext';

export function TopNavbar({ onOpenMobileSidebar, onToggleNotifications, unreadCount = 2 }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const displayName = user?.name || 'Citizen';

  const getPageMeta = (pathname) => {
    switch (pathname) {
      case '/dashboard':
        return { title: 'Citizen Dashboard', breadcrumb: 'Portal' };
      case '/schemes':
        return { title: 'Find Government Schemes', breadcrumb: 'Discovery' };
      case '/ai-analysis':
        return { title: 'AI Eligibility Analysis', breadcrumb: 'AI Engine' };
      case '/applications':
        return { title: 'My Applications', breadcrumb: 'Tracking' };
      case '/documents':
        return { title: 'Document Management', breadcrumb: 'Repository' };
      case '/ai-assistant':
        return { title: 'SchemeAssist AI Assistant', breadcrumb: 'AI Advisory' };
      case '/helpdesk':
        return { title: 'Citizen Helpdesk & Grievance', breadcrumb: 'Support' };
      case '/admin':
        return { title: 'Admin Command Center', breadcrumb: 'Executive Dashboard' };
      case '/settings':
        return { title: 'Account & Preferences', breadcrumb: 'Profile' };
      default:
        if (pathname.startsWith('/schemes/')) return { title: 'Scheme Details', breadcrumb: 'Schemes' };
        if (pathname.startsWith('/apply/')) return { title: 'Apply for Scheme', breadcrumb: 'Application' };
        return { title: 'SchemeAssist', breadcrumb: 'Home' };
    }
  };

  const { title, breadcrumb } = getPageMeta(location.pathname);

  return (
    <header className="h-16 bg-white border-b border-slate-border px-4 md:px-8 flex items-center justify-between sticky top-0 z-30 shadow-subtle">
      {/* Left: Mobile Toggle & Breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="md:hidden p-2 rounded-btn text-slate-text hover:bg-slate-100"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-muted uppercase tracking-wider">
            <span>SchemeAssist</span>
            <ChevronRight className="w-3 h-3 text-slate-400" />
            <span className="text-primary">{breadcrumb}</span>
          </div>
          <h2 className="text-base md:text-lg font-bold text-navy leading-none mt-0.5">
            {title}
          </h2>
        </div>
      </div>

      {/* Right: Search, Actions, Notifications, Profile */}
      <div className="flex items-center gap-2 md:gap-4">
        {/* Quick Search trigger */}
        <div
          onClick={() => navigate('/schemes')}
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-input bg-slate-bg border border-slate-border hover:border-slate-300 text-slate-muted text-xs cursor-pointer w-48 lg:w-64 transition-colors"
        >
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <span className="truncate">Search 450+ schemes...</span>
          <kbd className="hidden lg:inline-block ml-auto text-[10px] bg-white border border-slate-border px-1.5 py-0.5 rounded text-slate-400">
            /
          </kbd>
        </div>

        {/* AI Quick Chat CTA */}
        <Link
          to="/ai-assistant"
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-btn bg-primary-50 hover:bg-primary-100 text-primary text-xs font-semibold transition-colors border border-primary/20"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Ask AI</span>
        </Link>

        {/* Notifications Icon with Badge */}
        <button
          onClick={onToggleNotifications}
          className="relative p-2 rounded-btn text-slate-600 hover:text-navy hover:bg-slate-100 transition-colors"
          aria-label="View notifications"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary rounded-full ring-2 ring-white animate-pulse" />
          )}
        </button>

        {/* Help Link */}
        <Link
          to="/helpdesk"
          className="p-2 rounded-btn text-slate-600 hover:text-navy hover:bg-slate-100 transition-colors"
          title="Help & Support"
        >
          <HelpCircle className="w-4 h-4" />
        </Link>

        <div className="h-6 w-px bg-slate-border mx-1" />

        {/* User Profile Thumbnail */}
        <button
          onClick={() => navigate('/settings')}
          className="flex items-center gap-2 pl-1 hover:opacity-90 transition-opacity"
        >
          <Avatar name={displayName} size="sm" />
          <span className="hidden lg:block text-xs font-bold text-navy max-w-[100px] truncate">
            {displayName.split(' ')[0]}
          </span>
        </button>
      </div>
    </header>
  );
}

export default TopNavbar;
