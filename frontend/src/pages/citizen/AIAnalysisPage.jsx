import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles, User, Wallet, Users, CheckCircle2,
  Cpu, ShieldCheck, Database, BarChart3, Award,
  ArrowRight, ArrowLeft, AlertCircle, ExternalLink,
  Filter, Check, Layers, ChevronRight, HelpCircle,
  TrendingUp, IndianRupee, FileCheck, CheckCheck
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import { useAuth } from '../../context/AuthContext';
import { SCHEMES, SCHEME_CATEGORIES } from '../../data/schemesData';
import SchemeCard from '../../components/dashboard/SchemeCard';

const STEPS = ['Personal Info', 'Financial Info', 'Family & Category', 'AI Analysis'];

const PIPELINE_STAGES = [
  { title: 'Analyzing Profile', desc: 'Extracting income, occupation & landholding tokens', icon: Cpu },
  { title: 'Matching Eligibility Rules', desc: 'Cross-referencing central & state welfare thresholds', icon: ShieldCheck },
  { title: 'Searching Government Schemes', desc: 'ChromaDB vector similarity search over gazettes', icon: Database },
  { title: 'Calculating Match Score', desc: 'Computing weighted cosine & rule-fit percentages', icon: BarChart3 },
  { title: 'Generating Recommendations', desc: 'Synthesizing personalized citizen action plan', icon: Award },
];

const STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat',
  'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
  'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu & Kashmir', 'Ladakh',
];

const inputCls = 'w-full px-3.5 py-2.5 border border-slate-200 rounded-btn text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition bg-white';
const labelCls = 'block text-xs font-bold uppercase tracking-wide text-slate-600 mb-1.5';
const selectCls = inputCls + ' cursor-pointer';

function FieldGroup({ children, cols = 2 }) {
  return (
    <div className={`grid grid-cols-1 ${cols === 2 ? 'md:grid-cols-2' : 'md:grid-cols-3'} gap-4`}>
      {children}
    </div>
  );
}

function CheckBox({ id, label, checked, onChange }) {
  return (
    <label htmlFor={id} className="flex items-center gap-2.5 cursor-pointer group">
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
      />
      <span className="text-sm text-slate-700 group-hover:text-slate-900">{label}</span>
    </label>
  );
}

/**
 * calculateEligibility: Evaluates citizen profile parameters against government scheme
 * thresholds and cross-references with RAG output.
 */
function calculateEligibility(profile, ragResult) {
  const age = parseInt(profile.age, 10) || 0;
  const income = parseInt(profile.annualIncome, 10) || 0;
  const land = parseFloat(profile.landHolding) || 0;
  const occupation = (profile.occupation || '').toLowerCase();
  const gender = (profile.gender || '').toLowerCase();
  const category = (profile.category || '').toUpperCase().split(' ')[0];
  const isBPL = !!profile.hasBPL;
  const isRation = !!profile.hasRationCard;
  const isFarmer = !!profile.hasFarmerCard || occupation.includes('farm') || occupation.includes('agri') || land > 0;
  const isStudent = !!profile.isStudent || occupation.includes('student');
  const isWidow = !!profile.isWidow;
  const hasDisability = !!profile.hasDisability;

  const ragText = (
    (ragResult?.answer || '') + ' ' +
    (ragResult?.sources || []).map((s) => s.source || '').join(' ')
  ).toLowerCase();

  return SCHEMES.map((scheme) => {
    let score = 35; // base baseline
    const reasons = [];
    const id = scheme.id;

    if (id === 'pm-kisan') {
      if (isFarmer || land > 0) {
        score += 50;
        reasons.push(land > 0 ? `Cultivable landholding: ${land} acres reported` : 'Registered agricultural / farmer profile');
      }
      if (age >= 18 && age <= 75) {
        score += 15;
        reasons.push(`Applicant age (${age}) is within eligible landholder range (18-75)`);
      }
      if (income > 0 && income < 1000000) {
        score += 10;
        reasons.push('Meets non-institutional landholder income rules');
      }
    } else if (id === 'pm-fasal-bima') {
      if (isFarmer || land > 0) {
        score += 55;
        reasons.push('Direct crop loss risk coverage for notified operational land');
      }
      if (age >= 18) {
        score += 15;
      }
      if (profile.hasFarmerCard) {
        score += 15;
        reasons.push('Linked Kisan Credit Card / farmer enrollment');
      }
    } else if (id === 'ayushman-bharat') {
      if (isBPL || isRation) {
        score += 45;
        reasons.push('BPL / Priority Ration Card holder eligible under SECC deprivation criteria');
      }
      if (income > 0 && income <= 300000) {
        score += 30;
        reasons.push(`Annual income ₹${income.toLocaleString('en-IN')} meets vulnerable economic criteria`);
      } else if (income <= 600000) {
        score += 20;
        reasons.push('Eligible under state-extended health coverage criteria');
      }
      if (['SC', 'ST', 'OBC'].includes(category)) {
        score += 10;
        reasons.push(`Affirmative social category (${category}) inclusion`);
      }
      if (hasDisability) {
        score += 10;
        reasons.push('Disability healthcare entitlement benefit');
      }
    } else if (id === 'pm-awas-yojana') {
      if (isBPL) {
        score += 40;
        reasons.push('BPL housing assistance queue priority');
      }
      if (income > 0 && income <= 300000) {
        score += 35;
        reasons.push('Economically Weaker Section (EWS) pucca housing direct grant');
      } else if (income <= 600000) {
        score += 25;
        reasons.push('Low Income Group (LIG) credit-linked interest subsidy');
      }
      if (age >= 21) {
        score += 15;
        reasons.push('Meets primary applicant age requirement (≥ 21 years)');
      }
    } else if (id === 'pm-vishwakarma') {
      const trades = ['artisan', 'craft', 'carpenter', 'blacksmith', 'tailor', 'barber', 'potter', 'mason', 'labor', 'labour', 'welder', 'worker', 'mechanic', 'carpentry', 'electrician'];
      if (trades.some((t) => occupation.includes(t))) {
        score += 55;
        reasons.push(`Occupation (${profile.occupation}) matches traditional artisan & craftsman trade`);
      } else if (!occupation.includes('govt') && !occupation.includes('student')) {
        score += 30;
        reasons.push('Informal unorganized worker eligible for trade registration');
      }
      if (age >= 18) score += 15;
      if (income <= 500000) score += 10;
    } else if (id === 'pm-svanidhi') {
      const vendorKeywords = ['vendor', 'hawker', 'street', 'shop', 'trader', 'business', 'driver', 'daily', 'labor', 'labour', 'self'];
      if (vendorKeywords.some((k) => occupation.includes(k))) {
        score += 55;
        reasons.push(`Self-employed / informal worker (${profile.occupation}) eligible for micro-credit`);
      } else if (!occupation.includes('govt') && !occupation.includes('student')) {
        score += 25;
      }
      if (age >= 18) score += 15;
      if (income <= 400000) score += 15;
    } else if (id === 'senior-citizen-pension') {
      if (age >= 60) {
        score += 55;
        reasons.push(`Senior citizen age requirement fulfilled (${age} years ≥ 60)`);
        if (isBPL) {
          score += 35;
          reasons.push('BPL status fulfills IGNOAPS non-contributory pension rule');
        } else if (income <= 200000) {
          score += 25;
          reasons.push('Income within state pension threshold');
        }
      } else {
        score = 15; // Age not met
      }
    } else if (id === 'nsp-scholarship') {
      if (isStudent || (age >= 15 && age <= 28)) {
        score += 50;
        reasons.push(isStudent ? 'Active student enrollment declared' : `Age ${age} within post-matric higher education window`);
        if (income > 0 && income <= 250000) {
          score += 35;
          reasons.push(`Household income (₹${income.toLocaleString('en-IN')}) within ₹2.5 Lakh limit`);
        } else if (income <= 450000) {
          score += 20;
        }
      } else {
        score = 10;
      }
    } else if (id === 'pm-ujjwala') {
      if (gender === 'female' || isWidow) {
        score += 45;
        reasons.push('Adult woman applicant fulfills primary beneficiary rule');
      }
      if (isBPL || isRation) {
        score += 35;
        reasons.push('BPL / Ration card priority for deposit-free LPG');
      }
      if (['SC', 'ST'].includes(category)) {
        score += 15;
        reasons.push(`Priority under affirmative welfare quota (${category})`);
      }
      if (gender === 'male' && !isBPL) {
        score = Math.min(score, 35);
      }
    } else if (id === 'atal-pension') {
      if (age >= 18 && age <= 40) {
        score += 55;
        reasons.push(`Age ${age} falls within APY joining window (18-40 years)`);
        if (!occupation.includes('govt')) {
          score += 25;
          reasons.push('Unorganized worker eligible for guaranteed lifelong pension');
        }
      } else {
        score = 15;
      }
    } else if (id === 'sukanya-samriddhi') {
      if (parseInt(profile.familySize, 10) >= 3 || gender === 'female') {
        score += 45;
        reasons.push('Small savings sovereign deposit for girl child education & future');
        if (income <= 600000) score += 25;
      }
    }

    // Check RAG query boost
    const nameLower = scheme.name.toLowerCase();
    const fullLower = scheme.fullName ? scheme.fullName.toLowerCase() : '';
    let ragVerified = false;

    if (
      (nameLower && ragText.includes(nameLower)) ||
      (fullLower && ragText.includes(fullLower)) ||
      (id === 'pm-kisan' && (ragText.includes('kisan') || ragText.includes('pmkisan'))) ||
      (id === 'ayushman-bharat' && (ragText.includes('ayushman') || ragText.includes('pmjay') || ragText.includes('health'))) ||
      (id === 'pm-awas-yojana' && (ragText.includes('awas') || ragText.includes('pmay') || ragText.includes('housing'))) ||
      (id === 'pm-vishwakarma' && (ragText.includes('vishwakarma') || ragText.includes('artisan'))) ||
      (id === 'senior-citizen-pension' && (ragText.includes('senior') || ragText.includes('pension') || ragText.includes('ignoaps'))) ||
      (id === 'nsp-scholarship' && (ragText.includes('scholarship') || ragText.includes('student') || ragText.includes('nsp'))) ||
      (id === 'pm-ujjwala' && (ragText.includes('ujjwala') || ragText.includes('lpg') || ragText.includes('cylinder')))
    ) {
      ragVerified = true;
      score = Math.max(score + 18, 88);
      reasons.unshift('Directly recommended & verified by SchemeAssist AI RAG analysis');
    }

    score = Math.min(99, Math.max(15, score));
    const isEligible = score >= 70;
    const matchLevel = score >= 88 ? 'Highly Eligible' : score >= 70 ? 'Eligible' : 'Potentially Eligible';

    return {
      ...scheme,
      matchScore: score,
      matchLevel,
      isEligible,
      ragVerified,
      reasons: reasons.length > 0 ? reasons : ['General demographic profile match']
    };
  }).sort((a, b) => b.matchScore - a.matchScore);
}

export function AIAnalysisPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [step, setStep] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeStage, setActiveStage] = useState(-1);
  const [result, setResult] = useState(null);
  const [apiError, setApiError] = useState('');
  const [eligibleSchemes, setEligibleSchemes] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [savedSchemeIds, setSavedSchemeIds] = useState([]);

  const [profile, setProfile] = useState({
    // Personal
    name: user?.name || '',
    age: '',
    gender: '',
    state: user?.state || '',
    district: '',
    // Financial
    annualIncome: '',
    occupation: '',
    landHolding: '',
    hasBPL: false,
    hasRationCard: false,
    // Family & Category
    familySize: '',
    category: '',
    hasDisability: false,
    isWidow: false,
    hasFarmerCard: false,
    isStudent: false,
  });

  const set = (key) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setProfile((p) => ({ ...p, [key]: val }));
  };

  // ── Build a natural language question from collected profile ──────────────
  const buildQuestion = () => {
    const {
      name, age, gender, state, district,
      annualIncome, occupation, landHolding, hasBPL, hasRationCard,
      familySize, category, hasDisability, isWidow, hasFarmerCard, isStudent,
    } = profile;

    const parts = [];
    if (name) parts.push(`My name is ${name}.`);
    if (age) parts.push(`I am ${age} years old.`);
    if (gender) parts.push(`I am ${gender}.`);
    if (state) parts.push(`I live in ${district ? district + ', ' : ''}${state}.`);
    if (occupation) parts.push(`My occupation is ${occupation}.`);
    if (annualIncome) parts.push(`My annual household income is ₹${annualIncome}.`);
    if (landHolding) parts.push(`I own ${landHolding} acres of agricultural land.`);
    if (familySize) parts.push(`My family has ${familySize} members.`);
    if (category && category !== 'General') parts.push(`I belong to the ${category} category.`);
    if (hasBPL) parts.push('I have a Below Poverty Line (BPL) card.');
    if (hasRationCard) parts.push('I have a ration card.');
    if (hasFarmerCard) parts.push('I have a Kisan credit card / farmer registration.');
    if (hasDisability) parts.push('I have a disability.');
    if (isWidow) parts.push('I am a widow.');
    if (isStudent) parts.push('I am a student.');

    parts.push(
      'Based on this profile, which government welfare schemes am I eligible for? Please list the most relevant central and state government schemes with eligibility criteria and benefits.'
    );
    return parts.join(' ');
  };

  // ── Run analysis ──────────────────────────────────────────────────────────
  const runAnalysis = async () => {
    setStep(3);
    setAnalyzing(true);
    setResult(null);
    setEligibleSchemes([]);
    setApiError('');
    setActiveStage(0);

    const question = buildQuestion();

    // Animate pipeline stages
    const stageDelay = 900;
    for (let i = 0; i < PIPELINE_STAGES.length; i++) {
      await new Promise((r) => setTimeout(r, stageDelay));
      setActiveStage(i + 1);
    }

    // Call backend
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        // Fallback: try direct localhost
        const res2 = await fetch('http://127.0.0.1:8000/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question }),
        });
        if (!res2.ok) throw new Error('API request failed');
        const data = await res2.json();
        setResult(data);
        const evaluated = calculateEligibility(profile, data);
        setEligibleSchemes(evaluated);
      } else {
        const data = await res.json();
        setResult(data);
        const evaluated = calculateEligibility(profile, data);
        setEligibleSchemes(evaluated);
      }
    } catch (err) {
      setApiError(err.message || 'Failed to reach the AI backend. Make sure the API server is running.');
      const fallbackEvaluated = calculateEligibility(profile, null);
      setEligibleSchemes(fallbackEvaluated);
    }
    setAnalyzing(false);
  };

  // ── Validation ────────────────────────────────────────────────────────────
  const canProceedStep0 = profile.age && profile.gender && profile.state;
  const canProceedStep1 = profile.annualIncome && profile.occupation;
  const canProceedStep2 = profile.familySize && profile.category;

  const stepValid = [canProceedStep0, canProceedStep1, canProceedStep2, true];

  // ── UI ────────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6 animate-fadeIn max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="relative overflow-hidden rounded-card bg-navy p-6 md:p-8 text-white shadow-elevated">
        <div className="absolute right-0 top-0 h-full w-1/3 bg-primary/10 [clip-path:polygon(35%_0,100%_0,100%_100%,0_100%)]" />
        <div className="relative max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-badge bg-white/10 text-blue-100 border border-white/15 text-[11px] font-bold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            Government scheme matching
          </div>
          <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white">Find schemes that fit your profile</h1>
          <p className="text-sm text-blue-100/80 mt-2 max-w-2xl leading-relaxed">
            Share only the information needed for eligibility guidance. SchemeAssist compares your profile with available scheme rules and explains the next steps.
          </p>
        </div>
      </div>

      {/* Step Progress */}
      <div className="bg-white border border-slate-border rounded-card p-4 md:p-5 shadow-subtle flex items-center gap-0">
        {STEPS.map((s, i) => (
          <React.Fragment key={i}>
            <div className="flex flex-col items-center">
              <div className={`w-9 h-9 rounded-btn flex items-center justify-center text-xs font-bold border-2 transition-all
                ${i < step ? 'bg-gov-success border-gov-success text-white'
                  : i === step ? 'bg-primary border-primary text-white'
                    : 'bg-white border-slate-200 text-slate-400'}`}
              >
                {i < step ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
              </div>
              <span className={`text-[11px] font-semibold mt-1 hidden sm:block ${i === step ? 'text-primary' : i < step ? 'text-slate-600' : 'text-slate-400'}`}>
                {s}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`flex-1 h-0.5 mb-4 mx-1 transition-colors ${i < step ? 'bg-gov-success' : 'bg-slate-200'}`} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* ── STEP 0: Personal Info ── */}
      {step === 0 && (
        <Card className="space-y-6 border-slate-border shadow-subtle">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-border">
            <div className="w-10 h-10 bg-primary-50 rounded-btn flex items-center justify-center border border-primary/20">
              <User className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-base font-bold text-navy">Personal Information</h2>
              <p className="text-xs text-slate-500">Basic details to match schemes for your demographic</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className={labelCls}>Full Name</label>
              <input type="text" value={profile.name} onChange={set('name')} placeholder="Rajesh Kumar" className={inputCls} />
            </div>

            <FieldGroup>
              <div>
                <label className={labelCls}>Age <span className="text-red-500">*</span></label>
                <input type="number" value={profile.age} onChange={set('age')} placeholder="e.g. 35" min="1" max="120" className={inputCls} required />
              </div>
              <div>
                <label className={labelCls}>Gender <span className="text-red-500">*</span></label>
                <select value={profile.gender} onChange={set('gender')} className={selectCls} required>
                  <option value="">Select gender</option>
                  <option>Male</option>
                  <option>Female</option>
                  <option>Transgender</option>
                </select>
              </div>
            </FieldGroup>

            <FieldGroup>
              <div>
                <label className={labelCls}>State <span className="text-red-500">*</span></label>
                <select value={profile.state} onChange={set('state')} className={selectCls} required>
                  <option value="">Select state</option>
                  {STATES.map((s) => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className={labelCls}>District / City</label>
                <input type="text" value={profile.district} onChange={set('district')} placeholder="e.g. Pune" className={inputCls} />
              </div>
            </FieldGroup>
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={() => setStep(1)}
              disabled={!canProceedStep0}
              className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-dark disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold rounded-btn text-sm transition-colors"
            >
              Next <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </Card>
      )}

      {/* ── STEP 1: Financial Info ── */}
      {step === 1 && (
        <Card className="space-y-6 border-slate-border shadow-subtle">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <div className="w-10 h-10 bg-gov-success-light rounded-btn flex items-center justify-center border border-gov-success/20">
              <Wallet className="w-5 h-5 text-gov-success" />
            </div>
            <div>
              <h2 className="text-base font-bold text-navy">Financial Information</h2>
              <p className="text-xs text-slate-500">Income and occupation data for scheme eligibility matching</p>
            </div>
          </div>

          <div className="space-y-4">
            <FieldGroup>
              <div>
                <label className={labelCls}>Annual Household Income (₹) <span className="text-red-500">*</span></label>
                <input type="number" value={profile.annualIncome} onChange={set('annualIncome')} placeholder="e.g. 120000" min="0" className={inputCls} required />
                {profile.annualIncome && (
                  <p className="text-xs text-slate-400 mt-1">
                    ≈ ₹{Math.round(profile.annualIncome / 12).toLocaleString()} per month
                  </p>
                )}
              </div>
              <div>
                <label className={labelCls}>Primary Occupation <span className="text-red-500">*</span></label>
                <select value={profile.occupation} onChange={set('occupation')} className={selectCls} required>
                  <option value="">Select occupation</option>
                  <option>Farmer / Agricultural Worker</option>
                  <option>Daily Wage Labourer</option>
                  <option>Small Business Owner</option>
                  <option>Government Employee</option>
                  <option>Private Sector Employee</option>
                  <option>Self-Employed / Freelancer</option>
                  <option>Student</option>
                  <option>Homemaker</option>
                  <option>Unemployed</option>
                  <option>Retired</option>
                  <option>Fisher / Fisherman</option>
                  <option>Artisan / Craftsperson</option>
                </select>
              </div>
            </FieldGroup>

            <div>
              <label className={labelCls}>Agricultural Land Holding (Acres)</label>
              <input type="number" value={profile.landHolding} onChange={set('landHolding')} placeholder="0 if none" min="0" step="0.5" className={inputCls} />
              <p className="text-xs text-slate-400 mt-1">Relevant for PM-KISAN and farmer welfare schemes</p>
            </div>

            <div className="p-4 bg-slate-bg rounded-card border border-slate-border space-y-3">
              <p className="text-xs font-bold text-slate-600 uppercase tracking-wider">Government Cards / Documents</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <CheckBox id="bpl" label="BPL Card (Below Poverty Line)" checked={profile.hasBPL} onChange={set('hasBPL')} />
                <CheckBox id="ration" label="Ration Card (APL / NFSA)" checked={profile.hasRationCard} onChange={set('hasRationCard')} />
                <CheckBox id="farmer" label="Kisan Credit Card / Farmer ID" checked={profile.hasFarmerCard} onChange={set('hasFarmerCard')} />
              </div>
            </div>
          </div>

          <div className="flex justify-between pt-2">
            <button onClick={() => setStep(0)} className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 hover:border-slate-300 text-slate-600 font-semibold rounded-lg text-sm transition-colors">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={() => setStep(2)}
              disabled={!canProceedStep1}
              className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-dark disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold rounded-btn text-sm transition-colors"
            >
              Next <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </Card>
      )}

      {/* ── STEP 2: Family & Category ── */}
      {step === 2 && (
        <Card className="space-y-6 border-slate-border shadow-subtle">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <div className="w-10 h-10 bg-gov-warning-light rounded-btn flex items-center justify-center border border-gov-warning/20">
              <Users className="w-5 h-5 text-gov-warning" />
            </div>
            <div>
              <h2 className="text-base font-bold text-navy">Family & Social Category</h2>
              <p className="text-xs text-slate-500">Category and family details unlock reserved and targeted schemes</p>
            </div>
          </div>

          <div className="space-y-4">
            <FieldGroup>
              <div>
                <label className={labelCls}>Family Size (members) <span className="text-red-500">*</span></label>
                <input type="number" value={profile.familySize} onChange={set('familySize')} placeholder="e.g. 4" min="1" max="30" className={inputCls} required />
              </div>
              <div>
                <label className={labelCls}>Social Category <span className="text-red-500">*</span></label>
                <select value={profile.category} onChange={set('category')} className={selectCls} required>
                  <option value="">Select category</option>
                  <option>General</option>
                  <option>OBC (Other Backward Class)</option>
                  <option>SC (Scheduled Caste)</option>
                  <option>ST (Scheduled Tribe)</option>
                  <option>EWS (Economically Weaker Section)</option>
                  <option>Minority</option>
                </select>
              </div>
            </FieldGroup>

            <div className="p-4 bg-slate-50 rounded-lg border border-slate-100 space-y-3">
              <p className="text-xs font-bold text-slate-600 uppercase tracking-wider">Special Conditions</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <CheckBox id="disability" label="Person with Disability (PwD)" checked={profile.hasDisability} onChange={set('hasDisability')} />
                <CheckBox id="widow" label="Widow / Single Woman" checked={profile.isWidow} onChange={set('isWidow')} />
                <CheckBox id="student" label="Student (School / College)" checked={profile.isStudent} onChange={set('isStudent')} />
              </div>
            </div>

            {/* Profile Preview */}
            <div className="p-4 bg-primary-50 border border-primary/20 rounded-card">
              <p className="text-xs font-bold text-primary mb-2 uppercase tracking-wider">Review before analysis</p>
              <p className="text-xs text-slate-700 leading-relaxed">{buildQuestion()}</p>
            </div>
          </div>

          <div className="flex justify-between pt-2">
            <button onClick={() => setStep(1)} className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 hover:border-slate-300 text-slate-600 font-semibold rounded-lg text-sm transition-colors">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={runAnalysis}
              disabled={!canProceedStep2}
              className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-dark disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold rounded-btn text-sm transition-colors"
            >
              <Sparkles className="w-4 h-4" /> Run AI Analysis
            </button>
          </div>
        </Card>
      )}

      {/* ── STEP 3: Analysis ── */}
      {step === 3 && (
        <div className="space-y-6">
          {/* Pipeline Card */}
          <Card className="space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-base font-bold text-slate-900">AI Decision & Matching Pipeline</h2>
                <p className="text-xs text-slate-500">RAG-powered eligibility analysis using ChromaDB</p>
              </div>
              <Badge variant="primary" size="sm">RAG Multi-Stage</Badge>
            </div>

            <div className="space-y-3">
              {PIPELINE_STAGES.map((stage, idx) => {
                const done = activeStage > idx;
                const active = activeStage === idx && analyzing;
                const Icon = stage.icon;
                return (
                  <div key={idx} className={`flex items-start gap-4 p-3.5 rounded-xl border transition-all duration-300
                    ${done ? 'bg-green-50 border-green-200' : active ? 'bg-blue-50 border-blue-200 shadow-sm' : 'bg-slate-50 border-slate-100'}`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-colors
                      ${done ? 'bg-green-100' : active ? 'bg-blue-100' : 'bg-white border border-slate-200'}`}
                    >
                      {active ? (
                        <svg className="animate-spin w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                      ) : (
                        <Icon className={`w-5 h-5 ${done ? 'text-green-600' : 'text-slate-400'}`} />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className={`text-sm font-bold ${done ? 'text-green-800' : active ? 'text-blue-800' : 'text-slate-600'}`}>
                          {stage.title}
                        </h4>
                        <span className="text-[10px] font-mono text-slate-400">Step 0{idx + 1}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{stage.desc}</p>
                    </div>
                    {done && <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-1" />}
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Error */}
          {apiError && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-bold">Analysis Failed</p>
                <p className="text-xs mt-0.5">{apiError}</p>
                <button onClick={() => setStep(2)} className="text-xs underline mt-2 hover:no-underline">
                  Go back and try again
                </button>
              </div>
            </div>
          )}

          {/* Results */}
          {result && !analyzing && (
            <Card className="space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h2 className="text-base font-bold text-slate-900">AI Analysis Results</h2>
                <Badge variant="success" size="sm">
                  {result.status === 'answered' ? 'Complete' : result.status}
                </Badge>
              </div>

              {/* Answer */}
              <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50 rounded-xl p-4 border border-slate-100 text-sm">
                {result.answer}
              </div>

              {/* Sources */}
              {result.sources && result.sources.length > 0 && (
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Sources Used ({result.sources.length})
                  </p>
                  <div className="space-y-2">
                    {result.sources.map((src, i) => (
                      <div key={i} className="flex items-center gap-3 p-2.5 bg-white border border-slate-100 rounded-lg text-xs">
                        <Database className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                        <span className="font-medium text-slate-700 truncate">{src.source}</span>
                        {src.score != null && (
                          <span className="ml-auto shrink-0 font-mono text-slate-400">
                            {(src.score * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => navigate('/schemes')}
                  className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-sm transition-colors"
                >
                  Browse All Schemes <ExternalLink className="w-4 h-4" />
                </button>
                <button
                  onClick={() => { setStep(0); setResult(null); setActiveStage(-1); setEligibleSchemes([]); }}
                  className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 hover:border-slate-300 text-slate-600 font-semibold rounded-lg text-sm transition-colors"
                >
                  Re-analyse
                </button>
              </div>
            </Card>
          )}

          {/* ── Eligible Government Schemes Showcase ── */}
          {eligibleSchemes.length > 0 && !analyzing && (
            <div className="space-y-5 pt-2">
              {/* Header Banner */}
              <div className="bg-gradient-to-r from-[#0F2B46] to-blue-900 text-white rounded-2xl p-6 shadow-md border border-blue-800/40 relative overflow-hidden">
                <div className="absolute -right-6 -top-6 w-44 h-44 bg-blue-500/15 rounded-full blur-2xl pointer-events-none" />

                <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-5">
                  <div>
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/20 text-blue-200 border border-blue-400/30 text-xs font-bold uppercase tracking-wider mb-2">
                      <Sparkles className="w-3.5 h-3.5 text-blue-300" />
                      Eligible Schemes
                    </div>
                    <h2 className="text-2xl font-black tracking-tight text-white">
                      Schemes You Are Eligible For
                    </h2>
                    <p className="text-blue-100/80 text-xs sm:text-sm mt-1 max-w-xl leading-relaxed">
                      Based on the details you provided, these schemes have the strongest eligibility match. Review each reason before applying through the official authority.
                    </p>
                    <div className="flex flex-wrap gap-2 mt-4 text-[11px] text-blue-100">
                      <span className="px-2.5 py-1 rounded-badge bg-white/10 border border-white/15">Age: {profile.age || 'Not provided'}</span>
                      <span className="px-2.5 py-1 rounded-badge bg-white/10 border border-white/15">State: {profile.state || 'Not provided'}</span>
                      <span className="px-2.5 py-1 rounded-badge bg-white/10 border border-white/15">Occupation: {profile.occupation || 'Not provided'}</span>
                      <span className="px-2.5 py-1 rounded-badge bg-white/10 border border-white/15">Income: {profile.annualIncome ? `₹${Number(profile.annualIncome).toLocaleString('en-IN')}` : 'Not provided'}</span>
                    </div>
                  </div>

                  {/* Summary Metric Badges */}
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/10 text-center min-w-[90px]">
                      <span className="text-[10px] uppercase font-bold text-blue-200 block">Eligible</span>
                      <span className="text-2xl font-black text-white">
                        {eligibleSchemes.filter((s) => s.isEligible).length}
                      </span>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/10 text-center min-w-[130px]">
                      <span className="text-[10px] uppercase font-bold text-emerald-300 block">Max Benefit Potential</span>
                      <span className="text-base font-black text-emerald-300 truncate block">
                        ₹{eligibleSchemes
                          .filter((s) => s.isEligible)
                          .reduce((acc, s) => acc + (s.benefitAmount || 0), 0)
                          .toLocaleString('en-IN')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Filter Toolbar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                {/* Tabs */}
                <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg overflow-x-auto text-xs font-semibold">
                  <button
                    onClick={() => setActiveFilter('all')}
                    className={`px-3 py-1.5 rounded-md transition-colors whitespace-nowrap ${activeFilter === 'all'
                        ? 'bg-white text-blue-600 shadow-sm font-bold'
                        : 'text-slate-600 hover:text-slate-900'
                      }`}
                  >
                    All Eligible ({eligibleSchemes.filter((s) => s.isEligible).length})
                  </button>
                  <button
                    onClick={() => setActiveFilter('high')}
                    className={`px-3 py-1.5 rounded-md transition-colors whitespace-nowrap flex items-center gap-1.5 ${activeFilter === 'high'
                        ? 'bg-white text-emerald-600 shadow-sm font-bold'
                        : 'text-slate-600 hover:text-slate-900'
                      }`}
                  >
                    <span>Highly Eligible (≥85%)</span>
                    <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-700">
                      {eligibleSchemes.filter((s) => s.matchScore >= 85).length}
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveFilter('potential')}
                    className={`px-3 py-1.5 rounded-md transition-colors whitespace-nowrap ${activeFilter === 'potential'
                        ? 'bg-white text-blue-600 shadow-sm font-bold'
                        : 'text-slate-600 hover:text-slate-900'
                      }`}
                  >
                    Explore More ({eligibleSchemes.length})
                  </button>
                </div>

                {/* Category Dropdown */}
                <div className="flex items-center gap-2">
                  <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {SCHEME_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Scheme Cards Grid */}
              {(() => {
                const displayList = eligibleSchemes.filter((s) => {
                  if (activeFilter === 'high' && s.matchScore < 85) return false;
                  if (activeFilter === 'all' && !s.isEligible) return false;
                  if (selectedCategory !== 'All Categories' && s.category !== selectedCategory) return false;
                  return true;
                });

                if (displayList.length === 0) {
                  return (
                    <Card className="text-center py-10 space-y-3">
                      <HelpCircle className="w-8 h-8 text-slate-400 mx-auto" />
                      <p className="text-sm font-bold text-slate-700">No schemes match the current filter</p>
                      <p className="text-xs text-slate-500 max-w-sm mx-auto">
                        Try selecting "All Categories" or switching match filters to view all eligible schemes.
                      </p>
                      <button
                        onClick={() => { setSelectedCategory('All Categories'); setActiveFilter('all'); }}
                        className="px-4 py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700"
                      >
                        Reset Filters
                      </button>
                    </Card>
                  );
                }

                return (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {displayList.map((scheme) => (
                      <SchemeCard
                        key={scheme.id}
                        scheme={scheme}
                        isSaved={savedSchemeIds.includes(scheme.id)}
                        onSave={(id) => {
                          setSavedSchemeIds((prev) =>
                            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
                          );
                        }}
                      />
                    ))}
                  </div>
                );
              })()}

              {/* Bottom Support Banner */}
              <Card className="bg-slate-50 border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center shrink-0">
                    <Sparkles className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="text-xs sm:text-sm font-bold text-slate-900">Need help with eligibility documentation or application filing?</h4>
                    <p className="text-[11px] text-slate-500">Ask our AI Assistant for step-by-step guidance or visit the Helpdesk.</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Button variant="outline" size="sm" onClick={() => navigate('/ai-assistant')}>
                    Chat with AI
                  </Button>
                  <Button variant="primary" size="sm" onClick={() => navigate('/schemes')}>
                    Browse All Schemes
                  </Button>
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AIAnalysisPage;
