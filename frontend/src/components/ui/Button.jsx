import React from 'react';
import { Loader2 } from 'lucide-react';

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon,
  className = '',
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed rounded-btn';

  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-dark focus:ring-primary shadow-sm active:scale-[0.99]',
    navy: 'bg-navy text-white hover:bg-navy-800 focus:ring-navy shadow-sm active:scale-[0.99]',
    secondary: 'bg-primary-50 text-primary hover:bg-primary-100 focus:ring-primary',
    outline: 'border border-slate-border bg-white text-slate-text hover:bg-slate-bg focus:ring-primary',
    ghost: 'text-slate-text hover:bg-slate-100 focus:ring-slate-400',
    success: 'bg-gov-success text-white hover:bg-green-700 focus:ring-gov-success shadow-sm',
    danger: 'bg-gov-error text-white hover:bg-red-700 focus:ring-gov-error shadow-sm',
  };

  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2 gap-2',
    lg: 'text-base px-5 py-2.5 gap-2.5',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : Icon ? (
        <Icon className="w-4 h-4 shrink-0" />
      ) : null}
      {children}
    </button>
  );
}

export default Button;
