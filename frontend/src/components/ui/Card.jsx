import React from 'react';

export function Card({
  children,
  className = '',
  hoverEffect = false,
  onClick,
  ...props
}) {
  return (
    <div
      onClick={onClick}
      className={`bg-slate-card border border-slate-border rounded-card p-5 shadow-subtle transition-all duration-200 ${
        hoverEffect ? 'hover:shadow-elevated hover:border-primary/40 cursor-pointer' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action, className = '' }) {
  return (
    <div className={`flex items-start justify-between pb-4 border-b border-slate-border mb-4 ${className}`}>
      <div>
        <h3 className="text-base font-semibold text-navy tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-slate-muted mt-0.5">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export default Card;
