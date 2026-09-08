import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export function Modal({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  maxWidth = 'max-w-xl',
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy/60 backdrop-blur-sm animate-fadeIn">
      <div
        className={`w-full ${maxWidth} bg-white rounded-card shadow-modal border border-slate-border overflow-hidden transform transition-all duration-200 animate-scaleUp`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-border bg-slate-50/50">
          <div>
            <h3 className="text-base font-bold text-navy">{title}</h3>
            {subtitle && <p className="text-xs text-slate-muted mt-0.5">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 rounded-btn p-1 hover:bg-slate-100 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 max-h-[80vh] overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}

export default Modal;
