import React from 'react';

export function Skeleton({ className = '', variant = 'rect' }) {
  const baseClasses = 'animate-pulse bg-slate-200/80';
  const variants = {
    rect: 'rounded-card',
    circle: 'rounded-full',
    text: 'rounded h-4',
  };

  return <div className={`${baseClasses} ${variants[variant] || variants.rect} ${className}`} />;
}

export function CardSkeleton() {
  return (
    <div className="bg-white border border-slate-border rounded-card p-5 shadow-subtle space-y-3">
      <div className="flex items-center gap-3">
        <Skeleton variant="circle" className="w-10 h-10" />
        <div className="space-y-1.5 flex-1">
          <Skeleton variant="text" className="w-2/3" />
          <Skeleton variant="text" className="w-1/3 h-3" />
        </div>
      </div>
      <Skeleton variant="text" className="w-full h-12" />
      <div className="pt-2 flex justify-between items-center">
        <Skeleton variant="text" className="w-24 h-6 rounded-badge" />
        <Skeleton variant="rect" className="w-20 h-8 rounded-btn" />
      </div>
    </div>
  );
}

export default Skeleton;
