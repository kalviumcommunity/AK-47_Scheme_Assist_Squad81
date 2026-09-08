import React, { useState } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import { Settings, Shield, Bell, Database, Cpu, Lock, Check } from 'lucide-react';

export function AdminSettingsPage() {
  const [saved, setSaved] = useState(false);
  const [ragModel, setRagModel] = useState('llama-3.3-70b-versatile');
  const [chunkK, setChunkK] = useState(3);
  const [notifyEmail, setNotifyEmail] = useState(true);
  const [autoApproveLowRisk, setAutoApproveLowRisk] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-black text-slate-800">Admin Portal Configuration</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">Configure AI engine parameters, security rules, and platform notifications</p>
        </div>
      </div>

      {saved && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs flex items-center gap-2 font-semibold">
          <Check className="w-4 h-4 text-emerald-600" />
          Settings successfully updated and applied across platform nodes.
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* AI & RAG Configuration */}
        <Card className="p-5 space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
            <Cpu className="w-5 h-5 text-indigo-600" />
            <div>
              <h3 className="text-sm font-bold text-slate-800">RAG & LLM Engine Settings</h3>
              <p className="text-xs text-slate-400">Control Groq inference parameters and vector retrieval density</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">Groq Inference Model</label>
              <select
                value={ragModel}
                onChange={(e) => setRagModel(e.target.value)}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white font-medium text-slate-800 focus:ring-2 focus:ring-blue-500"
              >
                <option value="llama-3.3-70b-versatile">LLaMA 3.3 70B Versatile (Recommended)</option>
                <option value="llama-3.1-8b-instant">LLaMA 3.1 8B Instant (Low Latency)</option>
                <option value="mixtral-8x7b-32768">Mixtral 8x7B (Long Context)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1.5">ChromaDB Top-K Context Chunks</label>
              <input
                type="number"
                min="1"
                max="10"
                value={chunkK}
                onChange={(e) => setChunkK(Number(e.target.value))}
                className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white font-medium text-slate-800 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </Card>

        {/* Security & Access */}
        <Card className="p-5 space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
            <Shield className="w-5 h-5 text-emerald-600" />
            <div>
              <h3 className="text-sm font-bold text-slate-800">Security & Portal Restrictions</h3>
              <p className="text-xs text-slate-400">Manage administrative session timeouts and verification policies</p>
            </div>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 rounded-xl bg-slate-50 cursor-pointer">
              <div>
                <p className="text-xs font-bold text-slate-800">Role-Based Access Enforcement (RBAC)</p>
                <p className="text-[11px] text-slate-500">Isolate citizen sessions completely from administrative endpoints</p>
              </div>
              <input type="checkbox" defaultChecked disabled className="w-4 h-4 rounded text-blue-600" />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-slate-50 cursor-pointer">
              <div>
                <p className="text-xs font-bold text-slate-800">Auto-Approve Low Risk Renewals</p>
                <p className="text-[11px] text-slate-500">Fast-track verified beneficiaries who meet all eligibility criteria with zero delta</p>
              </div>
              <input
                type="checkbox"
                checked={autoApproveLowRisk}
                onChange={(e) => setAutoApproveLowRisk(e.target.checked)}
                className="w-4 h-4 rounded text-blue-600"
              />
            </label>
          </div>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" variant="primary">
            Save System Configuration
          </Button>
        </div>
      </form>
    </div>
  );
}

export default AdminSettingsPage;
