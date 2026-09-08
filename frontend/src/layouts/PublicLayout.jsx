import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Shield, Globe, Award, HelpCircle } from 'lucide-react';
import Button from '../components/ui/Button';

export function PublicLayout() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-slate-bg text-slate-text">
      {/* Top Banner (Govt Notice style) */}
      <div className="bg-navy-900 text-slate-300 text-[11px] py-1.5 px-4 text-center font-medium border-b border-navy-800 flex items-center justify-center gap-2">
        <span className="w-2 h-2 rounded-full bg-gov-success animate-pulse" />
        <span>Official Citizen Welfare Digital Advisory Gateway &bull; Powered by SchemeAssist AI &bull; Ministry Guidelines 2026</span>
      </div>

      {/* Public Navbar */}
      <header className="h-18 bg-white border-b border-slate-border sticky top-0 z-40 shadow-subtle">
        <div className="max-w-7xl mx-auto px-4 md:px-8 h-full flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-btn bg-navy text-white flex items-center justify-center font-extrabold text-xl shadow-sm">
              SA
            </div>
            <div>
              <span className="text-lg font-black text-navy tracking-tight leading-none block">
                SchemeAssist
              </span>
              <span className="text-[11px] font-semibold text-slate-muted block tracking-wide">
                AI Welfare Eligibility Platform
              </span>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-text">
            <Link to="/" className="hover:text-primary transition-colors">Home</Link>
            <a href="#how-it-works" className="hover:text-primary transition-colors">How It Works</a>
            <Link to="/schemes" className="hover:text-primary transition-colors">Schemes</Link>
            <a href="#about" className="hover:text-primary transition-colors">About</a>
            <Link to="/helpdesk" className="hover:text-primary transition-colors">Help</Link>
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="hidden sm:inline-flex"
            >
              Sign In
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Sparkles}
              onClick={() => navigate('/onboarding')}
            >
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1">
        <Outlet />
      </div>

      {/* Public Footer */}
      <footer className="bg-navy text-white pt-16 pb-12 border-t border-navy-800">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-10 pb-12 border-b border-navy-800">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-btn bg-white text-navy flex items-center justify-center font-extrabold text-lg">
                  SA
                </div>
                <span className="text-xl font-extrabold tracking-tight">SchemeAssist</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Empowering millions of citizens with automated AI welfare eligibility analysis, document intelligence, and personalized government scheme discovery.
              </p>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Shield className="w-4 h-4 text-gov-success" />
                <span>Verified Official Knowledge Base</span>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Quick Schemes</h4>
              <ul className="space-y-2 text-xs text-slate-300">
                <li><Link to="/schemes" className="hover:text-white transition-colors">PM-KISAN Samman Nidhi</Link></li>
                <li><Link to="/schemes" className="hover:text-white transition-colors">Ayushman Bharat PM-JAY</Link></li>
                <li><Link to="/schemes" className="hover:text-white transition-colors">PMAY Housing for All</Link></li>
                <li><Link to="/schemes" className="hover:text-white transition-colors">PM Vishwakarma Yojana</Link></li>
                <li><Link to="/schemes" className="hover:text-white transition-colors">Old Age Pension Scheme</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Citizen Services</h4>
              <ul className="space-y-2 text-xs text-slate-300">
                <li><Link to="/onboarding" className="hover:text-white transition-colors">Complete Citizen Profile</Link></li>
                <li><Link to="/ai-analysis" className="hover:text-white transition-colors">AI Eligibility Engine</Link></li>
                <li><Link to="/ai-assistant" className="hover:text-white transition-colors">Chat with Scheme AI</Link></li>
                <li><Link to="/documents" className="hover:text-white transition-colors">Manage Official Documents</Link></li>
                <li><Link to="/helpdesk" className="hover:text-white transition-colors">Citizen Helpdesk & Grievance</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Official Helpdesk</h4>
              <p className="text-xs text-slate-300 mb-2">National Welfare Toll-Free Number:</p>
              <p className="text-base font-extrabold text-primary-light mb-3">1800-111-565 / 14555</p>
              <p className="text-xs text-slate-400">Operating hours: 24x7 all days in 12 official regional languages.</p>
            </div>
          </div>

          <div className="pt-8 flex flex-col md:flex-row items-center justify-between text-xs text-slate-400 gap-4">
            <p>&copy; 2026 SchemeAssist Platform. Government Welfare Eligibility and Guidance Initiative.</p>
            <div className="flex gap-6">
              <span className="hover:text-white cursor-pointer">Privacy Policy</span>
              <span className="hover:text-white cursor-pointer">Terms of Service</span>
              <span className="hover:text-white cursor-pointer">Accessibility Statement</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default PublicLayout;
