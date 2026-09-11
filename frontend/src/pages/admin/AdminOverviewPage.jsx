import React from 'react';
import {
  Activity, CheckCircle2, Database, FileText, RefreshCw, Server, Sparkles
} from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import { useHealthCheck } from '../../hooks/useHealthCheck';

const STATUS_ITEMS = [
  ['Backend', Server, (health) => health?.status === 'healthy' ? 'Online' : 'Offline'],
  ['Gemini', Sparkles, (health) => health?.gemini_configured ? 'Configured' : 'Not configured'],
  ['Vector database', Database, (health) => health ? 'Connected' : 'Unavailable'],
];

export function AdminOverviewPage() {
  const { health, loading, error, refetch } = useHealthCheck(30000);

  return (
    <div className="space-y-6 animate-fadeIn pb-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-black text-navy">System overview</h1>
          <p className="text-xs text-slate-muted mt-1">Live status from the SchemeAssist backend and knowledge base.</p>
        </div>
        <Button variant="outline" size="sm" icon={RefreshCw} onClick={refetch} isLoading={loading}>Refresh</Button>
      </div>

      {error && <div className="p-3 rounded-card bg-gov-error-light border border-gov-error/20 text-xs text-gov-error">SchemeAssist backend is unavailable. No system metrics were returned.</div>}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {STATUS_ITEMS.map(([label, Icon, value]) => {
          const current = value(health);
          const healthy = current === 'Online' || current === 'Configured' || current === 'Connected';
          return <Card key={label} className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-slate-100 text-navy flex items-center justify-center"><Icon className="w-5 h-5" /></div>
            <div><p className="text-xs text-slate-muted">{label}</p><div className="flex items-center gap-2 mt-1"><Badge variant={healthy ? 'success' : 'warning'} size="sm" dot>{current}</Badge></div></div>
          </Card>;
        })}
      </div>

      <Card>
        <div className="flex items-center gap-2 mb-4"><Activity className="w-4 h-4 text-primary" /><h2 className="text-sm font-bold text-navy">Knowledge base status</h2></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div><p className="text-slate-muted">Indexed chunks</p><p className="text-xl font-black text-navy mt-1">{health?.indexed_chunks ?? '—'}</p></div>
          <div><p className="text-slate-muted">Embedding model</p><p className="font-semibold text-slate-700 mt-2 break-all">{health?.embedding_model || '—'}</p></div>
          <div><p className="text-slate-muted">Chat model</p><p className="font-semibold text-slate-700 mt-2 break-all">{health?.chat_model || '—'}</p></div>
          <div><p className="text-slate-muted">Collection</p><p className="font-semibold text-slate-700 mt-2 break-all">{health?.collection_name || '—'}</p></div>
        </div>
      </Card>

      <Card>
        <div className="flex items-center gap-2"><FileText className="w-4 h-4 text-primary" /><h2 className="text-sm font-bold text-navy">Analytics</h2></div>
        <p className="text-xs text-slate-muted mt-2">No analytics data available yet. Query metrics can be connected when the backend exposes an analytics endpoint.</p>
      </Card>
    </div>
  );
}

export default AdminOverviewPage;
