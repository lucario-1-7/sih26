export type Category =
  | 'Education'
  | 'Agriculture'
  | 'Healthcare'
  | 'Water Resources'
  | 'Environment'
  | 'Energy'
  | 'Urban Development'
  | 'Accessibility'
  | 'Public Administration'
  | 'Rural Livelihoods';

export type ProblemStatus =
  | 'Submitted'
  | 'Under Review'
  | 'Matched with Institution'
  | 'In Progress'
  | 'Solution Implemented';

export interface Milestone {
  id: string;
  problemId: string;
  stage: ProblemStatus;
  title: string;
  description: string;
  timestamp: string;
  completed: boolean;
  institution?: string;
  officerName?: string;
  evidenceNote?: string;
}

export interface ProblemMedia {
  id: string;
  type: 'image' | 'video' | 'document';
  url: string;
  name: string;
  size?: string;
}

export interface ProblemLocation {
  district: string;
  block?: string;
  villageOrArea: string;
  pincode?: string;
  latitude: number;
  longitude: number;
  formattedAddress: string;
}

export interface Problem {
  id: string;
  trackingCode: string;
  title: string;
  category: Category;
  description: string;
  location: ProblemLocation;
  media: ProblemMedia[];
  status: ProblemStatus;
  upvotes: number;
  submittedBy: {
    id: string;
    fullName: string;
    phone: string;
    district: string;
    isVerified: boolean;
  };
  matchedInstitution?: {
    name: string;
    type: 'University' | 'IIT' | 'NIT' | 'R&D Center' | 'Polytechnic';
    leadResearcher?: string;
    department?: string;
    projectTitle?: string;
  };
  solutionSummary?: string;
  impactMetrics?: string;
  milestones: Milestone[];
  createdAt: string;
  updatedAt: string;
}

/** The backend's citizen User model only has id/phone/name — age, district,
 * and pincode are not real fields on any account and are never fabricated
 * here (the previous "profile completion" step that collected them locally
 * has been removed — see login/page.tsx). */
export interface User {
  id: string;
  fullName: string;
  phone: string;
  isVerified: boolean;
}

export type Language = 'en' | 'hi';
export type TextScale = 'normal' | 'large' | 'larger';
