import React from 'react';

export function Select({
  label,
  options = [],
  error,
  helperText,
  className = '',
  id,
  ...props
}) {
  const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-xs font-semibold text-slate-text uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`w-full rounded-input border bg-white px-3 py-2 text-sm text-slate-text transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
          error ? 'border-gov-error focus:ring-gov-error' : 'border-slate-border hover:border-slate-300'
        } ${className}`}
        {...props}
      >
        {options.map((opt, i) => (
          <option key={i} value={typeof opt === 'string' ? opt : opt.value}>
            {typeof opt === 'string' ? opt : opt.label}
          </option>
        ))}
      </select>
      {error ? (
        <p className="mt-1 text-xs text-gov-error">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-xs text-slate-muted">{helperText}</p>
      ) : null}
    </div>
  );
}

export function Textarea({
  label,
  error,
  helperText,
  rows = 3,
  className = '',
  id,
  ...props
}) {
  const textareaId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={textareaId} className="block text-xs font-semibold text-slate-text uppercase tracking-wider mb-1.5">
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        rows={rows}
        className={`w-full rounded-input border bg-white px-3.5 py-2 text-sm text-slate-text transition-colors duration-150 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent ${
          error ? 'border-gov-error focus:ring-gov-error' : 'border-slate-border hover:border-slate-300'
        } ${className}`}
        {...props}
      />
      {error ? (
        <p className="mt-1 text-xs text-gov-error">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-xs text-slate-muted">{helperText}</p>
      ) : null}
    </div>
  );
}

export default Select;
