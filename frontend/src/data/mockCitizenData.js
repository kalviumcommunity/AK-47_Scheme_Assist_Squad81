/**
 * mockCitizenData.js - Default citizen state, applications, documents, and notifications
 */

export const DEFAULT_CITIZEN = {
  id: "CIT-88219",
  name: "Ramesh Kumar Sharma",
  email: "ramesh.sharma@example.com",
  phone: "+91 98765 43210",
  dob: "1984-06-15",
  age: 42,
  gender: "Male",
  location: {
    state: "Uttar Pradesh",
    district: "Varanasi",
    city: "Rohania",
    pincode: "221108",
    addressLine: "House 42, Gram Panchayat Rohania"
  },
  financial: {
    annualIncome: 140000,
    familyIncome: 180000,
    employmentStatus: "Self-Employed",
    occupation: "Smallholder Farmer / Agriculture"
  },
  additional: {
    education: "Secondary School (10th Pass)",
    landOwnership: "1.5 Acres (Marginal Cultivable Land)",
    disabilityStatus: "None",
    maritalStatus: "Married",
    familyMembers: 4
  },
  profileCompletion: 85,
  checklist: [
    { label: "Personal Details", completed: true },
    { label: "Address & Location", completed: true },
    { label: "Financial Details", completed: true },
    { label: "Mandatory Documents", completed: false }
  ]
};

export const MOCK_APPLICATIONS = [
  {
    id: "APP-2026-88412",
    schemeId: "pm-kisan",
    schemeName: "PM-KISAN Income Support",
    benefit: "₹6,000 / Year",
    category: "Agriculture",
    submittedDate: "2026-08-12",
    status: "Approved",
    statusCode: "approved",
    currentStep: 5,
    totalSteps: 5,
    timeline: [
      { step: "Application Submitted", date: "12 Aug 2026", done: true },
      { step: "Documents Verified", date: "16 Aug 2026", done: true },
      { step: "Under Review by Tehsildar", date: "21 Aug 2026", done: true },
      { step: "Government Verification", date: "28 Aug 2026", done: true },
      { step: "Approved & DBT Dispatched", date: "02 Sep 2026", done: true }
    ]
  },
  {
    id: "APP-2026-92105",
    schemeId: "ayushman-bharat",
    schemeName: "Ayushman Bharat Golden Card",
    benefit: "₹5 Lakh Coverage",
    category: "Healthcare",
    submittedDate: "2026-08-28",
    status: "Under Review",
    statusCode: "under_review",
    currentStep: 3,
    totalSteps: 5,
    timeline: [
      { step: "Application Submitted", date: "28 Aug 2026", done: true },
      { step: "Documents Verified", date: "30 Aug 2026", done: true },
      { step: "Under Review at District CMO", date: "04 Sep 2026", done: true },
      { step: "Government Verification", date: "Pending", done: false },
      { step: "Approved & Card Generated", date: "Pending", done: false }
    ]
  },
  {
    id: "APP-2026-94561",
    schemeId: "pm-awas-yojana",
    schemeName: "Pradhan Mantri Awas Yojana",
    benefit: "₹1.20 Lakh Grant",
    category: "Housing",
    submittedDate: "2026-09-02",
    status: "In Progress",
    statusCode: "in_progress",
    currentStep: 2,
    totalSteps: 5,
    timeline: [
      { step: "Application Submitted", date: "02 Sep 2026", done: true },
      { step: "Geo-tagging & Field Survey", date: "06 Sep 2026", done: true },
      { step: "Gram Sabha Review", date: "Pending", done: false },
      { step: "District Sanction Order", date: "Pending", done: false },
      { step: "First Tranche Disbursal", date: "Pending", done: false }
    ]
  },
  {
    id: "APP-2026-97814",
    schemeId: "pm-vishwakarma",
    schemeName: "PM Vishwakarma Modern Toolkit",
    benefit: "₹15,000 Grant + Loan",
    category: "Employment",
    submittedDate: "2026-09-06",
    status: "Pending",
    statusCode: "pending",
    currentStep: 1,
    totalSteps: 5,
    timeline: [
      { step: "Application Submitted", date: "06 Sep 2026", done: true },
      { step: "Gram Panchayat Verification", date: "Pending", done: false },
      { step: "District Screening Committee", date: "Pending", done: false },
      { step: "Trade Skill Assessment", date: "Pending", done: false },
      { step: "Sanction of Toolkit E-Voucher", date: "Pending", done: false }
    ]
  }
];

export const MOCK_DOCUMENTS = [
  {
    id: "doc-1",
    name: "Aadhaar Card",
    type: "Identity Proof",
    filename: "aadhaar_ramesh_kumar.pdf",
    size: "1.4 MB",
    uploadDate: "2026-07-14",
    status: "Verified",
    verified: true
  },
  {
    id: "doc-2",
    name: "Income Certificate",
    type: "Financial Proof",
    filename: "income_cert_2026_tehsildar.pdf",
    size: "2.1 MB",
    uploadDate: "2026-08-01",
    status: "Pending Review",
    verified: false
  },
  {
    id: "doc-3",
    name: "Land Revenue Record (Khasra-Khatauni)",
    type: "Property / Land Proof",
    filename: "khasra_plot_402_varanasi.pdf",
    size: "3.2 MB",
    uploadDate: "2026-08-10",
    status: "Verified",
    verified: true
  },
  {
    id: "doc-4",
    name: "Bank Passbook Front Page",
    type: "Banking Record",
    filename: "sbi_account_passbook.pdf",
    size: "890 KB",
    uploadDate: "2026-08-11",
    status: "Verified",
    verified: true
  },
  {
    id: "doc-5",
    name: "Ration Card (NFSA Priority)",
    type: "Family / Food Security",
    filename: "ration_card_up_nfsa.pdf",
    size: "1.1 MB",
    uploadDate: "2026-08-15",
    status: "Verified",
    verified: true
  },
  {
    id: "doc-6",
    name: "Caste / Category Certificate",
    type: "Social Welfare Proof",
    filename: "category_cert_obc.pdf",
    size: "1.7 MB",
    uploadDate: "2026-09-03",
    status: "Pending Review",
    verified: false
  }
];

export const MOCK_NOTIFICATIONS = [
  {
    id: "notif-1",
    title: "New Scheme Available",
    message: "You may be eligible for the newly updated PM Vishwakarma Kaushal Samman scheme based on your profile.",
    time: "10 mins ago",
    unread: true,
    type: "scheme",
    link: "/schemes/pm-vishwakarma"
  },
  {
    id: "notif-2",
    title: "Application Updated",
    message: "Your application APP-2026-92105 for Ayushman Bharat is now under review with the District CMO.",
    time: "2 hours ago",
    unread: true,
    type: "application",
    link: "/applications"
  },
  {
    id: "notif-3",
    title: "Document Verified",
    message: "Your Land Revenue Record (Khasra-Khatauni) has been successfully verified by the State Nodal Officer.",
    time: "Yesterday",
    unread: false,
    type: "document",
    link: "/documents"
  },
  {
    id: "notif-4",
    title: "PM-KISAN 17th Installment Credited",
    message: "Financial assistance of ₹2,000 has been transferred directly to your Aadhaar-seeded bank account.",
    time: "3 days ago",
    unread: false,
    type: "benefit",
    link: "/applications"
  }
];

export const MOCK_TICKETS = [
  {
    id: "TCK-4819",
    subject: "Aadhaar e-KYC biometric mismatch on portal",
    category: "Application Issues",
    status: "In Progress",
    createdDate: "2026-09-04",
    lastUpdate: "2026-09-06",
    description: "During PM-KISAN portal re-verification, the OTP verification fails with code 102. Need assistance updating mobile number."
  },
  {
    id: "TCK-4652",
    subject: "Income certificate re-upload request",
    category: "Document Issues",
    status: "Resolved",
    createdDate: "2026-08-25",
    lastUpdate: "2026-08-27",
    description: "Uploaded certificate was marked as blurred. Re-uploaded high resolution scan and approved."
  },
  {
    id: "TCK-4410",
    subject: "Query regarding land joint-ownership clause",
    category: "Eligibility Questions",
    status: "Closed",
    createdDate: "2026-08-15",
    lastUpdate: "2026-08-16",
    description: "Clarified that co-owners can each claim proportion based on individual name in registered Khatauni."
  }
];
