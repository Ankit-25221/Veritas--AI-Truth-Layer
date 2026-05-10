import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Brain, Globe, ShieldCheck, FileOutput, CheckCircle2, Circle } from 'lucide-react';
import type { JobStatusResponse } from '../types';

interface ProcessingViewProps {
  status: JobStatusResponse | null;
}

const STEPS = [
  { key: 'extracting_text',    label: 'Extracting PDF Text',    icon: FileText,    statuses: ['extracting_text'] },
  { key: 'extracting_claims',  label: 'Identifying Claims',      icon: Brain,       statuses: ['extracting_claims'] },
  { key: 'searching_web',      label: 'Searching Live Web',      icon: Globe,       statuses: ['searching_web'] },
  { key: 'verifying_claims',   label: 'Verifying with AI',       icon: ShieldCheck, statuses: ['verifying_claims'] },
  { key: 'generating_report',  label: 'Generating Report',       icon: FileOutput,  statuses: ['generating_report', 'completed'] },
];

const STATUS_ORDER = ['queued','extracting_text','extracting_claims','searching_web','verifying_claims','generating_report','completed'];

const getStepState = (stepStatuses: string[], currentStatus: string): 'done' | 'active' | 'pending' => {
  const currentIdx = STATUS_ORDER.indexOf(currentStatus);
  for (const s of stepStatuses) {
    const stepIdx = STATUS_ORDER.indexOf(s);
    if (currentIdx > stepIdx) return 'done';
    if (currentIdx === stepIdx) return 'active';
  }
  return 'pending';
};

export const ProcessingView: React.FC<ProcessingViewProps> = ({ status }) => {
  const currentStatus = status?.status ?? 'queued';
  const progress = status?.progress ?? 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass"
      style={{ padding: '36px', display: 'flex', flexDirection: 'column', gap: '28px' }}
    >
      <div style={{ textAlign: 'center' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: 8 }}>
          Analyzing Document...
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          {status?.message ?? 'Initializing pipeline...'}
        </p>
        {status?.total_claims && (
          <p style={{ color: 'var(--accent-light)', fontSize: '0.85rem', marginTop: 6, fontWeight: 500 }}>
            {status.processed_claims ?? 0} / {status.total_claims} claims verified
          </p>
        )}
      </div>

      {/* Progress bar */}
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          initial={{ width: '0%' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
      <p style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: -20 }}>
        {progress}% complete
      </p>

      {/* Step list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {STEPS.map((step, i) => {
          const state = getStepState(step.statuses, currentStatus);
          const Icon = step.icon;
          return (
            <motion.div
              key={step.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                padding: '14px 18px',
                borderRadius: 'var(--radius)',
                border: `1px solid ${state === 'active' ? 'var(--border-active)' : 'var(--border)'}`,
                background: state === 'active' ? 'rgba(99,102,241,0.08)' : state === 'done' ? 'rgba(16,185,129,0.05)' : 'transparent',
                transition: 'all 300ms ease',
              }}
            >
              <div style={{
                width: 36, height: 36, borderRadius: '8px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: state === 'done' ? 'var(--verified-bg)' : state === 'active' ? 'rgba(99,102,241,0.15)' : 'var(--bg-card)',
                flexShrink: 0,
              }}>
                {state === 'done'
                  ? <CheckCircle2 size={18} color="var(--verified)" />
                  : state === 'active'
                  ? <Icon size={18} color="var(--accent-light)" style={{ animation: 'pulse-glow 1.5s infinite' }} />
                  : <Circle size={18} color="var(--text-muted)" />
                }
              </div>
              <span style={{
                fontWeight: 500,
                color: state === 'done' ? 'var(--verified)' : state === 'active' ? 'var(--text-primary)' : 'var(--text-muted)',
                fontSize: '0.9rem',
              }}>
                {step.label}
              </span>
              {state === 'active' && (
                <div className="spinner" style={{ marginLeft: 'auto', opacity: 0.7 }} />
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};
