import React, { useEffect, useMemo, useState } from 'react';
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
import { DEFAULT_CITIZEN } from '../../data/mockCitizenData';
import { SCHEMES } from '../../data/schemesData';
import { useAuth } from '../../context/AuthContext';
import { getApplications } from '../../services/applicationService';
import { listUploadedDocuments } from '../../services/api';
import { getTickets } from '../../services/helpdeskService';

export function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const citizenName = user?.name || DEFAULT_CITIZEN.name;
  const [savedSchemes, setSavedSchemes] = useState(['pm-kisan', 'ayushman-bharat']);
  const [applications, setApplications] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [tickets, setTickets] = useState([]);

  const handleToggleSave = (id) => {
    setSavedSchemes((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const loadUserActivity = async () => {
    const [allApplications, documentResult] = await Promise.all([
      getApplications(),
      listUploadedDocuments(),
    ]);
    setApplications(allApplications.filter((application) => application.citizenEmail === user?.email || application.citizenId === user?.id));
    setDocuments(documentResult.documents || []);
    setTickets(getTickets().filter((ticket) => ticket.citizenEmail === user?.email || ticket.citizenId === user?.id));
  };

  useEffect(() => {
    loadUserActivity();
    const refresh = () => loadUserActivity();
    window.addEventListener('storage', refresh);
    const interval = setInterval(refresh, 5000);
    return () => { window.removeEventListener('storage', refresh); clearInterval(interval); };
  }, [user?.email, user?.id]);

  const recentActivities = useMemo(() => [
    ...applications.map((application) => ({
      title: `Application ${application.id} ${application.status}`,
      subtitle: application.schemeName || application.scheme || 'Government scheme application',
      time: application.submittedDate || 'Recently',
    })),
    ...documents.map((document) => ({
      title: `Document ${document.status || 'uploaded'}`,
      subtitle: document.filename,
      time: document.upload_date || 'Recently',
    })),
    ...tickets.map((ticket) => ({
      title: `Helpdesk ticket ${ticket.status}`,
      subtitle: ticket.subject,
      time: ticket.createdDate || 'Recently',
    })),
  ].slice(0, 6), [applications, documents, tickets]);

  const recommended = SCHEMES.slice(0, 4);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
            Good Morning, {citizenName} 👋
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
          value={recommended.length.toString()}
          subtitle="Explore verified scheme guidance"
          icon={Award}
          color="green"
        />
        <StatsCard
          title="Active Applications"
          value={applications.length.toString()}
          subtitle={`${applications.filter((application) => application.status === 'Approved').length} approved · ${applications.filter((application) => application.status === 'Under Review').length} under review`}
          icon={FileCheck2}
          color="blue"
        />
        <StatsCard
          title="My Documents"
          value={documents.length.toString()}
          subtitle={`${documents.filter((document) => document.status === 'Approved').length} approved for review`}
          icon={FolderLock}
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

          <ActivityFeed activities={recentActivities.length ? recentActivities : [{ title: 'No recent activity', subtitle: 'Your applications, documents, and tickets will appear here.', time: '—' }]} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button onClick={() => navigate('/applications')} className="text-left bg-white border border-slate-border rounded-card p-4 hover:border-primary/40 transition-colors">
          <p className="text-xs font-bold text-navy">Application status</p><p className="text-xs text-slate-muted mt-1">Track approval decisions and timelines.</p>
        </button>
        <button onClick={() => navigate('/documents')} className="text-left bg-white border border-slate-border rounded-card p-4 hover:border-primary/40 transition-colors">
          <p className="text-xs font-bold text-navy">Document review</p><p className="text-xs text-slate-muted mt-1">View uploaded documents and review status.</p>
        </button>
        <button onClick={() => navigate('/helpdesk')} className="text-left bg-white border border-slate-border rounded-card p-4 hover:border-primary/40 transition-colors">
          <p className="text-xs font-bold text-navy">Helpdesk tickets</p><p className="text-xs text-slate-muted mt-1">{tickets.length} ticket{tickets.length === 1 ? '' : 's'} raised by you.</p>
        </button>
      </div>
    </div>
  );
}

export default DashboardPage;
