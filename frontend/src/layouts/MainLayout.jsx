import React, { useState } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import TopNavbar from '../components/layout/TopNavbar';
import NotificationDrawer from '../components/layout/NotificationDrawer';

export function MainLayout() {
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-bg text-slate-text">
      <TopNavbar onToggleNotifications={() => setNotificationsOpen(true)} />

      <main className="flex-1">
        <div className="mx-auto w-full max-w-7xl px-4 py-6 md:px-8 lg:px-10">
          <Outlet />
        </div>
      </main>

      <footer className="mt-10 bg-navy text-white">
        <div className="mx-auto max-w-7xl px-4 py-12 md:px-8 lg:px-10">
          <div className="grid gap-10 border-b border-navy-800 pb-10 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-lg font-black text-navy">
                  SA
                </div>
                <div>
                  <div className="text-xl font-black tracking-tight">SchemeAssist</div>
                  <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                    AI Government Scheme Assistant
                  </div>
                </div>
              </div>

              <p className="text-sm leading-relaxed text-slate-300">
                Explore welfare schemes, understand eligibility, upload documents, and get trusted guidance from an AI-powered government platform.
              </p>

              <div className="inline-flex items-center gap-2 rounded-full border border-gov-success/30 bg-gov-success/10 px-3 py-1.5 text-xs font-semibold text-gov-success">
                <ShieldCheck className="h-4 w-4" />
                Verified Government Guidance
              </div>
            </div>

            <div>
              <h3 className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                Platform
              </h3>
              <ul className="space-y-3 text-sm text-slate-300">
                <li><Link to="/dashboard" className="transition-colors hover:text-white">Home</Link></li>
                <li><Link to="/schemes" className="transition-colors hover:text-white">Find Schemes</Link></li>
                <li><Link to="/ai-analysis" className="transition-colors hover:text-white">AI Analysis</Link></li>
                <li><Link to="/documents" className="transition-colors hover:text-white">Documents</Link></li>
                <li><Link to="/ai-assistant" className="transition-colors hover:text-white">AI Assistant</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                Support
              </h3>
              <ul className="space-y-3 text-sm text-slate-300">
                <li><Link to="/helpdesk" className="transition-colors hover:text-white">Helpdesk</Link></li>
                <li><Link to="/settings" className="transition-colors hover:text-white">Settings</Link></li>
                <li><Link to="/applications" className="transition-colors hover:text-white">My Applications</Link></li>
                <li><Link to="/schemes" className="transition-colors hover:text-white">Eligibility Guide</Link></li>
                <li><Link to="/dashboard" className="transition-colors hover:text-white">Privacy Policy</Link></li>
              </ul>
            </div>

            <div>
              <h3 className="mb-4 text-xs font-bold uppercase tracking-[0.2em] text-slate-400">
                Trust & Resources
              </h3>
              <div className="space-y-3 text-sm text-slate-300">
                <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 p-3">
                  <Sparkles className="h-4 w-4 text-primary-light" />
                  <span>AI-Powered Assistance</span>
                </div>
                <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 p-3">
                  <ShieldCheck className="h-4 w-4 text-gov-success" />
                  <span>Secure Documents</span>
                </div>
                <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 p-3">
                  <ArrowRight className="h-4 w-4 text-primary-light" />
                  <span>Government Scheme Guidance</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-4 pt-6 text-xs text-slate-400 md:flex-row md:items-center md:justify-between">
            <p>© 2026 SchemeAssist. All rights reserved.</p>
            <div className="flex flex-wrap items-center gap-4">
              <span>Privacy Policy</span>
              <span>Terms of Service</span>
              <span>Disclaimer</span>
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-700 bg-slate-800/40 p-3 text-xs leading-relaxed text-slate-300">
            SchemeAssist provides AI-powered guidance based on available government scheme information. Eligibility and benefits are subject to official government verification and applicable rules.
          </div>
        </div>
      </footer>

      <NotificationDrawer
        isOpen={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
      />
    </div>
  );
}

export default MainLayout;
