import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileCheck2,
  Bookmark,
  Sparkles,
  TrendingUp,
  Award,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  FolderLock
} from 'lucide-react';
import { StatsCard, ProfileProgress } from '../../components/dashboard/StatsCard';
import { SchemeCard, ActivityFeed } from '../../components/dashboard/SchemeCard';
import Button from '../../components/ui/Button';
import { DEFAULT_CITIZEN, MOCK_APPLICATIONS } from '../../data/mockCitizenData';
import { SCHEMES } from '../../data/schemesData';

export function DashboardPage() {
  const navigate = useNavigate();
  const [savedSchemes, setSavedSchemes] = useState(['pm-kisan', 'ayushman-bharat']);

  const handleToggleSave = (id) => {
    setSavedSchemes((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const recentActivities = [
    { title: "Application APP-2026-97814 Submitted", subtitle: "PM Vishwakarma Modern Toolkit under review", time: "2 hours ago" },
    { title: "AI Eligibility Analysis Completed", subtitle: "Scanned 450+ schemes; 12 matches identified", time: "5 hours ago" },
    { title: "New Scheme Recommendation", subtitle: "PMAY Credit Linked Subsidy Scheme added", time: "Yesterday" },
    { title: "Document Uploaded", subtitle: "Land Revenue Record (Khasra-Khatauni) indexed", time: "3 days ago" },
  ];

  const recommended = SCHEMES.slice(0, 4);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
            Good Morning, {DEFAULT_CITIZEN.name.split(' ')[0]} 👋
          </h1>
          <p className="text-xs sm:text-sm text-slate-muted mt-1">
            Here is your SchemeAssist welfare and eligibility overview.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={Sparkles}
            onClick={() => navigate('/ai-assistant')}
          >
            Chat with AI
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/schemes')}
          >
            Find Schemes &rarr;
          </Button>
        </div>
      </div>

      {/* Top 4 Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Eligible Schemes"
          value="12"
          subtitle="5 Highly recommended"
          icon={Award}
          color="green"
        />
        <StatsCard
          title="Active Applications"
          value={MOCK_APPLICATIONS.length.toString()}
          subtitle="1 Approved, 2 In review"
          icon={FileCheck2}
          color="blue"
        />
        <StatsCard
          title="Saved Schemes"
          value={savedSchemes.length.toString()}
          subtitle="Quick access bookmarks"
          icon={Bookmark}
          color="orange"
        />
        <StatsCard
          title="Profile Completion"
          value={`${DEFAULT_CITIZEN.profileCompletion}%`}
          subtitle="3 of 4 stages verified"
          icon={ShieldCheck}
          color="navy"
        />
      </div>

      {/* Main Grid: Recommended Schemes + Profile Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Recommended Schemes (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-navy">Recommended Schemes for You</h2>
              <p className="text-xs text-slate-muted">Personalized according to your farming occupation & income</p>
            </div>
            <button
              onClick={() => navigate('/schemes')}
              className="text-xs font-bold text-primary hover:text-primary-dark"
            >
              See All &rarr;
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {recommended.map((scheme) => (
              <SchemeCard
                key={scheme.id}
                scheme={scheme}
                isSaved={savedSchemes.includes(scheme.id)}
                onSave={handleToggleSave}
              />
            ))}
          </div>
        </div>

        {/* Right Column: Profile Progress + Quick Action (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <ProfileProgress
            percentage={DEFAULT_CITIZEN.profileCompletion}
            checklist={DEFAULT_CITIZEN.checklist}
            onComplete={() => navigate('/documents')}
          />

          <ActivityFeed activities={recentActivities} />
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
