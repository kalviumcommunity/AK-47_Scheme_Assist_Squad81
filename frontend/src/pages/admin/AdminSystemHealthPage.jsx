import React from 'react';
import { Activity, Database, RefreshCw, Server, Sparkles } from 'lucide-react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import { useHealthCheck } from '../../hooks/useHealthCheck';

export default function AdminSystemHealthPage() {
    const { health, loading, error, refetch } = useHealthCheck(30000);
    const online = health?.status === 'healthy';
    const items = [
        ['Backend status', online ? 'Online' : 'Offline', Server, online],
        ['AI provider', 'Google Gemini', Sparkles, health?.gemini_configured],
        ['Vector database', 'ChromaDB', Database, Boolean(health)],
        ['Retrieval', 'Hybrid retrieval', Activity, Boolean(health)],
    ];

    return (
        <div className="space-y-6 animate-fadeIn pb-10">
            <div className="flex items-start justify-between gap-4">
                <div><h1 className="text-xl font-black text-navy">System health</h1><p className="text-xs text-slate-muted mt-1">Live service configuration from <code>/api/health</code>. Refreshes every 30 seconds.</p></div>
                <Button variant="outline" size="sm" icon={RefreshCw} onClick={refetch} isLoading={loading}>Refresh</Button>
            </div>
            {error && <div className="p-3 rounded-card bg-gov-error-light border border-gov-error/20 text-xs text-gov-error">SchemeAssist AI is temporarily unavailable. Please try again in a moment.</div>}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {items.map(([label, value, Icon, healthy]) => <Card key={label} className="flex items-center gap-3"><div className="w-10 h-10 rounded-btn bg-slate-100 text-navy flex items-center justify-center"><Icon className="w-5 h-5" /></div><div><p className="text-xs text-slate-muted">{label}</p><Badge variant={healthy ? 'success' : 'warning'} size="sm" dot>{value}</Badge></div></Card>)}
            </div>
            <Card><h2 className="text-sm font-bold text-navy mb-4">Runtime configuration</h2><dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs"><div><dt className="text-slate-muted">Chat model</dt><dd className="font-semibold mt-1 break-all">{health?.chat_model || '—'}</dd></div><div><dt className="text-slate-muted">Embedding model</dt><dd className="font-semibold mt-1 break-all">{health?.embedding_model || '—'}</dd></div><div><dt className="text-slate-muted">Collection</dt><dd className="font-semibold mt-1 break-all">{health?.collection_name || '—'}</dd></div><div><dt className="text-slate-muted">Indexed chunks</dt><dd className="font-semibold mt-1">{health?.indexed_chunks ?? '—'}</dd></div></dl></Card>
            <p className="text-[11px] text-slate-muted">Last updated: {health ? new Date().toLocaleString('en-IN') : 'Not available'}</p>
        </div>
    );
}
