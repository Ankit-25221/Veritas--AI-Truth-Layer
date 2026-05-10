export type ClaimCategory = 'statistic' | 'date' | 'financial' | 'technical' | 'general';
export type ClaimVerdict = 'VERIFIED' | 'INACCURATE' | 'FALSE' | 'UNVERIFIABLE';
export type JobStatus =
  | 'queued'
  | 'extracting_text'
  | 'extracting_claims'
  | 'searching_web'
  | 'verifying_claims'
  | 'generating_report'
  | 'completed'
  | 'failed';

export interface Evidence {
  source_url: string;
  source_title: string;
  excerpt: string;
  supports_claim: boolean;
}

export interface ClaimResult {
  claim_id: string;
  text: string;
  category: ClaimCategory;
  verdict: ClaimVerdict;
  confidence: number;
  evidence: Evidence[];
  correction: string | null;
  explanation: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
  total_claims: number | null;
  processed_claims: number | null;
}

export interface FactCheckReport {
  job_id: string;
  filename: string;
  status: JobStatus;
  created_at: string;
  completed_at: string | null;
  summary: Record<ClaimVerdict, number>;
  summary_note?: string | null;
  claims: ClaimResult[];
  total_claims: number;
}

export interface UploadResponse {
  job_id: string;
  message: string;
  filename: string;
}
