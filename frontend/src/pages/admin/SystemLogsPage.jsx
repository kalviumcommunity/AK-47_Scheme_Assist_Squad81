import React, { useState, useEffect, useRef } from 'react';
import {
  ScrollText, Download, RefreshCw, Search, Filter,
  CheckCircle2, AlertCircle, Info, AlertTriangle,
  User, BookOpen, FileCheck2, Database, Cpu, Shield,
  ChevronDown, ChevronUp, Pause, Play, Trash2
} from 'lucide-react';

/* ── Realistic mock log generator ──────────────────────────── */
const LOG_TEMPLATES = [
  { level: 'INFO',    source: 'AUTH',     message: 'Citizen login successful — CIT-{id}',        icon: User },
  { level: 'INFO',    source: 'AUTH',     message: 'Admin session authenticated — nodal officer', icon: Shield },
  { level: 'INFO',    source: 'API',      message: 'POST /query — RAG pipeline triggered',        icon: Cpu },
  { level: 'INFO',    source: 'API',      message: 'GET /schemes — 10 schemes returned',          icon: BookOpen },
  { level: 'INFO',    source: 'DB',       message: 'ChromaDB similarity search completed — {ms}ms latency', icon: Database },
  { level: 'SUCCESS', source: 'APP',      message: 'Application APP-2026-{id} approved by nodal officer', icon: FileCheck2 },
  { level: 'SUCCESS', source: 'API',      message: 'Eligibility analysis completed for CIT-{id}', icon: Cpu },
  { level: 'SUCCESS', source: 'DB',       message: 'Document uploaded — {docs} docs indexed in ChromaDB', icon: Database },
  { level: 'WARN',    source: 'API',      message: 'Rate limit approaching — 80% of quota used',  icon: AlertTriangle },
  { level: 'WARN',    source: 'AUTH',     message: 'Failed login attempt from IP 192.168.{ip}',   icon: Shield },
  { level: 'WARN',    source: 'DB',       message: 'Slow query detected — took {ms}ms',           icon: Database },
  { level: 'ERROR',   source: 'API',      message: 'LLM API timeout — retrying (attempt {n}/3)',  icon: Cpu },
  { level: 'ERROR',   source: 'DB',       message: 'ChromaDB connection refused — port 8001',     icon: Database },
  { level: 'INFO',    source: 'SCHEME',   message: 'Scheme PM-KISAN eligibility rules recalculated', icon: BookOpen },
  { level: 'INFO',    source: 'HELPDESK', message: 'Ticket HELP-{id} created by citizen',         icon: User },
  { level: 'SUCCESS', source: 'HELPDESK', message: 'Ticket HELP-{id} resolved — SLA met',         icon: CheckCircle2 },
  { level: 'INFO',    source: 'SYSTEM',   message: 'Scheduled backup completed — 14.2 MB',        icon: Database },
  { level: 'INFO',    source: 'SYSTEM',   message: 'Health check passed — all services nominal',  icon: CheckCircle2 },
];

let logCounter = 1000;

function generateLog() {
  const tpl = LOG_TEMPLATES[Math.floor(Math.random() * LOG_TEMPLATES.length)];
  const id = String(Math.floor(Math.random() * 90000) + 10000);
  const ms = String(Math.floor(Math.random() * 1800) + 50);
  const ip = String(Math.floor(Math.random() * 255));
  const n = String(Math.floor(Math.random() * 2) + 1);
  const docs = String(Math.floor(Math.random() * 12) + 1);
  const helpId = String(Math.floor(Math.random() * 9000) + 1000);
  const msg = tpl.message
    .replace('{id}', id).replace('{ms}', ms).replace('{ip}', ip)
    .replace('{n}', n).replace('{docs}', docs);
  return {
    id: ++logCounter,
    level: tpl.level,
    source: tpl.source,
    message: msg,
    icon: tpl.icon,
    timestamp: new Date(),
    details: `RequestID: req-${id}-${Date.now().toString(36)}  |  Env: production  |  Node: worker-01`,
  };
}

const INITIAL_LOGS = Array.from({ length: 40 }, (_, i) => {
  const log = generateLog();
  log.timestamp = new Date(Date.now() - (40 - i) * 7000 - Math.random() * 5000);
  return log;
}).reverse();

/* ── Helpers ────────────────────────────────────────────────── */
const LEVEL_CONFIG = {
  INFO:    { bg: 'bg-blue-50',   text: 'text-blue-700',   dot: 'bg-blue-500',   border: 'border-blue-200' },
  SUCCESS: { bg: 'bg-emerald-50',text: 'text-emerald-700',dot: 'bg-emerald-500',border: 'border-emerald-200' },
  WARN:    { bg: 'bg-amber-50',  text: 'text-amber-700',  dot: 'bg-amber-400',  border: 'border-amber-200' },
  ERROR:   { bg: 'bg-red-50',    text: 'text-red-700',    dot: 'bg-red-500',    border: 'border-red-200' },
};

const SOURCES = ['All Sources', 'AUTH', 'API', 'DB', 'APP', 'SCHEME', 'HELPDESK', 'SYSTEM'];
const LEVELS  = ['All Levels', 'INFO', 'SUCCESS', 'WARN', 'ERROR'];

function fmtTime(d) {
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}
function fmtDate(d) {
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

export function SystemLogsPage() {
  const [logs, setLogs] = useState(INITIAL_LOGS);
  const [live, setLive] = useState(true);
  const [search, setSearch] = useState('');
  const [filterLevel, setFilterLevel] = useState('All Levels');
  const [filterSource, setFilterSource] = useState('All Sources');
  const [expandedId, setExpandedId] = useState(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const bottomRef = useRef(null);

  /* Live feed — adds a new log every ~4s when live=true */
  useEffect(() => {
    if (!live) return;
    const timer = setInterval(() => {
      setLogs((prev) => [generateLog(), ...prev.slice(0, 499)]);
    }, 4000);
    return () => clearInterval(timer);
  }, [live]);

  /* Auto-scroll */
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  /* Filtered view */
  const filtered = logs.filter((l) => {
    if (filterLevel !== 'All Levels' && l.level !== filterLevel) return false;
    if (filterSource !== 'All Sources' && l.source !== filterSource) return false;
    if (search && !l.message.toLowerCase().includes(search.toLowerCase()) &&
        !l.source.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const counts = { INFO: 0, SUCCESS: 0, WARN: 0, ERROR: 0 };
  logs.forEach((l) => counts[l.level]++);

  const downloadLogs = () => {
    const txt = filtered.map((l) =>
      `[${fmtDate(l.timestamp)} ${fmtTime(l.timestamp)}] [${l.level.padEnd(7)}] [${l.source.padEnd(8)}] ${l.message}`
    ).join('\n');
    const blob = new Blob([txt], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `schemeassist-logs-${Date.now()}.txt`;
    a.click();
  };

  return (
    <div className="space-y-5 animate-fadeIn pb-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ScrollText className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-black text-[#0F2B46] tracking-tight">System Activity Logs</h1>
            <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border ${
              live ? 'bg-emerald-50 text-emerald-700 border-emerald-300' : 'bg-slate-100 text-slate-500 border-slate-300'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${live ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
              {live ? 'Live Feed' : 'Paused'}
            </span>
          </div>
          <p className="text-xs text-slate-500">Real-time RAG pipeline, API, auth, and database event stream.</p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => setLogs(INITIAL_LOGS)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 border border-red-200 rounded-lg transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" /> Clear
          </button>
          <button
            onClick={() => setLogs((p) => [generateLog(), ...p])}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Simulate
          </button>
          <button
            onClick={downloadLogs}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50 border border-blue-200 rounded-lg transition-colors"
          >
            <Download className="w-3.5 h-3.5" /> Export
          </button>
          <button
            onClick={() => setLive((v) => !v)}
            className={`flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold rounded-lg border transition-colors ${
              live
                ? 'bg-[#0F2B46] text-white border-[#0F2B46] hover:bg-blue-900'
                : 'bg-emerald-600 text-white border-emerald-600 hover:bg-emerald-700'
            }`}
          >
            {live ? <><Pause className="w-3.5 h-3.5" /> Pause</> : <><Play className="w-3.5 h-3.5" /> Resume</>}
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {Object.entries(counts).map(([level, count]) => {
          const cfg = LEVEL_CONFIG[level];
          return (
            <button
              key={level}
              onClick={() => setFilterLevel(filterLevel === level ? 'All Levels' : level)}
              className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
                filterLevel === level
                  ? `${cfg.bg} ${cfg.border} ring-2 ring-offset-1 ring-current ${cfg.text}`
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div>
                <p className={`text-[10px] font-bold uppercase tracking-wider ${filterLevel === level ? cfg.text : 'text-slate-500'}`}>
                  {level}
                </p>
                <p className={`text-xl font-black ${filterLevel === level ? cfg.text : 'text-slate-800'}`}>
                  {count}
                </p>
              </div>
              <span className={`w-2.5 h-2.5 rounded-full ${cfg.dot} ${level === 'INFO' ? '' : 'animate-pulse'}`} />
            </button>
          );
        })}
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-2 bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search logs by message or source..."
            className="w-full pl-8 pr-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {SOURCES.map((s) => <option key={s}>{s}</option>)}
          </select>
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {LEVELS.map((l) => <option key={l}>{l}</option>)}
          </select>
          <label className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 cursor-pointer whitespace-nowrap">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-slate-300"
            />
            Auto-scroll
          </label>
        </div>
      </div>

      {/* Log Count */}
      <div className="flex items-center justify-between px-1">
        <p className="text-xs text-slate-500">
          Showing <span className="font-bold text-slate-800">{filtered.length}</span> of{' '}
          <span className="font-bold text-slate-800">{logs.length}</span> log entries
        </p>
        <span className="text-[10px] text-slate-400 font-mono">
          Last updated: {fmtTime(new Date())}
        </span>
      </div>

      {/* Log Table */}
      <div className="bg-[#0d1117] rounded-2xl border border-slate-800 overflow-hidden shadow-lg font-mono">
        {/* Table Header */}
        <div className="hidden sm:grid grid-cols-12 gap-2 px-4 py-2 border-b border-white/10 text-[10px] font-bold text-white/30 uppercase tracking-widest">
          <div className="col-span-2">Time</div>
          <div className="col-span-1">Level</div>
          <div className="col-span-2">Source</div>
          <div className="col-span-7">Message</div>
        </div>

        {/* Entries */}
        <div className="max-h-[60vh] overflow-y-auto" id="log-scroll-area">
          {filtered.length === 0 ? (
            <div className="py-16 text-center text-white/30">
              <ScrollText className="w-8 h-8 mx-auto mb-3 opacity-40" />
              <p className="text-sm font-bold">No logs match current filters</p>
            </div>
          ) : (
            filtered.map((log) => {
              const cfg = LEVEL_CONFIG[log.level];
              const isExpanded = expandedId === log.id;
              return (
                <div
                  key={log.id}
                  onClick={() => setExpandedId(isExpanded ? null : log.id)}
                  className={`border-b border-white/5 cursor-pointer transition-colors hover:bg-white/5 ${
                    isExpanded ? 'bg-white/8' : ''
                  }`}
                >
                  <div className="grid grid-cols-12 gap-2 px-4 py-2.5 text-[11px] items-start">
                    {/* Timestamp */}
                    <div className="col-span-3 sm:col-span-2 text-white/40 tabular-nums leading-relaxed">
                      <span className="hidden sm:block">{fmtDate(log.timestamp)}</span>
                      <span className="text-white/60">{fmtTime(log.timestamp)}</span>
                    </div>
                    {/* Level */}
                    <div className="col-span-2 sm:col-span-1">
                      <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${cfg.bg} ${cfg.text}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} shrink-0`} />
                        <span className="hidden sm:block">{log.level}</span>
                      </span>
                    </div>
                    {/* Source */}
                    <div className="hidden sm:block sm:col-span-2">
                      <span className="px-1.5 py-0.5 rounded bg-white/10 text-white/60 text-[9px] font-bold tracking-widest uppercase">
                        {log.source}
                      </span>
                    </div>
                    {/* Message */}
                    <div className="col-span-7 text-white/80 leading-relaxed break-words flex items-start justify-between gap-2">
                      <span>{log.message}</span>
                      {isExpanded
                        ? <ChevronUp className="w-3 h-3 text-white/30 shrink-0 mt-0.5" />
                        : <ChevronDown className="w-3 h-3 text-white/20 shrink-0 mt-0.5" />
                      }
                    </div>
                  </div>
                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="px-4 pb-3 pt-0 text-[10px] text-white/40 border-t border-white/10 bg-white/5">
                      <p className="font-mono leading-relaxed">{log.details}</p>
                      <p className="font-mono mt-0.5 text-white/20">Log ID: #{log.id} | Source: {log.source}</p>
                    </div>
                  )}
                </div>
              );
            })
          )}
          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}

export default SystemLogsPage;
