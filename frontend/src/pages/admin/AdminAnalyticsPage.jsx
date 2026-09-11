import React from 'react';
import Card from '../../components/ui/Card';
import { BarChart3 } from 'lucide-react';

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
            Backend analytics will appear here when the corresponding metrics endpoint is available.
          </p>
        </div>
      </div>
      <Card className="p-8 text-center"><p className="text-sm font-bold text-navy">No analytics data available yet.</p><p className="text-xs text-slate-muted mt-2">This view is ready for real query, response-time, and answer-mode metrics from a future backend analytics endpoint.</p></Card>
    </div>
  );
}

export default AdminAnalyticsPage;
