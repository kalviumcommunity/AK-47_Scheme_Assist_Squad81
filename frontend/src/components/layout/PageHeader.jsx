import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

/**
 * Standardized PageHeader layout component for SchemeAssist screens.
 * Supports breadcrumbs, title, subtitle, status badges, and action buttons.
 */
export function PageHeader({
  title,
  subtitle,
  breadcrumbs = [],
  badges = null,
  actions = null,
  className = '',
}) {
  return (
    <div className={`mb-6 md:mb-8 ${className}`}>
      {/* Breadcrumbs */}
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav aria-label="Breadcrumb" className="mb-2.5 flex items-center gap-1.5 text-xs text-text-secondary">
          <Link
            to="/"
            className="hover:text-primary-blue transition-colors flex items-center gap-1 text-slate-500"
          >
            <Home className="w-3.5 h-3.5" />
            <span className="sr-only">Home</span>
          </Link>
          {breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1;
            return (
              <React.Fragment key={index}>
                <ChevronRight className="w-3 h-3 text-slate-400 shrink-0" />
                {crumb.to && !isLast ? (
                  <Link
                    to={crumb.to}
                    className="hover:text-primary-blue transition-colors text-slate-600 truncate max-w-[140px] sm:max-w-none"
                  >
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="font-semibold text-text-primary truncate max-w-[160px] sm:max-w-none">
                    {crumb.label}
                  </span>
                )}
              </React.Fragment>
            );
          })}
        </nav>
      )}

      {/* Main Header Row */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold text-primary-navy tracking-tight">
              {title}
            </h1>
            {badges}
          </div>
          {subtitle && (
            <p className="text-sm text-text-secondary mt-1 max-w-2xl leading-relaxed">
              {subtitle}
            </p>
          )}
        </div>

        {/* Action Buttons */}
        {actions && (
          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

export default PageHeader;
