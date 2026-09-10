/**
 * schemesData.js - Comprehensive repository of government welfare schemes
 */

export const SCHEMES = [
  {
    id: "pm-kisan",
    name: "PM-KISAN",
    fullName: "Pradhan Mantri Kisan Samman Nidhi",
    category: "Agriculture",
    governmentType: "Central Government",
    benefit: "₹6,000 / Year",
    benefitAmount: 6000,
    benefitFrequency: "Three 4-monthly installments of ₹2,000 directly via DBT",
    matchScore: 95,
    matchLevel: "Highly Eligible",
    status: "Active",
    applicationMode: "Online & CSC",
    icon: "Wheat",
    description: "Central sector scheme providing direct income support to all landholding farmer families across the country to take care of agricultural and domestic needs.",
    overview: "Under the PM-KISAN scheme, the Government of India provides income support of ₹6,000 per year in three equal four-monthly installments directly into the bank accounts of eligible farmer families.",
    benefits: [
      "Direct financial support of ₹6,000 per year paid in three installments of ₹2,000 each.",
      "Direct Benefit Transfer (DBT) directly into bank accounts via Aadhaar linkage.",
      "Coverage for small, marginal, and landholding farmer families nationwide.",
      "Empowers farmers to procure quality seeds, fertilizers, and equipment."
    ],
    eligibility: {
      targetGroup: "Small and marginal farmer families with cultivable landholding",
      ageRange: "18 to 75 years",
      incomeLimit: "No strict ceiling, but institutional landholders & income tax payers are excluded",
      occupation: "Farmer / Agriculturalist",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card (Mandatory)",
      "Landholding Ownership Document / Khasra-Khatauni Record",
      "Bank Account Passbook / Statement linked with Aadhaar",
      "Active Mobile Number"
    ],
    applicationProcess: [
      "Self-registration on the PM-KISAN online portal (pmkisan.gov.in) or nearest CSC.",
      "Submit land records, Aadhaar details, and bank account number.",
      "State nodal officer verifies revenue records and land ownership.",
      "Aadhaar-based e-KYC verification.",
      "Installment credited directly via PFMS DBT gateway."
    ],
    faqs: [
      {
        question: "Can tenants or sharecroppers apply for PM-KISAN?",
        answer: "No. Only landholding farmer families who own cultivable agricultural land as per official land records are eligible."
      },
      {
        question: "How do I check if my installment was credited?",
        answer: "Visit the PM-KISAN portal 'Beneficiary Status' page, enter your Aadhaar or registered mobile number, and view your installment transaction logs."
      }
    ]
  },
  {
    id: "ayushman-bharat",
    name: "Ayushman Bharat",
    fullName: "Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
    category: "Healthcare",
    governmentType: "Central Government",
    benefit: "₹5 Lakh / Family / Year",
    benefitAmount: 500000,
    benefitFrequency: "Cashless secondary and tertiary hospitalization cover",
    matchScore: 92,
    matchLevel: "Highly Eligible",
    status: "Active",
    applicationMode: "Online & Empanelled Hospitals",
    icon: "HeartPulse",
    description: "The world's largest health assurance scheme, providing ₹5 Lakh health cover per family per year for secondary and tertiary hospitalization.",
    overview: "Ayushman Bharat PM-JAY aims to provide cashless and paperless access to services for the beneficiary at the point of service in empanelled public and private hospitals across India.",
    benefits: [
      "₹5,00,000 health assurance cover per family per year.",
      "Cashless treatment in over 29,000 empanelled hospitals across India.",
      "Covers 3 days of pre-hospitalization and 15 days of post-hospitalization costs.",
      "Covers 1,949 medical and surgical procedures with zero out-of-pocket costs.",
      "All pre-existing medical conditions covered from Day 1."
    ],
    eligibility: {
      targetGroup: "SECC 2011 identified vulnerable and deprived rural/urban families",
      ageRange: "All ages (No restrictions on family size or age)",
      incomeLimit: "Deprivation criteria based on SECC 2011 census",
      occupation: "Informal, casual, agricultural, or informal urban labor",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card or Ration Card",
      "Ration Card / SECC Family ID Proof",
      "Ayushman Golden Card (generated at hospital)"
    ],
    applicationProcess: [
      "Check name on the 'Am I Eligible' portal (mera.pmjay.gov.in).",
      "Visit any empanelled hospital or Common Service Center (CSC).",
      "Ayushman Mitra verifies identity with Aadhaar biometric authentication.",
      "Receive instant digital Golden Card for cashless admission."
    ],
    faqs: [
      {
        question: "Is there any limit on family size or age under PM-JAY?",
        answer: "No. There is no restriction on family size, gender, or age of family members."
      }
    ]
  },
  {
    id: "pm-awas-yojana",
    name: "PMAY-Gramin & Urban",
    fullName: "Pradhan Mantri Awas Yojana",
    category: "Housing",
    governmentType: "Central Government",
    benefit: "Up to ₹2.67 Lakh Subsidy",
    benefitAmount: 267000,
    benefitFrequency: "Direct grant / interest subsidy for pucca house construction",
    matchScore: 88,
    matchLevel: "Highly Eligible",
    status: "Active",
    applicationMode: "Online / Municipal Office",
    icon: "Home",
    description: "Housing for All initiative providing financial assistance and interest subsidies to construct durable, safe pucca houses with basic amenities.",
    overview: "PMAY addresses rural and urban housing shortages by extending financial grants (₹1.20 Lakh to ₹1.30 Lakh in Gramin) and Credit Linked Subsidy (CLSS up to ₹2.67 Lakh) for pucca construction.",
    benefits: [
      "Financial assistance of ₹1,20,000 (plains) to ₹1,30,000 (hilly states) in rural areas.",
      "Up to ₹2,67,000 interest subsidy under Credit Linked Subsidy Scheme (CLSS).",
      "Mandatory toilet construction assistance of ₹12,000 under Swachh Bharat Mission.",
      "90-95 days of unskilled wage labor support under MGNREGA."
    ],
    eligibility: {
      targetGroup: "Houseless families or living in kutcha/dilapidated houses",
      ageRange: "21 to 70 years",
      incomeLimit: "EWS: Up to ₹3 Lakh; LIG: ₹3 Lakh - ₹6 Lakh",
      occupation: "Any citizen without a permanent pucca house",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card",
      "Income Certificate",
      "Bank Account Details",
      "Land Record / Construction Permission",
      "Declaration of not owning any pucca house in India"
    ],
    applicationProcess: [
      "Apply via Gram Panchayat (Gramin) or municipal portal / CSC (Urban).",
      "Physical geo-tagging and verification of existing kutcha structure.",
      "Approval by District Level Committee.",
      "Funds released directly in tranches linked to construction milestones."
    ],
    faqs: [
      {
        question: "Can a family owning an ancestral house apply?",
        answer: "Only if the family does not own a permanent pucca house anywhere in India."
      }
    ]
  },
  {
    id: "pm-vishwakarma",
    name: "PM Vishwakarma",
    fullName: "PM Vishwakarma Kaushal Samman Yojana",
    category: "Employment",
    governmentType: "Central Government",
    benefit: "₹15,000 Toolkit + ₹3 Lakh Loan",
    benefitAmount: 315000,
    benefitFrequency: "Skill training, ₹500/day stipend, toolkit grant, and 5% interest loans",
    matchScore: 84,
    matchLevel: "Potentially Eligible",
    status: "Active",
    applicationMode: "Common Service Center (CSC)",
    icon: "Wrench",
    description: "End-to-end holistic support to traditional artisans and craftspeople with skill training, toolkit incentives, and collateral-free credit support.",
    overview: "PM Vishwakarma uplifts traditional artisans across 18 trades (blacksmiths, carpenters, potters, cobblers, tailors) through certification, basic & advanced training, ₹15,000 modern toolkits, and collateral-free enterprise loans at 5% interest.",
    benefits: [
      "Digital PM Vishwakarma Certificate and ID Card recognition.",
      "Basic training (5-7 days) & Advanced training (15 days) with ₹500/day stipend.",
      "₹15,000 direct grant for modern toolkit purchase.",
      "Collateral-free enterprise loan up to ₹3,00,000 (Tranche 1: ₹1 Lakh, Tranche 2: ₹2 Lakh) at concessional 5% interest rate.",
      "Incentive for digital transactions (₹1 per transaction up to 100/month)."
    ],
    eligibility: {
      targetGroup: "Artisans working with hands and tools in one of 18 trades",
      ageRange: "Minimum 18 years",
      incomeLimit: "Engaged in traditional family craft; one beneficiary per family",
      occupation: "Traditional Artisan / Craftsman",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card",
      "Mobile Number linked to Aadhaar",
      "Bank Account Details",
      "Ration Card / Family Proof"
    ],
    applicationProcess: [
      "Biometric registration at CSC on pmvishwakarma.gov.in.",
      "Three-tier verification: Gram Panchayat / ULB, District Committee, Screening Committee.",
      "Skill verification and issuance of Vishwakarma Certificate."
    ],
    faqs: [
      {
        question: "Which trades are covered under PM Vishwakarma?",
        answer: "18 traditional trades including Carpenter, Boat Maker, Armorer, Blacksmith, Hammer & Tool Kit Maker, Locksmith, Sculptor, Potter, Cobbler, Mason, Basket/Mat/Broom Maker, Coir Weaver, Doll & Toy Maker, Barber, Garland Maker, Washerman, Tailor, and Fishing Net Maker."
      }
    ]
  },
  {
    id: "senior-citizen-pension",
    name: "IGNOAPS Pension",
    fullName: "Indira Gandhi National Old Age Pension Scheme",
    category: "Senior Citizens",
    governmentType: "Central & State Joint",
    benefit: "₹1,000 - ₹3,000 / Month",
    benefitAmount: 24000,
    benefitFrequency: "Monthly direct pension into savings bank account",
    matchScore: 78,
    matchLevel: "Potentially Eligible",
    status: "Active",
    applicationMode: "District Social Welfare Office / Portal",
    icon: "ShieldAlert",
    description: "Social security monthly pension for senior citizens belonging to below poverty line (BPL) households across Indian states.",
    overview: "Part of the National Social Assistance Programme (NSAP), this scheme provides non-contributory monthly pensions to senior citizens living in BPL conditions to ensure dignity in their twilight years.",
    benefits: [
      "Monthly financial pension credited directly to the beneficiary's bank or postal account.",
      "Central contribution topped up with state government matching assistance.",
      "Disability and widow pension linkages where applicable."
    ],
    eligibility: {
      targetGroup: "Senior citizens living Below Poverty Line (BPL)",
      ageRange: "60 years and above",
      incomeLimit: "BPL cardholder household status",
      occupation: "Retired / Elderly",
      state: "All India"
    },
    requiredDocuments: [
      "Age Proof (Aadhaar / Voter ID / Birth Certificate)",
      "BPL Ration Card / Income Certificate",
      "Bank Account Passbook",
      "Passport-sized Photographs"
    ],
    applicationProcess: [
      "Submit application to Gram Panchayat / Block Development Office / Municipal Ward.",
      "Physical verification by Social Welfare Inspector.",
      "District Collector / Welfare Officer sanction.",
      "Direct pension disbursal via PFMS."
    ],
    faqs: [
      {
        question: "What happens when the beneficiary turns 80?",
        answer: "The monthly pension amount increases significantly under central norms from ₹200 to ₹500 base, with additional state contributions."
      }
    ]
  },
  {
    id: "nsp-scholarship",
    name: "National Scholarship",
    fullName: "NSP Post-Matric & Merit Scholarship",
    category: "Education",
    governmentType: "Central Government",
    benefit: "Up to ₹50,000 / Year",
    benefitAmount: 50000,
    benefitFrequency: "Annual tuition fee reimbursement and maintenance allowance",
    matchScore: 74,
    matchLevel: "Requires More Information",
    status: "Active",
    applicationMode: "National Scholarship Portal (NSP)",
    icon: "GraduationCap",
    description: "Financial assistance to students from economically disadvantaged families for post-matric and higher educational studies.",
    overview: "NSP acts as a single-window digital gateway providing transparent, merit-cum-means scholarships to students from Class 11 through post-graduate and technical degree programs.",
    benefits: [
      "Tuition fees directly paid or reimbursed to students.",
      "Monthly maintenance allowance for hostellers and day scholars.",
      "Book and equipment grant allowances for technical and medical courses."
    ],
    eligibility: {
      targetGroup: "Students pursuing higher education with verified academic record",
      ageRange: "15 to 30 years",
      incomeLimit: "Family income less than ₹2.5 Lakh per annum",
      occupation: "Student",
      state: "All India"
    },
    requiredDocuments: [
      "Student Aadhaar Card",
      "Previous Year Academic Marksheet",
      "Current Year Fee Receipt & College ID",
      "Income Certificate issued by competent authority",
      "Bank Account details in student's name"
    ],
    applicationProcess: [
      "Register on scholarships.gov.in using Aadhaar.",
      "Select applicable scholarship scheme and fill academic particulars.",
      "College / Institute nodal officer performs Level 1 verification.",
      "District / State nodal officer performs Level 2 verification.",
      "Direct DBT grant transfer via PFMS."
    ],
    faqs: [
      {
        question: "Can I receive more than one government scholarship?",
        answer: "No. A student can only avail one central or state scholarship benefit in an academic year."
      }
    ]
  },
  {
    id: "pm-ujjwala",
    name: "PM Ujjwala Yojana",
    fullName: "Pradhan Mantri Ujjwala Yojana (PMUY 2.0)",
    category: "Women",
    governmentType: "Central Government",
    benefit: "Free LPG Connection + First Refill",
    benefitAmount: 3200,
    benefitFrequency: "Deposit-free gas connection, regulator, hose, and subsidy on refills",
    matchScore: 72,
    matchLevel: "Requires More Information",
    status: "Active",
    applicationMode: "LPG Distributor / Portal",
    icon: "Flame",
    description: "Clean cooking fuel access for rural and deprived women with deposit-free LPG connections and subsidized refills.",
    overview: "PMUY empowers women in underprivileged households by safeguarding their respiratory health from hazardous smoke, providing free LPG connections and targeted cylinder subsidies.",
    benefits: [
      "Deposit-free LPG connection for the adult woman of the household.",
      "Free first refill cylinder and stove included.",
      "Direct targeted subsidy of ₹300 per refill up to 12 refills per year."
    ],
    eligibility: {
      targetGroup: "Adult women from BPL, SC/ST, PMAY, or deprived households",
      ageRange: "18 years and above (Female only)",
      incomeLimit: "BPL or SECC 2011 list",
      occupation: "Homemaker / Citizen",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card of Applicant and all adult family members",
      "Ration Card with family composition proof",
      "Bank Account linked to Aadhaar",
      "Address Proof"
    ],
    applicationProcess: [
      "Apply online or submit PMUY form at nearest LPG distributor.",
      "OMC (Oil Marketing Company) de-duplication check.",
      "Issuance of LPG subscription voucher and delivery of cylinder & stove."
    ],
    faqs: [
      {
        question: "Can a male family member apply for Ujjwala connection?",
        answer: "No. The LPG connection under PMUY is strictly issued in the name of an adult woman of the family."
      }
    ]
  },
  {
    id: "pm-svanidhi",
    name: "PM SVANidhi",
    fullName: "PM Street Vendor's AtmaNirbhar Nidhi",
    category: "Employment",
    governmentType: "Central Government",
    benefit: "Up to ₹50,000 Micro-Credit Loan",
    benefitAmount: 50000,
    benefitFrequency: "Collateral-free working capital loan with 7% interest subsidy & cashback",
    matchScore: 82,
    matchLevel: "Potentially Eligible",
    status: "Active",
    applicationMode: "Online & Urban Local Bodies",
    icon: "Wrench",
    description: "Affordable working capital loan scheme to empower street vendors and small micro-entrepreneurs to resume and expand livelihoods.",
    overview: "PM SVANidhi provides collateral-free working capital loans of ₹10,000 (1st tranche), ₹20,000 (2nd tranche), and up to ₹50,000 (3rd tranche) with 7% interest subsidy on regular repayment.",
    benefits: [
      "Initial working capital loan of ₹10,000 without collateral.",
      "Higher credit limit up to ₹50,000 on timely repayment.",
      "7% annual interest subsidy credited directly to bank account.",
      "Monthly cashback incentive of up to ₹100 on digital transactions."
    ],
    eligibility: {
      targetGroup: "Street vendors, hawkers, small shopkeepers, and informal sellers",
      ageRange: "18 years and above",
      incomeLimit: "Engaged in vending in urban, semi-urban, or peri-urban areas",
      occupation: "Street Vendor / Small Business / Informal Trader",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card",
      "Voter Identity Card or Letter of Recommendation (LoR)",
      "Bank Account details",
      "Mobile number linked to Aadhaar"
    ],
    applicationProcess: [
      "Submit application on pmsvanidhi.mohua.gov.in or via CSC.",
      "Urban Local Body (ULB) verifies vending certificate or issues LoR.",
      "Lending institution sanctions and disburses loan directly to bank account."
    ],
    faqs: [
      {
        question: "Is collateral security required for PM SVANidhi loans?",
        answer: "No. The loan is 100% collateral-free and backed by the Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)."
      }
    ]
  },
  {
    id: "pm-fasal-bima",
    name: "PM Fasal Bima Yojana",
    fullName: "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
    category: "Agriculture",
    governmentType: "Central Government",
    benefit: "Comprehensive Crop Loss Insurance",
    benefitAmount: 150000,
    benefitFrequency: "Direct claim settlement against prevented sowing, localized calamities, post-harvest losses",
    matchScore: 89,
    matchLevel: "Highly Eligible",
    status: "Active",
    applicationMode: "Banks, CSC & PMFBY Portal",
    icon: "Wheat",
    description: "Affordable crop insurance coverage against natural risks, pests, and unseasonal weather with minimal farmer premium rates (1.5% to 2%).",
    overview: "PMFBY provides comprehensive insurance protection against yield losses due to non-preventable natural risks such as drought, floods, pests, landslides, and cyclonic rains.",
    benefits: [
      "Very low premium: 2% for Kharif crops, 1.5% for Rabi crops, and 5% for horticultural crops.",
      "Balance premium is heavily subsidized and shared 50:50 by Central and State Governments.",
      "Claims paid directly via DBT into farmer bank accounts based on satellite and drone yield estimations.",
      "Full sum insured without capping or reduction in benefit amount."
    ],
    eligibility: {
      targetGroup: "All farmers growing notified crops in notified areas including sharecroppers and tenant farmers",
      ageRange: "18 to 75 years",
      incomeLimit: "No income ceiling",
      occupation: "Farmer / Agriculturalist",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card",
      "Land Ownership Document (RoR / Patta) or Tenant / Sharecropper Agreement",
      "Sowing Certificate issued by Patwari / Village Agricultural Officer",
      "Bank Account Passbook"
    ],
    applicationProcess: [
      "Enroll online at pmfby.gov.in or through bank branch / CSC.",
      "Pay farmer share of premium before cutoff date.",
      "Receive insurance policy certificate.",
      "Report crop damage within 72 hours via Crop Insurance App in case of localized calamity."
    ],
    faqs: [
      {
        question: "Can tenant farmers apply without land ownership documents?",
        answer: "Yes. Tenant farmers and sharecroppers can enroll by providing a valid tenancy agreement or village panchayat declaration."
      }
    ]
  },
  {
    id: "atal-pension",
    name: "Atal Pension Yojana",
    fullName: "Atal Pension Yojana (APY)",
    category: "Senior Citizens",
    governmentType: "Central Government",
    benefit: "Guaranteed ₹1,000 - ₹5,000 / Month",
    benefitAmount: 60000,
    benefitFrequency: "Monthly lifelong guaranteed pension starting from age 60",
    matchScore: 80,
    matchLevel: "Potentially Eligible",
    status: "Active",
    applicationMode: "Bank / Post Office Branch & Online",
    icon: "ShieldAlert",
    description: "Government-backed guaranteed pension scheme focused on unorganized sector workers to ensure financial security in retirement.",
    overview: "APY offers a guaranteed minimum monthly pension ranging between ₹1,000 and ₹5,000 upon reaching 60 years of age, depending on contribution amount and entry age.",
    benefits: [
      "Guaranteed pension of ₹1,000, ₹2,000, ₹3,000, ₹4,000, or ₹5,000 per month.",
      "Government guarantees the pension payout even if fund returns are low.",
      "Spouse receives identical pension for life upon subscriber's demise.",
      "Accumulated corpus returned to nominee upon demise of both subscriber and spouse."
    ],
    eligibility: {
      targetGroup: "All Indian citizens working in unorganized sector; must not be income tax payers",
      ageRange: "18 to 40 years",
      incomeLimit: "Non-income tax payer",
      occupation: "Any citizen / unorganized worker",
      state: "All India"
    },
    requiredDocuments: [
      "Aadhaar Card",
      "Savings Bank Account / Post Office Savings Account",
      "Active Mobile Number linked with bank"
    ],
    applicationProcess: [
      "Visit bank branch where savings account is maintained or apply via netbanking.",
      "Provide Aadhaar, nominee details, and select monthly pension amount (₹1,000 - ₹5,000).",
      "Auto-debit setup for monthly/quarterly contribution."
    ],
    faqs: [
      {
        question: "Can income tax payers join Atal Pension Yojana?",
        answer: "From October 1, 2022, citizens who are or have been income tax payers are not eligible to join APY."
      }
    ]
  },
  {
    id: "sukanya-samriddhi",
    name: "Sukanya Samriddhi Yojana",
    fullName: "Sukanya Samriddhi Account (SSY)",
    category: "Women",
    governmentType: "Central Government",
    benefit: "8.2% Interest + Tax-Free Maturity",
    benefitAmount: 1500000,
    benefitFrequency: "High interest small savings scheme with full Section 80C tax exemption",
    matchScore: 79,
    matchLevel: "Potentially Eligible",
    status: "Active",
    applicationMode: "Post Offices & Authorized Commercial Banks",
    icon: "Flame",
    description: "Beti Bachao Beti Padhao flagship savings scheme offering 8.2% government interest for girl child education and marriage.",
    overview: "Sukanya Samriddhi Yojana provides parents/guardians with a secure, sovereign-guaranteed investment vehicle for girl children under 10 years with triple tax exemption (EEE).",
    benefits: [
      "Highest interest rate among small savings schemes (currently 8.2% p.a.).",
      "Triple tax exemption (Exempt on deposit under 80C, exempt on interest, exempt on withdrawal).",
      "Partial withdrawal of up to 50% allowed for higher education after age 18.",
      "Account matures upon girl attaining 21 years or upon marriage after age 18."
    ],
    eligibility: {
      targetGroup: "Parents or legal guardians of girl child below 10 years of age",
      ageRange: "Girl child aged 0 to 10 years",
      incomeLimit: "No income restrictions; deposit between ₹250 and ₹1.5 Lakh per year",
      occupation: "Open to all citizen families",
      state: "All India"
    },
    requiredDocuments: [
      "Girl Child Birth Certificate",
      "Parent / Guardian Aadhaar Card",
      "Address Proof of Guardian",
      "Photographs of child and guardian"
    ],
    applicationProcess: [
      "Collect Form 1 from nearest India Post office or authorized commercial bank.",
      "Submit with girl child's birth certificate and guardian KYC.",
      "Deposit initial minimum amount of ₹250.",
      "Receive official passbook."
    ],
    faqs: [
      {
        question: "How many accounts can be opened in one family?",
        answer: "A maximum of two accounts can be opened per family for two girl children (three in case of twin/triplet girls in first birth)."
      }
    ]
  }
];

export const SCHEME_CATEGORIES = [
  "All Categories",
  "Agriculture",
  "Healthcare",
  "Housing",
  "Employment",
  "Education",
  "Women",
  "Senior Citizens"
];

export const GOVERNMENT_TYPES = [
  "All Governments",
  "Central Government",
  "State Government",
  "Central & State Joint"
];
