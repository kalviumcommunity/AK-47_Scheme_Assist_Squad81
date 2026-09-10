import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, MapPin, IndianRupee, FileText, CheckCircle, ArrowLeft, ArrowRight, Save } from 'lucide-react';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';
import Select from '../../components/ui/Select';
import { DEFAULT_CITIZEN } from '../../data/mockCitizenData';
import { useAuth } from '../../context/AuthContext';

export function OnboardingPage() {
  const navigate = useNavigate();
  const { user, login } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Personal
    fullName: user?.name || DEFAULT_CITIZEN.name,
    dob: DEFAULT_CITIZEN.dob,
    age: DEFAULT_CITIZEN.age,
    gender: DEFAULT_CITIZEN.gender,
    phone: user?.phone || DEFAULT_CITIZEN.phone,
    email: user?.email || DEFAULT_CITIZEN.email,
    // Step 2: Location
    state: user?.state || DEFAULT_CITIZEN.location.state,
    district: DEFAULT_CITIZEN.location.district,
    city: DEFAULT_CITIZEN.location.city,
    pincode: DEFAULT_CITIZEN.location.pincode,
    // Step 3: Financial
    annualIncome: DEFAULT_CITIZEN.financial.annualIncome,
    familyIncome: DEFAULT_CITIZEN.financial.familyIncome,
    employmentStatus: DEFAULT_CITIZEN.financial.employmentStatus,
    occupation: DEFAULT_CITIZEN.financial.occupation,
    // Step 4: Additional
    education: DEFAULT_CITIZEN.additional.education,
    landOwnership: DEFAULT_CITIZEN.additional.landOwnership,
    disabilityStatus: DEFAULT_CITIZEN.additional.disabilityStatus,
    maritalStatus: DEFAULT_CITIZEN.additional.maritalStatus,
    familyMembers: DEFAULT_CITIZEN.additional.familyMembers,
  });

  const steps = [
    { number: 1, title: 'Personal Information', icon: User },
    { number: 2, title: 'Location Details', icon: MapPin },
    { number: 3, title: 'Financial Profile', icon: IndianRupee },
    { number: 4, title: 'Additional Criteria', icon: FileText },
  ];

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      // Completed, persist profile and redirect to dashboard
      if (user) {
        login({
          ...user,
          name: formData.fullName.trim() || user.name,
          phone: formData.phone.trim(),
          email: formData.email.trim(),
          state: formData.state,
        });
      }
      navigate('/dashboard');
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-bg py-8 px-4 md:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Top Header */}
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-btn bg-navy text-white flex items-center justify-center font-extrabold text-base shadow-sm">
              SA
            </div>
            <div>
              <h2 className="text-lg font-black text-navy leading-tight">SchemeAssist Onboarding</h2>
              <p className="text-xs text-slate-muted">Step {currentStep} of 4: {steps[currentStep - 1].title}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            icon={Save}
            onClick={() => alert("Progress saved locally in your browser session.")}
          >
            Save Progress
          </Button>
        </div>

        {/* Progress Step Bar */}
        <div className="grid grid-cols-4 gap-2 mb-8">
          {steps.map((s) => {
            const isDone = currentStep > s.number;
            const isCurrent = currentStep === s.number;
            return (
              <div key={s.number} className="text-center">
                <div
                  className={`h-2 rounded-full mb-2 transition-all ${
                    isDone
                      ? 'bg-gov-success'
                      : isCurrent
                      ? 'bg-primary'
                      : 'bg-slate-200'
                  }`}
                />
                <span className={`text-[11px] font-bold block truncate ${
                  isCurrent ? 'text-primary' : isDone ? 'text-navy' : 'text-slate-400'
                }`}>
                  {s.title}
                </span>
              </div>
            );
          })}
        </div>

        {/* Form Card */}
        <Card className="p-6 md:p-8 shadow-elevated">
          {currentStep === 1 && (
            <div className="space-y-4 animate-fadeIn">
              <h3 className="text-base font-bold text-navy border-b border-slate-border pb-2">
                Step 1: Personal Information
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Full Name (as in Aadhaar)"
                  value={formData.fullName}
                  onChange={(e) => handleChange('fullName', e.target.value)}
                  required
                />
                <Input
                  label="Date of Birth"
                  type="date"
                  value={formData.dob}
                  onChange={(e) => handleChange('dob', e.target.value)}
                  required
                />
                <Input
                  label="Current Age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => handleChange('age', e.target.value)}
                  required
                />
                <Select
                  label="Gender"
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  options={['Male', 'Female', 'Other']}
                />
                <Input
                  label="Mobile Number"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  required
                />
                <Input
                  label="Email Address"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4 animate-fadeIn">
              <h3 className="text-base font-bold text-navy border-b border-slate-border pb-2">
                Step 2: Location & Residence
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  label="State / UT"
                  value={formData.state}
                  onChange={(e) => handleChange('state', e.target.value)}
                  options={[
                    'Uttar Pradesh',
                    'Bihar',
                    'Maharashtra',
                    'Madhya Pradesh',
                    'Rajasthan',
                    'Karnataka',
                    'Tamil Nadu',
                    'Punjab',
                    'West Bengal'
                  ]}
                />
                <Input
                  label="District"
                  value={formData.district}
                  onChange={(e) => handleChange('district', e.target.value)}
                  required
                />
                <Input
                  label="Tehsil / Sub-District / City"
                  value={formData.city}
                  onChange={(e) => handleChange('city', e.target.value)}
                  required
                />
                <Input
                  label="Postal Pincode"
                  value={formData.pincode}
                  onChange={(e) => handleChange('pincode', e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-4 animate-fadeIn">
              <h3 className="text-base font-bold text-navy border-b border-slate-border pb-2">
                Step 3: Financial Information
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Individual Annual Income (₹)"
                  type="number"
                  value={formData.annualIncome}
                  onChange={(e) => handleChange('annualIncome', Number(e.target.value))}
                  required
                />
                <Input
                  label="Total Family Annual Income (₹)"
                  type="number"
                  value={formData.familyIncome}
                  onChange={(e) => handleChange('familyIncome', Number(e.target.value))}
                  required
                />
                <Select
                  label="Employment Status"
                  value={formData.employmentStatus}
                  onChange={(e) => handleChange('employmentStatus', e.target.value)}
                  options={[
                    'Self-Employed / Farmer',
                    'Daily Wage Worker / Casual Labour',
                    'Salaried Employee (Private)',
                    'Government Employee',
                    'Unemployed / Student',
                    'Retired / Pensioner'
                  ]}
                />
                <Input
                  label="Primary Occupation"
                  value={formData.occupation}
                  onChange={(e) => handleChange('occupation', e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-4 animate-fadeIn">
              <h3 className="text-base font-bold text-navy border-b border-slate-border pb-2">
                Step 4: Additional Information & Criteria
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  label="Highest Education"
                  value={formData.education}
                  onChange={(e) => handleChange('education', e.target.value)}
                  options={[
                    'No Formal Education',
                    'Primary School (5th Pass)',
                    'Secondary School (10th Pass)',
                    'Higher Secondary (12th Pass)',
                    'Graduate Degree',
                    'Post-Graduate / Professional'
                  ]}
                />
                <Select
                  label="Agricultural Land Ownership"
                  value={formData.landOwnership}
                  onChange={(e) => handleChange('landOwnership', e.target.value)}
                  options={[
                    'No Land / Landless',
                    'Marginal Farmer (Less than 2.5 Acres)',
                    'Small Farmer (2.5 to 5.0 Acres)',
                    'Medium / Large Landholding (5+ Acres)'
                  ]}
                />
                <Select
                  label="Disability Status"
                  value={formData.disabilityStatus}
                  onChange={(e) => handleChange('disabilityStatus', e.target.value)}
                  options={['None', 'Locomotor Disability (40%+)', 'Visual Impairment', 'Hearing Impairment', 'Other']}
                />
                <Select
                  label="Marital Status"
                  value={formData.maritalStatus}
                  onChange={(e) => handleChange('maritalStatus', e.target.value)}
                  options={['Married', 'Single / Unmarried', 'Widowed', 'Divorced']}
                />
                <Input
                  label="Number of Dependent Family Members"
                  type="number"
                  value={formData.familyMembers}
                  onChange={(e) => handleChange('familyMembers', Number(e.target.value))}
                  required
                />
              </div>
            </div>
          )}

          {/* Form Actions */}
          <div className="flex items-center justify-between pt-6 border-t border-slate-border mt-8">
            {currentStep > 1 ? (
              <Button
                variant="outline"
                size="md"
                icon={ArrowLeft}
                onClick={handleBack}
              >
                Previous
              </Button>
            ) : (
              <div />
            )}

            <Button
              variant="primary"
              size="md"
              onClick={handleNext}
            >
              {currentStep === 4 ? "Run AI Eligibility Analysis" : "Next"}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default OnboardingPage;
