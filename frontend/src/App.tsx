import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ShieldCheck, Github } from 'lucide-react';
import { uploadPDF } from './api/client';
import { useJobStatus } from './hooks/useJobStatus';
import { UploadZone } from './components/UploadZone';
import { ProcessingView } from './components/ProcessingView';
import { ReportView } from './components/ReportView';

type AppState = 'idle' | 'uploading' | 'processing' | 'done' | 'error';

export default function App() {
  const [appState, setAppState] = useState<AppState>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { status, report, error: pollError } = useJobStatus(
    appState === 'processing' ? jobId : null
  );

  // Auto-transition to done when report arrives
  React.useEffect(() => {
    if (report && appState === 'processing') setAppState('done');
  }, [report, appState]);

  React.useEffect(() => {
    if (pollError && appState === 'processing') setAppState('error');
  }, [pollError, appState]);

  const handleUpload = async (file: File) => {
    setUploadError(null);
    setAppState('uploading');
    try {
      const res = await uploadPDF(file);
      setJobId(res.job_id);
      setAppState('processing');
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Upload failed. Please try again.';
      setUploadError(msg);
      setAppState('idle');
    }
  };

  const handleReset = () => {
    setAppState('idle');
    setJobId(null);
    setUploadError(null);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 🌀 Senior Tech: Dynamic Mesh Background */}
      <div className="bg-mesh" />

      {/* ── Header ── */}
      <header style={{
        position: 'sticky', top: 0, zIndex: 100,
        backdropFilter: 'blur(20px)', borderBottom: '1px solid var(--border)',
        background: 'rgba(3, 7, 18, 0.6)',
      }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: 40, height: 40, borderRadius: '12px',
              background: 'linear-gradient(135deg, #ef4444, #b91c1c)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 8px 20px rgba(239, 68, 68, 0.25)',
            }}>
              <ShieldCheck size={22} color="white" />
            </div>
            <div>
              <span className="crimson-text" style={{ fontWeight: 850, fontSize: '1.25rem', letterSpacing: '-0.8px' }}>Veritas</span>
              <span style={{ 
                fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', 
                background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--border-active)',
                marginLeft: '6px', color: 'var(--accent-primary)', fontWeight: 700,
                textTransform: 'uppercase', verticalAlign: 'middle'
              }}>Beta</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <a href="#" className="nav-link" style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}></a>
            <a href="#" className="nav-link" style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}></a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              style={{ 
                padding: '8px 16px', borderRadius: '8px', border: '1px solid var(--border)',
                color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px', 
                fontSize: '0.85rem', textDecoration: 'none', background: 'rgba(255,255,255,0.03)',
                transition: 'var(--transition)'
              }}
            >
              <Github size={16} /> GitHub
            </a>
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main style={{ flex: 1, position: 'relative', zIndex: 1, paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <AnimatePresence mode="wait">
            {(appState === 'idle' || appState === 'uploading') && (
              <motion.div
                key="idle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
              >
                {/* Hero Section: Engineered for maximum impact */}
                <div style={{ textAlign: 'center', marginBottom: 80 }}>
                  <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    style={{ 
                      fontSize: 'clamp(3rem, 8vw, 5rem)', 
                      fontWeight: 900, 
                      lineHeight: 0.95, 
                      marginBottom: 32, 
                      letterSpacing: '-2.5px' 
                    }}
                  >
                    The <span className="crimson-text">Truth Layer</span> for<br />
                    <span className="gradient-text">AI Generation.</span>
                  </motion.h1>

                  <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2, duration: 0.8 }}
                    style={{ 
                      fontSize: '1.35rem', 
                      color: 'var(--text-secondary)', 
                      maxWidth: 720, 
                      margin: '0 auto 48px', 
                      lineHeight: 1.5,
                      fontWeight: 400
                    }}
                  >
                    Catch hallucinated stats before they damage your brand.{' '}
                    <strong>Veritas</strong> provides automated verification against real-time,
                    authoritative data sources.
                  </motion.p>
                </div>

                {/* Upload card */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.25 }}
                  className="glass"
                  style={{ padding: '40px', maxWidth: 680, margin: '0 auto' }}
                >
                  <UploadZone onUpload={handleUpload} isLoading={appState === 'uploading'} />
                  {uploadError && (
                    <p style={{ color: 'var(--false)', fontSize: '0.85rem', marginTop: 12, textAlign: 'center' }}>
                      {uploadError}
                    </p>
                  )}
                </motion.div>

                {/* Steps Section */}
                <div style={{ 
                  marginTop: 100, 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
                  gap: 32,
                  textAlign: 'left'
                }}>
                  <div className="glass" style={{ padding: 32 }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-light)', marginBottom: 12 }}>01 — EXTRACT</div>
                    <h3 style={{ marginBottom: 12 }}>Identify claims</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                      Parse the PDF and identify every verifiable claim — statistics, dates, financial figures, technical specs.
                    </p>
                  </div>
                  <div className="glass" style={{ padding: 32 }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-light)', marginBottom: 12 }}>02 — VERIFY</div>
                    <h3 style={{ marginBottom: 12 }}>Live data sync</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                      Cross-reference each claim against live web data and authoritative sources across the internet.
                    </p>
                  </div>
                  <div className="glass" style={{ padding: 32 }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--accent-light)', marginBottom: 12 }}>03 — REPORT</div>
                    <h3 style={{ marginBottom: 12 }}>Verdict analysis</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                      A trust score, flagged inaccuracies, and the correct values — ready to share or export instantly.
                    </p>
                  </div>
                </div>

                {/* Feature pills */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  style={{ display: 'flex', justifyContent: 'center', gap: '12px', marginTop: 32, flexWrap: 'wrap' }}
                >
                  {['📊 Stats', '📅 Dates', '💰 Financials', '⚙️ Tech Specs'].map(tag => (
                    <span key={tag} style={{
                      padding: '6px 14px', borderRadius: '99px', fontSize: '0.8rem',
                      background: 'var(--bg-card)', border: '1px solid var(--border)',
                      color: 'var(--text-secondary)',
                    }}>
                      {tag}
                    </span>
                  ))}
                </motion.div>
              </motion.div>
            )}

            {appState === 'processing' && (
              <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div style={{ maxWidth: 620, margin: '0 auto' }}>
                  <ProcessingView status={status} />
                </div>
              </motion.div>
            )}

            {appState === 'done' && report && (
              <motion.div key="done" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <ReportView report={report} onReset={handleReset} />
              </motion.div>
            )}

            {appState === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ textAlign: 'center', padding: 60 }}
              >
                <p style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</p>
                <h2 style={{ marginBottom: 12 }}>Something went wrong</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>{pollError}</p>
                <button className="btn-primary" onClick={handleReset}>Try Again</button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* ── Footer ── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '40px 0', opacity: 0.8 }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: 12 }}>
            <div style={{ width: 20, height: 20, borderRadius: '6px', background: 'linear-gradient(135deg, #ef4444, #f87171)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ShieldCheck size={12} color="white" />
            </div>
            <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Veritas</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            &copy; 2026 Veritas — built for the GEO ecosystem.
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 8 }}>
            A truth layer for the generative web.
          </p>
        </div>
      </footer>
    </div>
  );
}
