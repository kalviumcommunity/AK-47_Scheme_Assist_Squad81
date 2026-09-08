import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  CheckCircle2,
  UploadCloud,
  FileText,
  ShieldCheck,
  ArrowRight,
  ArrowLeft,
  Check,
  Sparkles
} from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Input from '../../components/ui/Input';
import { SCHEMES } from '../../data/schemesData';
import { DEFAULT_CITIZEN } from '../../data/mockCitizenData';

export function ApplicationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [appId] = useState(`APP-2026-${Math.floor(10000 + Math.random() * 90000)}`);

  const scheme = SCHEMES.find((s) => s.id === id) || SCHEMES[0];

  const steps = [
    "Personal Details",
    "Eligibility Check",
    "Document Upload",
    "Review",
    "Submit"
  ];

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-fadeIn pb-16">
      {/* Top Banner */}
      <div className="text-center space-y-1">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Official Government Application
        </span>
        <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
          Apply for {scheme.name}
        </h1>
        <p className="text-xs sm:text-sm text-slate-muted">
          Sanction Grant: <span className="font-bold text-primary">{scheme.benefit}</span> &bull; {scheme.governmentType}
        </p>
      </div>

      {/* 5-Step Progress Indicator */}
      <div className="flex items-center justify-between relative px-2">
        <div className="absolute top-4 left-6 right-6 h-0.5 bg-slate-200 -z-0" />
        {steps.map((label, idx) => {
          const stepNum = idx + 1;
          const isDone = currentStep > stepNum;
          const isCurrent = currentStep === stepNum;
          return (
            <div key={idx} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all shadow-subtle ${
                  isDone
                    ? 'bg-gov-success text-white'
                    : isCurrent
                    ? 'bg-primary text-white ring-4 ring-primary/20'
                    : 'bg-white border border-slate-300 text-slate-400'
                }`}
              >
                {isDone ? <Check className="w-4 h-4" /> : stepNum}
              </div>
              <span className={`text-[10px] sm:text-xs font-semibold mt-1.5 whitespace-nowrap ${
                isCurrent ? 'text-primary' : isDone ? 'text-navy' : 'text-slate-400'
              }`}>
                {label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Step Content */}
      <Card className="p-6 md:p-8 shadow-elevated">
        {/* Step 1: Personal Details */}
        {currentStep === 1 && (
          <div className="space-y-4 animate-fadeIn">
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border">
              Step 1: Verified Citizen Particulars
            </h3>
            <div className="p-3 bg-primary-50/60 border border-primary/20 rounded-btn text-xs text-primary flex items-center gap-2">
              <Sparkles className="w-4 h-4 shrink-0" />
              <span>Details auto-populated from your verified citizen profile.</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <Input label="Applicant Name" value={DEFAULT_CITIZEN.name} readOnly disabled />
              <Input label="Aadhaar Linked Phone" value={DEFAULT_CITIZEN.phone} readOnly disabled />
              <Input label="Date of Birth" value={DEFAULT_CITIZEN.dob} readOnly disabled />
              <Input label="State & District" value={`${DEFAULT_CITIZEN.location.district}, ${DEFAULT_CITIZEN.location.state}`} readOnly disabled />
              <Input label="Annual Family Income" value={`₹${DEFAULT_CITIZEN.financial.familyIncome.toLocaleString()}`} readOnly disabled />
              <Input label="Verified Occupation" value={DEFAULT_CITIZEN.financial.occupation} readOnly disabled />
            </div>
          </div>
        )}

        {/* Step 2: Eligibility Confirmation */}
        {currentStep === 2 && (
          <div className="space-y-4 animate-fadeIn">
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border">
              Step 2: Statutory Eligibility Affirmations
            </h3>

            <div className="space-y-3">
              {[
                { title: "Age Requirement Confirmation", desc: "Applicant confirms meeting age ceiling requirements (18+ years)." },
                { title: "Income & Landholding Thresholds", desc: `Applicant confirms declared family income is below gazetted limit and land records are cultivable.` },
                { title: "Geographic Location & Domicile", desc: "Applicant confirms continuous residence in declared state jurisdiction." },
                { title: "Non-Exclusion Affirmation", desc: "Applicant declares not having been disqualified under institutional taxpayer exclusion rules." },
              ].map((item, i) => (
                <label key={i} className="flex items-start gap-3 p-3.5 rounded-btn bg-slate-bg border border-slate-border cursor-pointer hover:border-primary/40">
                  <input type="checkbox" defaultChecked className="mt-1 w-4 h-4 text-primary rounded focus:ring-primary" />
                  <div>
                    <span className="text-xs font-bold text-navy block">{item.title}</span>
                    <span className="text-[11px] text-slate-muted mt-0.5 block leading-relaxed">{item.desc}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Document Upload */}
        {currentStep === 3 && (
          <div className="space-y-4 animate-fadeIn">
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border">
              Step 3: Document Attestation
            </h3>

            <div className="space-y-3">
              {scheme.requiredDocuments.map((doc, idx) => (
                <div key={idx} className="flex items-center justify-between p-3.5 rounded-btn bg-slate-bg border border-slate-border text-xs">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-primary" />
                    <div>
                      <span className="font-bold text-navy block">{doc}</span>
                      <span className="text-[10px] text-gov-success font-semibold flex items-center gap-1">
                        <Check className="w-3 h-3" /> Auto-attached from verified repository
                      </span>
                    </div>
                  </div>
                  <Badge variant="success" size="sm">Attached</Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Review Application */}
        {currentStep === 4 && (
          <div className="space-y-4 animate-fadeIn">
            <h3 className="text-base font-bold text-navy pb-3 border-b border-slate-border">
              Step 4: Review & Declaration
            </h3>

            <div className="bg-slate-bg p-4 rounded-btn border border-slate-border text-xs space-y-2">
              <div className="flex justify-between pb-1 border-b border-slate-200">
                <span className="text-slate-muted">Applying Scheme:</span>
                <span className="font-bold text-navy">{scheme.name}</span>
              </div>
              <div className="flex justify-between pb-1 border-b border-slate-200">
                <span className="text-slate-muted">Applicant:</span>
                <span className="font-bold text-navy">{DEFAULT_CITIZEN.name}</span>
              </div>
              <div className="flex justify-between pb-1 border-b border-slate-200">
                <span className="text-slate-muted">Direct Benefit Amount:</span>
                <span className="font-bold text-primary">{scheme.benefit}</span>
              </div>
              <div className="flex justify-between pb-1 border-b border-slate-200">
                <span className="text-slate-muted">Attached Documents:</span>
                <span className="font-bold text-gov-success">4 Documents Verified</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-muted">Disbursal Gateway:</span>
                <span className="font-bold text-navy">Direct Benefit Transfer (PFMS DBT)</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 italic">
              By clicking "Submit Application", I certify under penalty of perjury that all particulars submitted herein are true and accurate.
            </p>
          </div>
        )}

        {/* Step 5: Success Confirmation */}
        {currentStep === 5 && (
          <div className="text-center py-6 space-y-4 animate-fadeIn">
            <div className="w-16 h-16 rounded-full bg-gov-success text-white flex items-center justify-center mx-auto shadow-elevated">
              <Check className="w-8 h-8 stroke-[3]" />
            </div>

            <div className="space-y-1">
              <Badge variant="success" size="md">Application Submitted</Badge>
              <h3 className="text-2xl font-black text-navy mt-2">
                Application Submitted Successfully 🎉
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 max-w-md mx-auto">
                Your application for <span className="font-bold text-navy">{scheme.name}</span> has been dispatched to the State Nodal Officer for verification.
              </p>
            </div>

            <div className="inline-block p-4 rounded-card bg-slate-bg border border-slate-border text-center">
              <span className="text-xs text-slate-400 font-semibold block uppercase tracking-wider">Application Tracking ID</span>
              <span className="text-xl font-black font-mono text-primary mt-1 block">{appId}</span>
            </div>

            <div className="pt-4 flex justify-center gap-3">
              <Button variant="primary" size="md" onClick={() => navigate('/applications')}>
                Track Application &rarr;
              </Button>
            </div>
          </div>
        )}

        {/* Action Controls */}
        {currentStep < 5 && (
          <div className="flex items-center justify-between pt-6 border-t border-slate-border mt-8">
            {currentStep > 1 ? (
              <Button
                variant="outline"
                size="md"
                icon={ArrowLeft}
                onClick={() => setCurrentStep((prev) => prev - 1)}
              >
                Previous
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="md"
                onClick={() => navigate(-1)}
              >
                Cancel
              </Button>
            )}

            <Button
              variant="primary"
              size="md"
              onClick={() => setCurrentStep((prev) => prev + 1)}
            >
              {currentStep === 4 ? "Submit Application" : "Next"}
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}

export default ApplicationPage;
