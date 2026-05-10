import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ExternalLink, AlertTriangle, CheckCircle2, XCircle, HelpCircle, type LucideIcon } from 'lucide-react';
import type { ClaimResult, ClaimVerdict } from '../types';

interface ClaimCardProps {
  claim: ClaimResult;
  index: number;
}

const VERDICT_CONFIG: Record<ClaimVerdict, {
  label: string; icon: LucideIcon; color: string;
  bg: string; border: string; accent: string;
}> = {
  VERIFIED: {
    label: 'Verified', icon: CheckCircle2, color: 'var(--verified)',
    bg: 'rgba(16, 185, 129, 0.05)', border: 'var(--verified-border)', accent: '#10b981',
  },
  INACCURATE: {
    label: 'Inaccurate', icon: AlertTriangle, color: 'var(--inaccurate)',
    bg: 'rgba(245, 158, 11, 0.05)', border: 'var(--inaccurate-border)', accent: '#f59e0b',
  },
  FALSE: {
    label: 'False', icon: XCircle, color: 'var(--false)',
    bg: 'rgba(239, 68, 68, 0.05)', border: 'var(--false-border)', accent: '#ef4444',
  },
  UNVERIFIABLE: {
    label: 'Unverifiable', icon: HelpCircle, color: 'var(--text-muted)',
    bg: 'rgba(107, 114, 128, 0.05)', border: 'var(--border)', accent: '#6b7280',
  },
};

const CATEGORY_LABEL: Record<string, string> = {
  statistic: '📊 Statistic', date: '📅 Date', financial: '💰 Financial',
  technical: '⚙️ Technical', general: '📝 General',
};

export const ClaimCard: React.FC<ClaimCardProps> = ({ claim, index }) => {
  const [expanded, setExpanded] = useState(claim.verdict !== 'VERIFIED');
  const cfg = VERDICT_CONFIG[claim.verdict];
  const VerdictIcon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        delay: index * 0.08, 
        duration: 0.8, 
        ease: [0.16, 1, 0.3, 1] 
      }}
      className="glass"
      style={{
        borderLeftColor: cfg.accent,
        borderLeftWidth: '4px',
        borderColor: expanded ? 'var(--border-active)' : 'var(--border)',
        overflow: 'hidden',
        position: 'relative',
        marginBottom: '12px',
      }}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', gap: '20px',
          padding: '24px', background: 'none', border: 'none', cursor: 'pointer',
          textAlign: 'left',
        }}
      >
        {/* Status indicator */}
        <div style={{
          width: 44, height: 44, borderRadius: '12px', flexShrink: 0,
          background: cfg.bg, border: `1px solid ${cfg.border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: `0 4px 12px ${cfg.bg}`,
        }}>
          <VerdictIcon size={22} color={cfg.color} />
        </div>

        {/* Claim text + meta */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{
            color: 'var(--text-primary)', fontWeight: 600, fontSize: '1.05rem',
            lineHeight: 1.4, marginBottom: 10, letterSpacing: '-0.2px'
          }}>
            "{claim.text}"
          </p>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ 
              fontSize: '0.7rem', fontWeight: 800, color: cfg.color, 
              textTransform: 'uppercase', letterSpacing: '1px',
              padding: '4px 10px', borderRadius: '6px', background: cfg.bg,
              border: `1px solid ${cfg.border}`
            }}>
              {cfg.label}
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ opacity: 0.5 }}>|</span> {CATEGORY_LABEL[claim.category] ?? claim.category}
            </span>
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
               <div style={{ width: 60, height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                  <div style={{ width: `${claim.confidence * 100}%`, height: '100%', background: cfg.color }} />
               </div>
               <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                {Math.round(claim.confidence * 100)}%
              </span>
            </div>
          </div>
        </div>

        <motion.div animate={{ rotate: expanded ? 180 : 0 }}>
          <ChevronDown size={20} color="var(--text-muted)" />
        </motion.div>
      </button>

      {/* Expandable body */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            <div style={{ padding: '0 24px 24px 88px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ height: 1, background: 'var(--border)' }} />

              {/* Analysis */}
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 10 }}>
                  Strategic Analysis
                </h4>
                <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {claim.explanation}
                </p>
              </div>

              {/* Correction Card */}
              {claim.correction && (
                <div style={{
                  padding: '20px', borderRadius: '12px',
                  background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.1)',
                  position: 'relative', overflow: 'hidden'
                }}>
                  <div style={{ position: 'absolute', top: 0, left: 0, width: 2, height: '100%', background: 'var(--accent-primary)' }} />
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-primary)', textTransform: 'uppercase', marginBottom: 8 }}>
                    Recommended Correction
                  </h4>
                  <p style={{ fontSize: '1rem', color: 'var(--text-primary)', fontWeight: 500, lineHeight: 1.5 }}>
                    {claim.correction}
                  </p>
                </div>
              )}

              {/* Evidence Dashboard */}
              {claim.evidence.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 12 }}>
                    Authoritative Sources
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
                    {claim.evidence.map((ev, i) => (
                      <a
                        key={i}
                        href={ev.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'block', padding: '16px',
                          borderRadius: '10px', background: 'rgba(255,255,255,0.02)',
                          border: '1px solid var(--border)',
                          textDecoration: 'none', transition: 'var(--transition)',
                        }}
                        onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--border-active)'}
                        onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                           <p style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', paddingRight: 10 }}>
                              {ev.source_title}
                           </p>
                           <ExternalLink size={14} color="var(--text-muted)" />
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                          {ev.excerpt.slice(0, 120)}...
                        </p>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
