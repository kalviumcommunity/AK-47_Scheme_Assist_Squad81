import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  BotMessageSquare,
  FileCheck2,
  FolderLock
} from 'lucide-react';

export function MobileNavigation() {
  const items = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Schemes', path: '/schemes', icon: Search },
    { name: 'Ask AI', path: '/ai-assistant', icon: BotMessageSquare, highlight: true },
    { name: 'Applications', path: '/applications', icon: FileCheck2 },
    { name: 'Docs', path: '/documents', icon: FolderLock },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white border-t border-slate-border flex items-center justify-around px-2 z-40 shadow-elevated">
      {items.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            `flex flex-col items-center justify-center w-full py-1 text-[10px] font-semibold transition-colors ${
              isActive
                ? 'text-primary'
                : 'text-slate-muted hover:text-slate-text'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <div
                className={`p-1 rounded-btn transition-colors ${
                  item.highlight
                    ? 'bg-primary-50 text-primary border border-primary/20'
                    : ''
                }`}
              >
                <item.icon className="w-5 h-5" />
              </div>
              <span className="mt-0.5">{item.name}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}

export default MobileNavigation;
