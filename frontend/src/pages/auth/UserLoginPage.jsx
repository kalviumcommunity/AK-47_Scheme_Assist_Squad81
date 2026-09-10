import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  Phone,
  MapPin,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  Landmark,
  Building2,
  FileCheck2,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function UserLoginPage({ defaultTab = 'login' }) {
  const { login, register, findUserByEmail } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab] = useState(defaultTab); // 'login' | 'signup'
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Login form state
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: '',
    rememberMe: true,
  });

  // Signup form state
  const [signupForm, setSignupForm] = useState({
    name: '',
    email: '',
    phone: '',
    state: 'Uttar Pradesh',
    password: '',
    confirmPassword: '',
    agreeTerms: true,
  });

  const indianStates = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Delhi (NCT)', 'Jammu & Kashmir', 'Ladakh', 'Puducherry'
  ];

  // Handle Login Submit
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    const cleanEmail = loginForm.email.trim();
    if (!cleanEmail || !loginForm.password) {
      setError('Please provide both your email address and password.');
      return;
    }

    if (loginForm.password.length < 6) {
      setError('Password must contain at least 6 characters.');
      return;
    }

    setLoading(true);

    setTimeout(() => {
      // Look up in database to fetch user's EXACT registered name
      const existingUser = findUserByEmail(cleanEmail);

      let userName = '';
      let userPhone = '';
      let userState = '';

      if (existingUser && existingUser.name) {
        userName = existingUser.name;
        userPhone = existingUser.phone || '';
        userState = existingUser.state || '';
      } else {
        // Format name from email if not previously registered
        const prefix = cleanEmail.split('@')[0];
        userName = prefix
          .replace(/[._-]/g, ' ')
          .split(' ')
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' ');
      }

      const citizenUser = {
        id: existingUser?.id || `CIT-${Date.now().toString().slice(-6)}`,
        name: userName,
        email: cleanEmail,
        phone: userPhone,
        state: userState,
        role: 'citizen',
        avatar: null,
      };

      login(citizenUser);
      setSuccessMsg(`Welcome back, ${userName}! Redirecting...`);

      setTimeout(() => {
        navigate('/dashboard');
      }, 500);

      setLoading(false);
    }, 600);
  };

  // Handle Signup Submit
  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    const cleanName = signupForm.name.trim();
    const cleanEmail = signupForm.email.trim();

    if (!cleanName) {
      setError('Please enter your full name as per official records.');
      return;
    }

    if (!cleanEmail) {
      setError('Please provide a valid email address.');
      return;
    }

    if (!signupForm.password || signupForm.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (signupForm.password !== signupForm.confirmPassword) {
      setError('Passwords do not match. Please re-check.');
      return;
    }

    if (!signupForm.agreeTerms) {
      setError('Please accept the citizen terms and data privacy consent.');
      return;
    }

    setLoading(true);

    setTimeout(() => {
      const newCitizen = {
        name: cleanName,
        email: cleanEmail,
        phone: signupForm.phone.trim(),
        state: signupForm.state,
        role: 'citizen',
      };

      // Register and save user's EXACT name
      register(newCitizen);

      setSuccessMsg(`Account created for ${cleanName}! Redirecting to dashboard...`);

      setTimeout(() => {
        navigate('/dashboard');
      }, 600);

      setLoading(false);
    }, 700);
  };

  // Quick fill demo user
  const handleFillDemo = () => {
    setLoginForm({
      email: 'rajesh.kumar@example.com',
      password: 'password123',
      rememberMe: true,
    });
    setError('');
  };

  return (
    <div className="min-h-screen bg-slate-bg flex flex-col justify-center py-8 px-4 sm:px-6 lg:px-8 relative overflow-hidden font-sans">
      {/* Decorative Government Tricolor Top Accent */}
      <div className="fixed top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-[#FF9933] via-white to-[#138808] z-50 shadow-sm" />

      {/* Subtle background glow */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-48 -right-48 w-96 h-96 bg-primary-100/50 rounded-full blur-3xl" />
        <div className="absolute -bottom-48 -left-48 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl" />
      </div>

      <div className="max-w-4xl w-full mx-auto relative z-10">
        <div className="bg-white rounded-2xl shadow-xl border border-slate-border overflow-hidden grid grid-cols-1 md:grid-cols-12 min-h-[620px]">

          {/* ─── Left Hero Brand Panel (Desktop) ─── */}
          <div className="md:col-span-5 bg-gradient-to-br from-navy to-navy-800 p-8 text-white flex flex-col justify-between relative overflow-hidden">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-5 pointer-events-none bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]" />

            <div>
              {/* National Emblem Badge & Brand */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur border border-white/20 flex items-center justify-center shadow-md">
                  <Landmark className="w-6 h-6 text-[#FF9933]" />
                </div>
                <div>
                  <h1 className="text-xl font-black tracking-tight text-white leading-none">
                    SchemeAssist
                  </h1>
                  <p className="text-[11px] text-slate-300 uppercase tracking-widest mt-1 font-semibold">
                    National Welfare Portal
                  </p>
                </div>
              </div>

              <div className="mt-8 space-y-4">
                <h2 className="text-2xl font-black text-white leading-snug tracking-tight">
                  One Unified Identity for Every Citizen Benefit.
                </h2>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Discover, verify eligibility, and track over 450+ Central and State welfare programs with AI assistance.
                </p>
              </div>

              {/* Feature checklist */}
              <div className="mt-8 space-y-3">
                {[
                  { text: 'Verified Schemes & Instant DBT Check', icon: CheckCircle2 },
                  { text: 'Grounded Gemini AI Support (No Hallucination)', icon: Sparkles },
                  { text: 'Aadhaar & DigiLocker Safe Verification', icon: ShieldCheck },
                  { text: 'Multi-lingual Eligibility Guidance', icon: FileCheck2 },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-2.5 text-xs text-slate-200">
                    <item.icon className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom trust badge */}
            <div className="pt-8 border-t border-white/10 mt-8">
              <div className="flex items-center gap-2 text-[11px] text-slate-300">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Ministry Standard • 256-Bit Encrypted</span>
              </div>
            </div>
          </div>

          {/* ─── Right Form Panel ─── */}
          <div className="md:col-span-7 p-6 sm:p-8 flex flex-col justify-between bg-white">
            <div>
              {/* Header & Tab Switcher */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-border mb-6">
                <div>
                  <h2 className="text-xl font-black text-navy tracking-tight">
                    {tab === 'login' ? 'Citizen Portal Sign In' : 'Create Citizen Profile'}
                  </h2>
                  <p className="text-xs text-slate-muted mt-0.5">
                    {tab === 'login'
                      ? 'Enter your credentials to access your welfare dashboard'
                      : 'Register your name to check eligibility and track applications'}
                  </p>
                </div>

                {/* Tab Pill */}
                <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-bold">
                  <button
                    type="button"
                    onClick={() => {
                      setTab('login');
                      setError('');
                      setSuccessMsg('');
                    }}
                    className={`px-3 py-1.5 rounded-md transition-all ${
                      tab === 'login'
                        ? 'bg-white text-navy shadow-sm'
                        : 'text-slate-muted hover:text-navy'
                    }`}
                  >
                    Sign In
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setTab('signup');
                      setError('');
                      setSuccessMsg('');
                    }}
                    className={`px-3 py-1.5 rounded-md transition-all ${
                      tab === 'signup'
                        ? 'bg-white text-navy shadow-sm'
                        : 'text-slate-muted hover:text-navy'
                    }`}
                  >
                    Register
                  </button>
                </div>
              </div>

              {/* Error Alert */}
              {error && (
                <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 animate-fadeIn">
                  <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {/* Success Alert */}
              {successMsg && (
                <div className="mb-5 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 animate-fadeIn">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{successMsg}</span>
                </div>
              )}

              {/* ─── TAB 1: LOGIN FORM ─── */}
              {tab === 'login' && (
                <form onSubmit={handleLoginSubmit} className="space-y-4 animate-fadeIn">
                  {/* Email */}
                  <div>
                    <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                      Email Address or Mobile Number <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        name="email"
                        value={loginForm.email}
                        onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                        placeholder="you@example.com or 9876543210"
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                        required
                      />
                    </div>
                  </div>

                  {/* Password */}
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <label className="block text-xs font-bold text-navy uppercase tracking-wider">
                        Password <span className="text-red-500">*</span>
                      </label>
                      <button
                        type="button"
                        onClick={() => alert('Please contact the citizen helpdesk or re-register with your email.')}
                        className="text-[11px] text-primary hover:underline font-semibold"
                      >
                        Forgot Password?
                      </button>
                    </div>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                        placeholder="Enter your account password"
                        className="w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-navy"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {/* Remember Me */}
                  <div className="flex items-center justify-between pt-1">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={loginForm.rememberMe}
                        onChange={(e) => setLoginForm({ ...loginForm, rememberMe: e.target.checked })}
                        className="w-4 h-4 rounded border-slate-border text-primary focus:ring-primary/20"
                      />
                      <span className="text-xs text-slate-muted">Keep me signed in on this device</span>
                    </label>

                    {/* Quick Demo Citizen Fill */}
                    <button
                      type="button"
                      onClick={handleFillDemo}
                      className="text-[11px] text-slate-500 hover:text-primary font-semibold bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded transition"
                    >
                      Fill Demo: Rajesh
                    </button>
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-2 py-3 px-4 bg-primary hover:bg-primary-dark active:scale-[0.99] disabled:opacity-50 text-white text-xs font-black uppercase tracking-wider rounded-btn shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Signing In...</span>
                      </>
                    ) : (
                      <>
                        <span>Sign In to Citizen Portal</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </form>
              )}

              {/* ─── TAB 2: SIGNUP FORM ─── */}
              {tab === 'signup' && (
                <form onSubmit={handleSignupSubmit} className="space-y-3.5 animate-fadeIn">
                  {/* Full Name */}
                  <div>
                    <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1">
                      Full Name (as per Aadhaar / Official ID) <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        name="name"
                        value={signupForm.name}
                        onChange={(e) => setSignupForm({ ...signupForm, name: e.target.value })}
                        placeholder="e.g. Mohamed Sham, Priya Sharma"
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                        required
                      />
                    </div>
                  </div>

                  {/* Email & Phone Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1">
                        Email Address <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input
                          type="email"
                          name="email"
                          value={signupForm.email}
                          onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
                          placeholder="citizen@example.com"
                          className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1">
                        Aadhaar Linked Mobile
                      </label>
                      <div className="relative">
                        <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input
                          type="tel"
                          name="phone"
                          value={signupForm.phone}
                          onChange={(e) => setSignupForm({ ...signupForm, phone: e.target.value })}
                          placeholder="+91 98765 43210"
                          className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                        />
                      </div>
                    </div>
                  </div>

                  {/* State of Residence */}
                  <div>
                    <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1">
                      State / Union Territory
                    </label>
                    <div className="relative">
                      <MapPin className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <select
                        name="state"
                        value={signupForm.state}
                        onChange={(e) => setSignupForm({ ...signupForm, state: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                      >
                        {indianStates.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Password & Confirm Password */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1">
                        Create Password <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={signupForm.password}
                          onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
                          placeholder="Min 6 characters"
                          className="w-full pl-10 pr-8 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-navy"
                        >
                          {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1">
                        Confirm Password <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input
                          type={showConfirmPassword ? 'text' : 'password'}
                          name="confirmPassword"
                          value={signupForm.confirmPassword}
                          onChange={(e) => setSignupForm({ ...signupForm, confirmPassword: e.target.value })}
                          placeholder="Re-enter password"
                          className="w-full pl-10 pr-8 py-2.5 bg-slate-50 border border-slate-border rounded-input text-xs text-navy placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-navy"
                        >
                          {showConfirmPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Terms */}
                  <label className="flex items-start gap-2 pt-1 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={signupForm.agreeTerms}
                      onChange={(e) => setSignupForm({ ...signupForm, agreeTerms: e.target.checked })}
                      className="w-4 h-4 mt-0.5 rounded border-slate-border text-primary focus:ring-primary/20"
                    />
                    <span className="text-[11px] text-slate-500 leading-tight">
                      I declare that the information provided is accurate and consent to statutory welfare eligibility verification.
                    </span>
                  </label>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-2 py-3 px-4 bg-primary hover:bg-primary-dark active:scale-[0.99] disabled:opacity-50 text-white text-xs font-black uppercase tracking-wider rounded-btn shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Creating Profile...</span>
                      </>
                    ) : (
                      <>
                        <span>Complete Registration & Proceed</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>

            {/* Bottom Footer: Switch tab or admin link */}
            <div className="pt-6 border-t border-slate-border mt-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-muted">
              <div>
                {tab === 'login' ? (
                  <span>
                    New to SchemeAssist?{' '}
                    <button
                      type="button"
                      onClick={() => {
                        setTab('signup');
                        setError('');
                      }}
                      className="text-primary hover:underline font-bold"
                    >
                      Create your Citizen Account
                    </button>
                  </span>
                ) : (
                  <span>
                    Already have an account?{' '}
                    <button
                      type="button"
                      onClick={() => {
                        setTab('login');
                        setError('');
                      }}
                      className="text-primary hover:underline font-bold"
                    >
                      Sign in here
                    </button>
                  </span>
                )}
              </div>

              <Link
                to="/admin/login"
                className="text-slate-400 hover:text-navy flex items-center gap-1 font-semibold transition"
              >
                <Building2 className="w-3.5 h-3.5" />
                <span>Department Admin Login</span>
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
