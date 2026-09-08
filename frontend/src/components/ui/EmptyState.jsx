import React from 'react';
import { Inbox, AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';

export function EmptyState({
  title = 'No items found',
  description = 'There are currently no records matching your request.',
  icon: Icon = Inbox,
  actionText,
  onAction,
  className = '',
}) {
  return (
    <div className={`text-center py-12 px-4 border border-dashed border-slate-border rounded-card bg-white/50 ${className}`}>
      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-3">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-navy mb-1">{title}</h3>
      <p className="text-xs text-slate-muted max-w-sm mx-auto mb-4">{description}</p>
      {actionText && onAction && (
        <Button variant="primary" size="sm" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
}

export function ErrorState({
  title = 'Unable to Load Data',
  description = 'A network or server error occurred while retrieving this information.',
  onRetry,
  className = '',
}) {
  return (
    <div className={`p-6 border border-gov-error/20 bg-gov-error-light rounded-card text-center ${className}`}>
      <div className="w-10 h-10 rounded-full bg-gov-error/10 text-gov-error flex items-center justify-center mx-auto mb-3">
        <AlertTriangle className="w-5 h-5" />
      </div>
      <h3 className="text-sm font-bold text-gov-error mb-1">{title}</h3>
      <p className="text-xs text-slate-muted max-w-md mx-auto mb-4">{description}</p>
      {onRetry && (
        <Button variant="outline" size="sm" icon={RefreshCw} onClick={onRetry} className="bg-white">
          Try Again
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
