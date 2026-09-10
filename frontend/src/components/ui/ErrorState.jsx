import React, { useState } from 'react';
import { AlertTriangle, RefreshCw, ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import Button from './Button';

/**
 * Reusable ErrorState UI component for handling runtime, network, or data retrieval errors.
 */
export function ErrorState({
  title = 'Unable to Load Data',
  description = 'A network or server error occurred while retrieving this information. Please try again.',
  errorDetails = null,
  onRetry,
  onBack,
  retryLabel = 'Try Again',
  backLabel = 'Go Back',
  className = '',
}) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div
      role="alert"
      className={`p-6 sm:p-8 border border-error/20 bg-red-50/70 rounded-card text-center transition-all ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-error/10 text-error flex items-center justify-center mx-auto mb-3.5 shadow-sm">
        <AlertTriangle className="w-6 h-6" />
      </div>

      <h3 className="text-base font-bold text-text-primary mb-1.5">{title}</h3>
      <p className="text-sm text-text-secondary max-w-md mx-auto mb-5 leading-relaxed">
        {description}
      </p>

      <div className="flex flex-wrap items-center justify-center gap-2.5">
        {onRetry && (
          <Button
            variant="primary"
            size="sm"
            icon={RefreshCw}
            onClick={onRetry}
            className="shadow-sm"
          >
            {retryLabel}
          </Button>
        )}
        {onBack && (
          <Button
            variant="outline"
            size="sm"
            icon={ArrowLeft}
            onClick={onBack}
            className="bg-white border-border-color"
          >
            {backLabel}
          </Button>
        )}
      </div>

      {errorDetails && (
        <div className="mt-4 pt-4 border-t border-error/15 text-left max-w-lg mx-auto">
          <button
            type="button"
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs font-semibold text-text-secondary hover:text-text-primary flex items-center gap-1 mx-auto"
          >
            <span>{showDetails ? 'Hide technical details' : 'Show technical details'}</span>
            {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showDetails && (
            <pre className="mt-2.5 p-3 rounded bg-slate-900 text-slate-100 text-[11px] font-mono overflow-x-auto whitespace-pre-wrap">
              {typeof errorDetails === 'object' ? JSON.stringify(errorDetails, null, 2) : String(errorDetails)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export default ErrorState;
