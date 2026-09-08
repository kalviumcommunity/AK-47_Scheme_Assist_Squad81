import React from 'react';

export function Input({
  label,
  error,
  helperText,
  icon: Icon,
  className = '',
  id,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold text-slate-text uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-muted">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          className={`w-full rounded-input border bg-white px-3.5 py-2 text-sm text-slate-text transition-colors duration-150 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:bg-slate-50 disabled:text-slate-400 ${
            Icon ? 'pl-9' : ''
          } ${
            error
              ? 'border-gov-error focus:ring-gov-error'
              : 'border-slate-border hover:border-slate-300'
          } ${className}`}
          {...props}
        />
      </div>
      {error ? (
        <p className="mt-1 text-xs text-gov-error">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-xs text-slate-muted">{helperText}</p>
      ) : null}
    </div>
  );
}

export default Input;
