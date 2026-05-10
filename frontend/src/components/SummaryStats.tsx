import React from 'react';
import { motion } from 'framer-motion';
import { FileText, ShieldAlert, CheckCircle2 } from 'lucide-react';
import type { FactCheckReport } from '../types';

interface SummaryStatsProps {
  report: FactCheckReport;
}

const STAT_CONFIG = [
  { key: 'VERIFIED', label: 'Verified', color: 'var(--verified)', bg: 'rgba(16, 185, 129, 0.05)', border: 'var(--verified-border)' },
  { key: 'INACCURATE', label: 'Inaccurate', color: 'var(--inaccurate)', bg: 'rgba(245, 158, 11, 0.05)', border: 'var(--inaccurate-border)' },
  { key: 'FALSE', label: 'False', color: 'var(--false)', bg: 'rgba(239, 68, 68, 0.05)', border: 'var(--false-border)' },
  { key: 'UNVERIFIABLE', label: 'Unverifiable', color: 'var(--text-muted)', bg: 'rgba(107, 114, 128, 0.05)', border: 'var(--border)' },
] as const;

export const SummaryStats: React.FC<SummaryStatsProps> = ({ report }) => {
  const issueCount = (report.summary['FALSE'] ?? 0) + (report.summary['INACCURATE'] ?? 0);
  const accuracy = report.total_claims > 0
    ? Math.round(((report.summary['VERIFIED'] ?? 0) / report.total_claims) * 100)
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="glass"
      style={{ padding: '32px', marginBottom: '32px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 24, marginBottom: 40 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: 12 }}>
            <FileText size={20} color="var(--accent-primary)" />
            <h2 className="gradient-text" style={{ fontSize: '1.75rem', fontWeight: 850, letterSpacing: '-0.8px' }}>Analysis Report</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', fontWeight: 500 }}>
             {report.filename} <span style={{ opacity: 0.3, margin: '0 8px' }}>|</span> {report.total_claims} claims analyzed
          </p>
        </div>

        <div style={{
          padding: '10px 20px',
          borderRadius: '12px',
          background: issueCount > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
          border: `1px solid ${issueCount > 0 ? 'var(--false-border)' : 'var(--verified-border)'}`,
          display: 'flex', alignItems: 'center', gap: '10px'
        }}>
          {issueCount > 0 ? <ShieldAlert size={18} color="var(--false)" /> : <CheckCircle2 size={18} color="var(--verified)" />}
          <span style={{ 
            color: issueCount > 0 ? 'var(--false)' : 'var(--verified)', 
            fontWeight: 800, fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.5px' 
          }}>
            {issueCount > 0 ? `${issueCount} Critical Issues` : 'Document Verified'}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: 40 }}>
        {STAT_CONFIG.map((s, i) => (
          <motion.div
            key={s.key}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
            style={{ 
              padding: '24px', borderRadius: '16px', background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border)', textAlign: 'center'
            }}
          >
            <p style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: 8 }}>
              {s.label}
            </p>
            <p style={{ fontSize: '2rem', fontWeight: 900, color: s.color, lineHeight: 1 }}>
              {report.summary[s.key] ?? 0}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Accuracy Dashboard Section */}
      <div style={{ 
        padding: '24px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', 
        border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '32px' 
      }}>
        <div style={{ flexShrink: 0 }}>
           <p style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
             Trust Score
           </p>
           <p style={{ 
             fontSize: '2.5rem', fontWeight: 950, 
             color: accuracy >= 80 ? 'var(--verified)' : accuracy >= 50 ? 'var(--inaccurate)' : 'var(--false)' 
           }}>
             {accuracy}%
           </p>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ height: 12, width: '100%', background: 'var(--bg-primary)', borderRadius: 6, overflow: 'hidden', border: '1px solid var(--border)' }}>
             <motion.div
               initial={{ width: 0 }}
               animate={{ width: `${accuracy}%` }}
               transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
               style={{ 
                 height: '100%', 
                 background: accuracy >= 80 ? 'var(--verified)' : accuracy >= 50 ? 'var(--inaccurate)' : 'var(--false)',
                 boxShadow: `0 0 20px ${accuracy >= 80 ? 'var(--verified)' : accuracy >= 50 ? 'var(--inaccurate)' : 'var(--false)'}44`
               }}
             />
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 12 }}>
             {accuracy >= 80 ? 'This document meets high-confidence verification standards.' : 
              accuracy >= 50 ? 'Proceed with caution: several claims require correction.' : 
              'Warning: High volume of inaccuracies detected in this source.'}
          </p>
        </div>
      </div>
    </motion.div>
  );
};
