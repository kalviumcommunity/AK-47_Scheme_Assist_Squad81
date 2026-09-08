import React from 'react';

export function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  className = '',
  dot = false,
}) {
  const baseStyles = 'inline-flex items-center font-medium rounded-badge border transition-colors';

  const variants = {
    primary: 'bg-primary-50 text-primary border-primary/20',
    success: 'bg-gov-success-light text-gov-success border-gov-success/20',
    warning: 'bg-gov-warning-light text-gov-warning border-gov-warning/20',
    danger: 'bg-gov-error-light text-gov-error border-gov-error/20',
    navy: 'bg-navy/10 text-navy border-navy/20',
    neutral: 'bg-slate-100 text-slate-muted border-slate-border',
  };

  const dotColors = {
    primary: 'bg-primary',
    success: 'bg-gov-success',
    warning: 'bg-gov-warning',
    danger: 'bg-gov-error',
    navy: 'bg-navy',
    neutral: 'bg-slate-400',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  };

  return (
    <span className={`${baseStyles} ${variants[variant] || variants.neutral} ${sizes[size] || sizes.md} ${className}`}>
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant] || dotColors.neutral}`} />
      )}
      {children}
    </span>
  );
}

export default Badge;
