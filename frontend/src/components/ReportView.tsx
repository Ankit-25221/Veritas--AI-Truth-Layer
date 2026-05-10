import React from 'react';
import { motion } from 'framer-motion';
import { RotateCcw } from 'lucide-react';
import type { FactCheckReport } from '../types';
import { SummaryStats } from './SummaryStats';
import { ClaimCard } from './ClaimCard';

interface ReportViewProps {
  report: FactCheckReport;
  onReset: () => void;
}

export const ReportView: React.FC<ReportViewProps> = ({ report, onReset }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}
    >
      <SummaryStats report={report} />

      {report.claims.length === 0 ? (
        <div className="glass" style={{ padding: '40px', textAlign: 'center' }}>
          <p style={{ fontSize: '2.5rem', marginBottom: 16 }}>📝</p>
          <h3 style={{ marginBottom: 12 }}>No Verifiable Claims Detected</h3>
          <p style={{ 
            color: 'var(--text-secondary)', 
            fontSize: '0.95rem', 
            lineHeight: 1.6, 
            maxWidth: 480, 
            margin: '0 auto' 
          }}>
            {report.summary_note || "No specific verifiable claims were found in this document."}
          </p>
        </div>
      ) : (
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Individual Claims ({report.total_claims})
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {report.claims.map((claim, i) => (
              <ClaimCard key={claim.claim_id} claim={claim} index={i} />
            ))}
          </div>
        </div>
      )}

      <button
        className="btn-primary"
        onClick={onReset}
        style={{ alignSelf: 'center', marginTop: 8 }}
      >
        <RotateCcw size={16} />
        Check Another Document
      </button>
    </motion.div>
  );
};
