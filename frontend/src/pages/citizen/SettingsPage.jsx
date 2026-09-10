import React, { useState, useEffect } from 'react';
import {
  User,
  Bell,
  Globe,
  Shield,
  FileCheck2,
  Save,
  CheckCircle2
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';
import Select from '../../components/ui/Select';
import Button from '../../components/ui/Button';
import { DEFAULT_CITIZEN } from '../../data/mockCitizenData';
import { useAuth } from '../../context/AuthContext';

export function SettingsPage() {
  const { user, login } = useAuth();
  const [fullName, setFullName] = useState(user?.name || DEFAULT_CITIZEN.name);
  const [phone, setPhone] = useState(user?.phone || DEFAULT_CITIZEN.phone);
  const [email, setEmail] = useState(user?.email || DEFAULT_CITIZEN.email);
  const [occupation, setOccupation] = useState(DEFAULT_CITIZEN.financial.occupation);
  const [saved, setSaved] = useState(false);
  const [language, setLanguage] = useState('English');
  const [smsAlerts, setSmsAlerts] = useState(true);

  useEffect(() => {
    if (user?.name) setFullName(user.name);
    if (user?.email) setEmail(user.email);
    if (user?.phone) setPhone(user.phone);
  }, [user]);

  const handleSave = (e) => {
    e.preventDefault();
    if (user) {
      login({
        ...user,
        name: fullName.trim() || user.name,
        phone: phone.trim(),
        email: email.trim(),
      });
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn pb-12">
      <div>
        <h1 className="text-2xl font-black text-navy tracking-tight">Account & Preferences</h1>
        <p className="text-xs sm:text-sm text-slate-muted mt-0.5">
          Manage your verified citizen profile, notification preferences, and regional settings.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Profile Details */}
        <Card>
          <h3 className="text-sm font-bold text-navy pb-3 border-b border-slate-border mb-4 flex items-center gap-2">
            <User className="w-4 h-4 text-primary" />
            <span>Citizen Profile Particulars</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <Input
              label="Aadhaar Registered Phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <Input
              label="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              label="Current Occupation"
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
            />
          </div>
        </Card>

        {/* Preferences */}
        <Card>
          <h3 className="text-sm font-bold text-navy pb-3 border-b border-slate-border mb-4 flex items-center gap-2">
            <Globe className="w-4 h-4 text-primary" />
            <span>Language & Communication</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <Select
              label="Primary Language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              options={['English', 'Hindi (हिन्दी)', 'Bengali (বাংলা)', 'Marathi (मराठी)', 'Telugu (తెలుగు)', 'Tamil (தமிழ்)']}
            />
            <div className="pt-5 flex items-center gap-3">
              <input
                type="checkbox"
                id="sms-alerts"
                checked={smsAlerts}
                onChange={(e) => setSmsAlerts(e.target.checked)}
                className="w-4 h-4 text-primary rounded focus:ring-primary"
              />
              <label htmlFor="sms-alerts" className="text-xs text-slate-700 font-medium cursor-pointer">
                Receive SMS alerts for DBT payment dispatches & application status updates
              </label>
            </div>
          </div>
        </Card>

        <div className="flex items-center justify-between pt-2">
          {saved && (
            <span className="text-xs font-bold text-gov-success flex items-center gap-1.5 animate-fadeIn">
              <CheckCircle2 className="w-4 h-4" /> Profile & preferences updated successfully!
            </span>
          )}
          <div className="ml-auto">
            <Button variant="primary" size="md" icon={Save} type="submit">
              Save Changes
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default SettingsPage;
