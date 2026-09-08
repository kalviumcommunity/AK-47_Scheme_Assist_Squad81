import React from 'react';
import Card from '../ui/Card';

export function StatsCard({ title, value, icon: Icon, color = 'blue', subtitle }) {
  const colorMap = {
    blue: 'bg-primary-50 text-primary border-primary/20',
    green: 'bg-gov-success-light text-gov-success border-gov-success/20',
    orange: 'bg-gov-warning-light text-gov-warning border-gov-warning/20',
    navy: 'bg-navy/10 text-navy border-navy/20',
  };

  return (
    <Card className="flex items-center justify-between">
      <div>
        <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">{title}</p>
        <h3 className="text-2xl font-bold text-navy mt-1 tracking-tight">{value}</h3>
        {subtitle && <p className="text-[11px] text-slate-muted mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3 rounded-card border ${colorMap[color] || colorMap.blue} shrink-0`}>
        {Icon && <Icon className="w-6 h-6" />}
      </div>
    </Card>
  );
}

export function ProfileProgress({ percentage = 85, checklist = [], onComplete }) {
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <Card>
      <div className="flex items-center justify-between pb-3 border-b border-slate-border mb-4">
        <div>
          <h3 className="text-sm font-bold text-navy">Profile Completion</h3>
          <p className="text-xs text-slate-muted">Complete profile to unlock 100% eligibility</p>
        </div>
      </div>

      <div className="flex items-center gap-6 mb-4">
        {/* Circular Progress */}
        <div className="relative w-24 h-24 shrink-0 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-slate-100"
              strokeWidth="8"
              stroke="currentColor"
              fill="transparent"
            />
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="text-primary transition-all duration-1000 ease-out"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-bold text-navy">{percentage}%</span>
            <span className="text-[10px] text-slate-400 font-medium">Ready</span>
          </div>
        </div>

        {/* Checklist */}
        <div className="flex-1 space-y-2">
          {checklist.map((item, idx) => (
            <div key={idx} className="flex items-center gap-2 text-xs">
              <span
                className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                  item.completed
                    ? 'bg-gov-success text-white'
                    : 'border border-slate-300 text-transparent'
                }`}
              >
                ✓
              </span>
              <span className={item.completed ? 'text-slate-text font-medium' : 'text-slate-muted'}>
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={onComplete}
        className="w-full py-2 px-3 text-xs font-bold text-primary bg-primary-50 hover:bg-primary-100 rounded-btn transition-colors text-center border border-primary/20"
      >
        Complete Profile Checklist &rarr;
      </button>
    </Card>
  );
}

export default StatsCard;
