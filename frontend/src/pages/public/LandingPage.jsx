import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Search,
  FileCheck2,
  FolderLock,
  BotMessageSquare,
  Users,
  Award,
  CheckCircle2,
  ChevronRight,
  Landmark,
  Layers,
  FileText
} from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { SCHEMES } from '../../data/schemesData';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 md:pt-20 pb-12 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column */}
            <div className="lg:col-span-7 space-y-6 text-left">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-50 border border-primary/20 text-primary text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Next-Gen Welfare Intelligence</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-navy leading-[1.1] tracking-tight">
                Find Government Schemes <br className="hidden sm:inline" />
                <span className="text-primary underline decoration-primary/20 decoration-wavy">Made for You</span>
              </h1>

              <p className="text-base sm:text-lg text-slate-600 max-w-xl leading-relaxed">
                Discover welfare schemes, check your eligibility, and get personalized guidance powered by AI. Never miss out on benefits guaranteed for your family.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
                <Button
                  variant="primary"
                  size="lg"
                  icon={ArrowRight}
                  onClick={() => navigate('/onboarding')}
                >
                  Get Started Free
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => navigate('/schemes')}
                >
                  Explore 450+ Schemes
                </Button>
              </div>

              {/* Citizen trust note */}
              <div className="pt-4 flex items-center gap-4 text-xs text-slate-500">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 rounded-full bg-navy text-white flex items-center justify-center font-bold text-[10px] ring-2 ring-white">RK</div>
                  <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-bold text-[10px] ring-2 ring-white">SV</div>
                  <div className="w-8 h-8 rounded-full bg-gov-success text-white flex items-center justify-center font-bold text-[10px] ring-2 ring-white">AG</div>
                </div>
                <div>
                  <span className="font-bold text-slate-700">Trusted by 2.4M+ citizens</span> across all 28 states and union territories.
                </div>
              </div>
            </div>

            {/* Right Column: High-fidelity Illustration & Interactive Mockup */}
            <div className="lg:col-span-5 relative">
              <div className="absolute -inset-2 bg-gradient-to-r from-primary/10 to-navy/10 rounded-2xl blur-xl" />
              <div className="relative bg-white border border-slate-border rounded-2xl p-6 shadow-elevated space-y-4">
                {/* Government AI Card preview */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-border">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-btn bg-navy text-white flex items-center justify-center font-bold text-xs">
                      AI
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-navy">Eligibility Engine</h4>
                      <span className="text-[10px] text-gov-success flex items-center gap-1 font-semibold">
                        <span className="w-1.5 h-1.5 rounded-full bg-gov-success animate-pulse" /> Live Analysis
                      </span>
                    </div>
                  </div>
                  <Badge variant="success" size="sm">95% Match Score</Badge>
                </div>

                {/* Scheme Sample Preview */}
                <div className="p-4 rounded-xl bg-slate-bg border border-slate-border space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-500 uppercase">Recommended Scheme</span>
                    <span className="text-xs font-black text-primary">₹6,000 / Year</span>
                  </div>
                  <h3 className="text-sm font-bold text-navy">PM-KISAN Direct Support</h3>
                  <p className="text-xs text-slate-600 leading-snug">
                    Verified landholding agricultural support transferred directly via Aadhaar Direct Benefit Transfer gateway.
                  </p>
                </div>

                {/* Simulated Verification checklist */}
                <div className="space-y-2 pt-1 text-xs">
                  <div className="flex items-center justify-between p-2 rounded-btn bg-gov-success-light text-gov-success font-medium">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Landholding verified</span>
                    </div>
                    <span className="text-[10px] font-bold">Passed</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-btn bg-gov-success-light text-gov-success font-medium">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>SECC Deprivation criteria</span>
                    </div>
                    <span className="text-[10px] font-bold">Passed</span>
                  </div>
                </div>

                <div className="pt-2">
                  <Button
                    variant="navy"
                    size="sm"
                    className="w-full"
                    onClick={() => navigate('/ai-assistant')}
                  >
                    Ask SchemeAssist AI &rarr;
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Statistics Section */}
      <section className="bg-navy text-white py-12 border-y border-navy-800">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-3xl md:text-4xl font-black text-primary-light">450+</p>
              <p className="text-xs md:text-sm text-slate-300 font-medium mt-1">Government Schemes</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-black text-gov-success">2.4M</p>
              <p className="text-xs md:text-sm text-slate-300 font-medium mt-1">Citizens Supported</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-black text-gov-warning">93%</p>
              <p className="text-xs md:text-sm text-slate-300 font-medium mt-1">Eligibility Accuracy</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-black text-primary-light">₹12M+</p>
              <p className="text-xs md:text-sm text-slate-300 font-medium mt-1">Benefits Discovered</p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section - 4 Feature Cards */}
      <section className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12 space-y-2">
          <Badge variant="primary" size="sm">Comprehensive Capabilities</Badge>
          <h2 className="text-3xl font-bold text-navy">Engineered for Citizen Empowerment</h2>
          <p className="text-sm text-slate-600">
            From discovering obscure circulars to tracking DBT disbursement, every step is streamlined.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card hoverEffect className="space-y-3">
            <div className="w-12 h-12 rounded-btn bg-primary-50 text-primary flex items-center justify-center border border-primary/20">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-navy">AI Scheme Discovery</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Instantly find relevant central and state schemes filtered precisely by your occupation, income, and region.
            </p>
          </Card>

          <Card hoverEffect className="space-y-3">
            <div className="w-12 h-12 rounded-btn bg-gov-success-light text-gov-success flex items-center justify-center border border-gov-success/20">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-navy">Eligibility Analysis</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Our automated rules and vector pipeline analyze your personal and financial profile against gazetted criteria.
            </p>
          </Card>

          <Card hoverEffect className="space-y-3">
            <div className="w-12 h-12 rounded-btn bg-navy/10 text-navy flex items-center justify-center border border-navy/20">
              <FileCheck2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-navy">Application Guidance</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Step-by-step interactive instructions ensure your forms, declarations, and certificates are error-free.
            </p>
          </Card>

          <Card hoverEffect className="space-y-3">
            <div className="w-12 h-12 rounded-btn bg-gov-warning-light text-gov-warning flex items-center justify-center border border-gov-warning/20">
              <FolderLock className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-navy">Document Management</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Safely store, verify, and reuse your Aadhaar, income certificates, and land records across multiple welfare applications.
            </p>
          </Card>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="bg-white border border-slate-border rounded-2xl p-8 md:p-12 shadow-subtle">
          <div className="text-center max-w-xl mx-auto mb-10 space-y-2">
            <Badge variant="navy" size="sm">Simple 4-Step Process</Badge>
            <h2 className="text-2xl md:text-3xl font-bold text-navy">How SchemeAssist Works</h2>
            <p className="text-xs md:text-sm text-slate-600">
              From initial registration to direct benefit transfer in 4 clear milestones.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative">
            <div className="p-4 rounded-xl bg-slate-bg border border-slate-border relative space-y-3">
              <span className="w-7 h-7 rounded-full bg-navy text-white flex items-center justify-center text-xs font-black">1</span>
              <h4 className="text-sm font-bold text-navy">Create Your Profile</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Provide basic demographic, location, and occupational details in a simple 2-minute wizard.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-bg border border-slate-border relative space-y-3">
              <span className="w-7 h-7 rounded-full bg-primary text-white flex items-center justify-center text-xs font-black">2</span>
              <h4 className="text-sm font-bold text-navy">AI Analyzes Eligibility</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                RAG intelligence scans verified ministry databases to calculate exact match percentages.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-bg border border-slate-border relative space-y-3">
              <span className="w-7 h-7 rounded-full bg-gov-warning text-white flex items-center justify-center text-xs font-black">3</span>
              <h4 className="text-sm font-bold text-navy">Discover Schemes</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Review tailored scheme cards, comparison tables, financial benefits, and required paperwork.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-bg border border-slate-border relative space-y-3">
              <span className="w-7 h-7 rounded-full bg-gov-success text-white flex items-center justify-center text-xs font-black">4</span>
              <h4 className="text-sm font-bold text-navy">Apply Successfully</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Submit multi-step applications online and track verification status directly in real-time.
              </p>
            </div>
          </div>

          <div className="mt-10 text-center">
            <Button
              variant="primary"
              size="lg"
              onClick={() => navigate('/onboarding')}
            >
              Start Eligibility Assessment &rarr;
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
