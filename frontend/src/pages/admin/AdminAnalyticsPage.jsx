import React from 'react';
import { AnalyticsVisual, AdminStatsGrid } from '../../components/admin/AdminComponents';
import { ADMIN_STATS, ADMIN_ANALYTICS } from '../../data/adminData';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { BarChart3, TrendingUp, Users, CheckCircle2, FileSpreadsheet } from 'lucide-react';

export function AdminAnalyticsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-black text-slate-800">Platform Analytics & Insights</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Real-time telemetry, disbursement rates, citizen demographics, and scheme uptake trends
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="success" size="sm">Live Telemetry Active</Badge>
          <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors">
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Export Report
          </button>
        </div>
      </div>

      <AdminStatsGrid stats={ADMIN_STATS} />

      <AnalyticsVisual analytics={ADMIN_ANALYTICS} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution */}
        <Card className="p-5">
          <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            Application Decision Rates
          </h3>
          <div className="space-y-3 pt-2">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-600">Approved</span>
                <span className="text-emerald-600 font-bold">78% ({ADMIN_ANALYTICS.statusBreakdown.approved})</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: '78%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-600">Under Review</span>
                <span className="text-blue-600 font-bold">14% ({ADMIN_ANALYTICS.statusBreakdown.underReview})</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full rounded-full" style={{ width: '14%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-600">Pending Docs</span>
                <span className="text-amber-600 font-bold">4% ({ADMIN_ANALYTICS.statusBreakdown.pending})</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full rounded-full" style={{ width: '4%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-slate-600">Rejected</span>
                <span className="text-rose-600 font-bold">4% ({ADMIN_ANALYTICS.statusBreakdown.rejected})</span>
              </div>
              <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                <div className="bg-rose-500 h-full rounded-full" style={{ width: '4%' }} />
              </div>
            </div>
          </div>
        </Card>

        {/* Demographics */}
        <Card className="p-5">
          <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            Citizen Demographics
          </h3>
          <div className="space-y-2.5 text-xs text-slate-600">
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Rural vs Urban</span>
              <span className="font-bold text-slate-800">68% Rural / 32% Urban</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Primary Sector</span>
              <span className="font-bold text-slate-800">Agriculture (54%)</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Average Annual Income</span>
              <span className="font-bold text-slate-800">₹1.45 Lakhs</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Direct Benefit Transfer</span>
              <span className="font-bold text-emerald-600">99.2% Aadhaar Linked</span>
            </div>
          </div>
        </Card>

        {/* AI Performance */}
        <Card className="p-5">
          <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-indigo-600" />
            AI Retrieval Metrics
          </h3>
          <div className="space-y-2.5 text-xs text-slate-600">
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Average Latency</span>
              <span className="font-bold text-slate-800">1.24s (Groq LLaMA 3.3)</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">ChromaDB Chunk Precision</span>
              <span className="font-bold text-emerald-600">96.8% Top-3 Relevancy</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Daily Queries Processed</span>
              <span className="font-bold text-slate-800">4,380 queries</span>
            </div>
            <div className="flex justify-between p-2 rounded-lg bg-slate-50">
              <span className="font-medium">Cache Hit Ratio</span>
              <span className="font-bold text-blue-600">42.1%</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default AdminAnalyticsPage;
