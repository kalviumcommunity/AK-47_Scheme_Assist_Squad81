import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Share2,
  Bookmark,
  CheckCircle2,
  Calendar,
  FileText,
  HelpCircle,
  Sparkles,
  Building,
  Layers,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { SCHEMES } from '../../data/schemesData';

export function SchemeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isSaved, setIsSaved] = useState(false);
  const [expandedFaq, setExpandedFaq] = useState(null);

  const scheme = SCHEMES.find((s) => s.id === id) || SCHEMES[0];

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      alert("Scheme URL copied to clipboard!");
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Top Bar with Back Button */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-border">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-navy transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Schemes</span>
        </button>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            icon={Share2}
            onClick={handleShare}
          >
            Share
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={Bookmark}
            onClick={() => setIsSaved(!isSaved)}
            className={isSaved ? 'text-gov-warning bg-gov-warning-light' : ''}
          >
            {isSaved ? 'Saved' : 'Save Scheme'}
          </Button>
        </div>
      </div>

      {/* Scheme Header Banner */}
      <div className="bg-white border border-slate-border rounded-card p-6 shadow-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-card bg-primary-50 border border-primary/20 flex items-center justify-center text-primary font-black text-xl shrink-0">
            SA
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                {scheme.category}
              </span>
              <span className="text-slate-300">&bull;</span>
              <span className="text-xs text-slate-500 font-medium">
                {scheme.governmentType}
              </span>
            </div>
            <h1 className="text-2xl font-black text-navy mt-0.5 tracking-tight">
              {scheme.fullName || scheme.name}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
          <Badge variant="success" size="md" dot>
            Active Scheme
          </Badge>
          <Badge variant="primary" size="md">
            {scheme.matchScore}% Match
          </Badge>
        </div>
      </div>

      {/* Main Grid: Details + Quick Info Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Scheme In-depth Details (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Overview */}
          <Card>
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border mb-3">
              Overview & Background
            </h3>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
              {scheme.overview}
            </p>
          </Card>

          {/* Benefits */}
          <Card>
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border mb-3">
              Key Benefits & Disbursals
            </h3>
            <div className="space-y-2.5">
              {scheme.benefits.map((b, i) => (
                <div key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-gov-success shrink-0 mt-0.5" />
                  <span>{b}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Eligibility Criteria */}
          <Card>
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border mb-3">
              Eligibility Criteria
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3 rounded-btn bg-slate-bg border border-slate-border">
                <span className="text-slate-400 font-semibold block uppercase text-[10px]">Target Group</span>
                <span className="font-bold text-navy mt-1 block">{scheme.eligibility.targetGroup}</span>
              </div>
              <div className="p-3 rounded-btn bg-slate-bg border border-slate-border">
                <span className="text-slate-400 font-semibold block uppercase text-[10px]">Age Ceiling</span>
                <span className="font-bold text-navy mt-1 block">{scheme.eligibility.ageRange}</span>
              </div>
              <div className="p-3 rounded-btn bg-slate-bg border border-slate-border">
                <span className="text-slate-400 font-semibold block uppercase text-[10px]">Income Limit</span>
                <span className="font-bold text-navy mt-1 block">{scheme.eligibility.incomeLimit}</span>
              </div>
              <div className="p-3 rounded-btn bg-slate-bg border border-slate-border">
                <span className="text-slate-400 font-semibold block uppercase text-[10px]">Occupation</span>
                <span className="font-bold text-navy mt-1 block">{scheme.eligibility.occupation}</span>
              </div>
            </div>
          </Card>

          {/* Required Documents */}
          <Card>
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border mb-3">
              Required Documents
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
              {scheme.requiredDocuments.map((doc, idx) => (
                <div key={idx} className="flex items-center gap-2 p-2.5 rounded-btn bg-slate-50 border border-slate-border text-slate-700 font-medium">
                  <FileText className="w-4 h-4 text-primary shrink-0" />
                  <span>{doc}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Application Process */}
          <Card>
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border mb-3">
              Application Process & Workflow
            </h3>
            <div className="space-y-3">
              {scheme.applicationProcess.map((step, idx) => (
                <div key={idx} className="flex items-start gap-3 text-xs">
                  <span className="w-6 h-6 rounded-full bg-navy text-white flex items-center justify-center font-bold shrink-0 text-[11px]">
                    {idx + 1}
                  </span>
                  <p className="text-slate-700 leading-relaxed pt-0.5">{step}</p>
                </div>
              ))}
            </div>
          </Card>

          {/* FAQs */}
          {scheme.faqs && scheme.faqs.length > 0 && (
            <Card>
              <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border mb-3">
                Frequently Asked Questions
              </h3>
              <div className="divide-y divide-slate-100">
                {scheme.faqs.map((faq, idx) => (
                  <div key={idx} className="py-3">
                    <button
                      onClick={() => setExpandedFaq(expandedFaq === idx ? null : idx)}
                      className="flex items-center justify-between w-full text-left text-xs sm:text-sm font-bold text-navy"
                    >
                      <span>{faq.question}</span>
                      {expandedFaq === idx ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                    </button>
                    {expandedFaq === idx && (
                      <p className="text-xs text-slate-600 mt-2 leading-relaxed bg-slate-bg p-3 rounded-btn">
                        {faq.answer}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column: Quick Info Sidebar (4 cols) */}
        <div className="lg:col-span-4 space-y-6 sticky top-20">
          <Card className="space-y-4 shadow-elevated">
            <h3 className="text-sm font-bold text-navy pb-3 border-b border-slate-border">
              Quick Information
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between pb-2 border-b border-slate-100">
                <span className="text-slate-muted">Financial Benefit</span>
                <span className="font-bold text-primary">{scheme.benefit}</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-slate-100">
                <span className="text-slate-muted">Category</span>
                <span className="font-bold text-navy">{scheme.category}</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-slate-100">
                <span className="text-slate-muted">Government</span>
                <span className="font-bold text-navy">{scheme.governmentType}</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-slate-100">
                <span className="text-slate-muted">Application Mode</span>
                <span className="font-bold text-navy">{scheme.applicationMode}</span>
              </div>
            </div>

            <div className="pt-2 space-y-2.5">
              <Button
                variant="primary"
                size="md"
                className="w-full"
                onClick={() => navigate(`/apply/${scheme.id}`)}
              >
                Apply Now &rarr;
              </Button>
              <Button
                variant="secondary"
                size="md"
                icon={Sparkles}
                className="w-full"
                onClick={() => navigate('/ai-assistant')}
              >
                Ask AI About This Scheme
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default SchemeDetailPage;
