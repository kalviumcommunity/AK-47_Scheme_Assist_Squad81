import React from 'react';

export function Avatar({
  name = 'User',
  src,
  size = 'md',
  status,
  className = '',
}) {
  const getInitials = (n) => {
    if (!n) return 'U';
    const parts = n.trim().split(' ');
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return parts[0].slice(0, 2).toUpperCase();
  };

  const sizes = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-9 h-9 text-sm',
    lg: 'w-12 h-12 text-base font-semibold',
  };

  return (
    <div className="relative inline-block">
      {src ? (
        <img
          src={src}
          alt={name}
          className={`${sizes[size] || sizes.md} rounded-full object-cover border border-slate-border ${className}`}
        />
      ) : (
        <div
          className={`${sizes[size] || sizes.md} rounded-full bg-navy text-white flex items-center justify-center font-bold tracking-tight shadow-sm ${className}`}
        >
          {getInitials(name)}
        </div>
      )}
      {status && (
        <span
          className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full ring-2 ring-white ${
            status === 'online' ? 'bg-gov-success' : 'bg-slate-400'
          }`}
        />
      )}
    </div>
  );
}

export function Tabs({ tabs, activeTab, onChange, className = '' }) {
  return (
    <div className={`flex border-b border-slate-border gap-2 overflow-x-auto ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`pb-3 px-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px flex items-center gap-2 ${
              isActive
                ? 'border-primary text-primary font-semibold'
                : 'border-transparent text-slate-muted hover:text-slate-text hover:border-slate-300'
            }`}
          >
            {tab.icon && <tab.icon className="w-4 h-4" />}
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={`text-xs px-1.5 py-0.5 rounded-full ${
                  isActive ? 'bg-primary-100 text-primary' : 'bg-slate-100 text-slate-600'
                }`}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export default Avatar;
