/**
 * adminData.js - Admin statistics, analytics breakdowns, and management registries
 */

export const ADMIN_STATS = {
  totalCitizens: 10245,
  activeSchemes: 450,
  totalApplications: 8230,
  pendingReviews: 324,
  disbursedBenefits: "₹18.4 Cr",
  averageProcessingDays: 4.2
};

export const ADMIN_ANALYTICS = {
  monthlyApplications: [
    { month: "Apr", applications: 720, approved: 650 },
    { month: "May", applications: 890, approved: 780 },
    { month: "Jun", applications: 1150, approved: 1020 },
    { month: "Jul", applications: 1420, approved: 1280 },
    { month: "Aug", applications: 1890, approved: 1690 },
    { month: "Sep", applications: 2160, approved: 1810 }
  ],
  schemePopularity: [
    { name: "PM-KISAN", count: 3410, percentage: 41 },
    { name: "Ayushman Bharat", count: 2150, percentage: 26 },
    { name: "PMAY Housing", count: 1420, percentage: 17 },
    { name: "PM Vishwakarma", count: 850, percentage: 10 },
    { name: "Others", count: 400, percentage: 6 }
  ],
  statusBreakdown: {
    approved: 6420,
    underReview: 1140,
    pending: 346,
    rejected: 324
  }
};

export const ADMIN_SCHEMES_LIST = [
  {
    id: "pm-kisan",
    name: "PM-KISAN Samman Nidhi",
    category: "Agriculture",
    government: "Central Government",
    status: "Active",
    applications: 3410,
    lastUpdated: "2026-09-01",
    budget: "₹60,000 Cr"
  },
  {
    id: "ayushman-bharat",
    name: "Ayushman Bharat PM-JAY",
    category: "Healthcare",
    government: "Central Government",
    status: "Active",
    applications: 2150,
    lastUpdated: "2026-08-28",
    budget: "₹7,200 Cr"
  },
  {
    id: "pm-awas-yojana",
    name: "Pradhan Mantri Awas Yojana",
    category: "Housing",
    government: "Central Government",
    status: "Active",
    applications: 1420,
    lastUpdated: "2026-08-15",
    budget: "₹54,000 Cr"
  },
  {
    id: "pm-vishwakarma",
    name: "PM Vishwakarma Kaushal Samman",
    category: "Employment",
    government: "Central Government",
    status: "Active",
    applications: 850,
    lastUpdated: "2026-09-05",
    budget: "₹13,000 Cr"
  },
  {
    id: "senior-citizen-pension",
    name: "IGNOAPS Old Age Pension",
    category: "Senior Citizens",
    government: "Central & State Joint",
    status: "Active",
    applications: 310,
    lastUpdated: "2026-07-20",
    budget: "₹9,500 Cr"
  }
];

export const ADMIN_CITIZENS_LIST = [
  {
    id: "CIT-88219",
    name: "Ramesh Kumar Sharma",
    location: "Varanasi, Uttar Pradesh",
    applicationsCount: 4,
    eligibilityStatus: "Highly Eligible (4)",
    profileCompletion: 85,
    status: "Verified",
    registeredDate: "2026-07-10"
  },
  {
    id: "CIT-87940",
    name: "Sunita Devi Verma",
    location: "Patna, Bihar",
    applicationsCount: 2,
    eligibilityStatus: "Highly Eligible (3)",
    profileCompletion: 95,
    status: "Verified",
    registeredDate: "2026-07-12"
  },
  {
    id: "CIT-86512",
    name: "Anil Chandra Gowda",
    location: "Mandya, Karnataka",
    applicationsCount: 3,
    eligibilityStatus: "Highly Eligible (2)",
    profileCompletion: 100,
    status: "Verified",
    registeredDate: "2026-07-18"
  },
  {
    id: "CIT-85210",
    name: "Meenakshi Sundaram",
    location: "Madurai, Tamil Nadu",
    applicationsCount: 1,
    eligibilityStatus: "Potentially Eligible (3)",
    profileCompletion: 70,
    status: "Pending Documents",
    registeredDate: "2026-08-01"
  },
  {
    id: "CIT-84199",
    name: "Gurpreet Singh Gill",
    location: "Amritsar, Punjab",
    applicationsCount: 2,
    eligibilityStatus: "Highly Eligible (3)",
    profileCompletion: 90,
    status: "Verified",
    registeredDate: "2026-08-05"
  }
];

export const ADMIN_APPLICATIONS_LIST = [
  {
    id: "APP-2026-97814",
    citizenName: "Ramesh Kumar Sharma",
    scheme: "PM Vishwakarma Toolkit",
    state: "Uttar Pradesh",
    submittedDate: "2026-09-06",
    status: "Pending",
    docsCount: 4
  },
  {
    id: "APP-2026-97210",
    citizenName: "Sunita Devi Verma",
    scheme: "Ayushman Bharat Golden Card",
    state: "Bihar",
    submittedDate: "2026-09-05",
    status: "Under Review",
    docsCount: 3
  },
  {
    id: "APP-2026-96850",
    citizenName: "Anil Chandra Gowda",
    scheme: "PM-KISAN Samman Nidhi",
    state: "Karnataka",
    submittedDate: "2026-09-04",
    status: "Approved",
    docsCount: 4
  },
  {
    id: "APP-2026-95412",
    citizenName: "Meenakshi Sundaram",
    scheme: "PMAY Housing Subsidy",
    state: "Tamil Nadu",
    submittedDate: "2026-09-01",
    status: "Rejected",
    docsCount: 2
  }
];
