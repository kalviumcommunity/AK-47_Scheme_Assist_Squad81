import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wheat,
  HeartPulse,
  Home,
  Wrench,
  ShieldAlert,
  GraduationCap,
  Flame,
  ArrowRight,
  Bookmark,
  CheckCircle2
} from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export function SchemeCard({ scheme, onSave, isSaved = false }) {
  const navigate = useNavigate();

  const getIcon = (name) => {
    switch (name) {
      case 'Wheat': return <Wheat className="w-5 h-5 text-gov-warning" />;
      case 'HeartPulse': return <HeartPulse className="w-5 h-5 text-gov-error" />;
      case 'Home': return <Home className="w-5 h-5 text-primary" />;
      case 'Wrench': return <Wrench className="w-5 h-5 text-slate-text" />;
      case 'GraduationCap': return <GraduationCap className="w-5 h-5 text-primary" />;
      case 'Flame': return <Flame className="w-5 h-5 text-gov-warning" />;
      default: return <ShieldAlert className="w-5 h-5 text-navy" />;
    }
  };

  const getMatchVariant = (score) => {
    if (score >= 90) return 'success';
    if (score >= 75) return 'primary';
    return 'warning';
  };

  return (
    <Card hoverEffect className="flex flex-col justify-between h-full group">
      <div>
        {/* Header: Icon, Category & Match Badge */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-slate-bg border border-slate-border flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              {getIcon(scheme.icon)}
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                {scheme.category}
              </span>
              <h4 className="text-sm font-bold text-navy group-hover:text-primary transition-colors leading-tight">
                {scheme.name}
              </h4>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            <Badge variant={getMatchVariant(scheme.matchScore)} size="sm">
              {scheme.matchScore}% Match
            </Badge>
            {scheme.ragVerified && (
              <span className="text-[9px] font-bold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 flex items-center gap-0.5">
                <span>✨</span>
                <span>AI Verified</span>
              </span>
            )}
          </div>
        </div>

        {/* Benefits Tag */}
        <div className="bg-primary-50/50 border border-primary/10 rounded-btn p-2.5 mb-3">
          <span className="text-[11px] font-bold text-primary block leading-none">
            {scheme.benefit}
          </span>
          <span className="text-[10px] text-slate-muted mt-0.5 block leading-tight">
            {scheme.benefitFrequency || scheme.governmentType}
          </span>
        </div>

        {/* Description */}
        <p className="text-xs text-slate-muted line-clamp-2 mb-3 leading-relaxed">
          {scheme.description}
        </p>

        {/* Eligibility Reasons & Highlights */}
        {scheme.reasons && scheme.reasons.length > 0 && (
          <div className="mb-3 p-2.5 bg-emerald-50/70 border border-emerald-200/80 rounded-lg text-xs">
            <div className="flex items-center gap-1.5 font-bold text-[10px] text-emerald-800 uppercase tracking-wider mb-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Eligibility Match Criteria</span>
            </div>
            <div className="space-y-1">
              {scheme.reasons.slice(0, 2).map((reason, rIdx) => (
                <div key={rIdx} className="text-[11px] text-slate-700 flex items-start gap-1.5 leading-tight">
                  <span className="text-emerald-600 font-bold">•</span>
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="pt-3 border-t border-slate-border flex items-center justify-between gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSave && onSave(scheme.id);
          }}
          className={`p-1.5 rounded-btn transition-colors ${
            isSaved
              ? 'text-gov-warning bg-gov-warning-light'
              : 'text-slate-400 hover:text-navy hover:bg-slate-100'
          }`}
          title={isSaved ? 'Saved in profile' : 'Save scheme'}
        >
          <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
        </button>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/schemes/${scheme.id}`)}
          >
            Details
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate(`/apply/${scheme.id}`)}
          >
            Apply Now
          </Button>
        </div>
      </div>
    </Card>
  );
}

export function ActivityFeed({ activities = [] }) {
  return (
    <Card>
      <div className="flex items-center justify-between pb-3 border-b border-slate-border mb-3">
        <h3 className="text-sm font-bold text-navy">Recent Activity</h3>
      </div>
      <div className="divide-y divide-slate-100">
        {activities.map((act, i) => (
          <div key={i} className="py-2.5 flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-1.5 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-text truncate">{act.title}</p>
              <p className="text-[11px] text-slate-muted">{act.subtitle}</p>
            </div>
            <span className="text-[10px] text-slate-400 shrink-0">{act.time}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default SchemeCard;
