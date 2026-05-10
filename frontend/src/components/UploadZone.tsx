import React, { useCallback, useState } from 'react';
import { useDropzone, type FileRejection } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, X, Zap, ShieldCheck } from 'lucide-react';

interface UploadZoneProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const UploadZone: React.FC<UploadZoneProps> = ({ onUpload, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[], rejected: FileRejection[]) => {
    setError(null);
    if (rejected && rejected.length > 0) {
      setError('Only PDF files up to 20 MB are accepted.');
      return;
    }
    if (accepted[0]) setSelectedFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 20 * 1024 * 1024,
    disabled: isLoading,
  });

  const handleSubmit = () => {
    if (selectedFile && !isLoading) onUpload(selectedFile);
  };

  // Spread getRootProps onto a plain div so framer-motion doesn't receive
  // conflicting native DOM event handler types (e.g. onAnimationStart).
  const rootProps = getRootProps();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <motion.div
        animate={{
          scale: isDragActive ? 1.02 : 1,
          borderColor: isDragActive
            ? 'var(--accent-primary)'
            : selectedFile
            ? 'var(--verified)'
            : 'var(--border)',
        }}
        style={{
          border: '2px dashed',
          borderRadius: '24px',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {/* Plain div receives the dropzone handlers to avoid type conflicts */}
        <div
          {...rootProps}
          style={{
            padding: '60px 40px',
            textAlign: 'center',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            background: isDragActive ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255, 255, 255, 0.02)',
            boxShadow: isDragActive ? '0 0 40px rgba(239, 68, 68, 0.1)' : 'none',
            transition: 'background 0.3s ease, box-shadow 0.3s ease',
          }}
        >
          <input {...getInputProps()} />

          <AnimatePresence mode="wait">
            {selectedFile ? (
              <motion.div
                key="file"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}
              >
                <div style={{
                  width: 64, height: 64, borderRadius: '16px',
                  background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--verified-border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 8px 24px rgba(16, 185, 129, 0.1)',
                }}>
                  <FileText size={32} color="var(--verified)" />
                </div>
                <div>
                  <p style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '1.1rem' }}>{selectedFile.name}</p>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    {formatBytes(selectedFile.size)} · Ready for analysis
                  </p>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--accent-primary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Click to Replace
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}
              >
                <div style={{
                  width: 80, height: 80, borderRadius: '20px',
                  background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  position: 'relative',
                }}>
                  <Upload size={32} color={isDragActive ? 'var(--accent-primary)' : 'var(--text-muted)'} />
                  {isDragActive && (
                    <motion.div
                      layoutId="glow"
                      style={{ position: 'absolute', inset: -4, borderRadius: '24px', border: '2px solid var(--accent-primary)', opacity: 0.5 }}
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                    />
                  )}
                </div>
                <div>
                  <p style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8, letterSpacing: '-0.5px' }}>
                    {isDragActive ? 'Drop to Begin' : 'Drop your PDF here'}
                  </p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '1rem', lineHeight: 1.5 }}>
                    or <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>browse files</span><br />
                    <span style={{ fontSize: '0.8rem' }}>Maximum file size: 20 MB</span>
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '16px', borderRadius: '12px',
            background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--false-border)',
            color: 'var(--false)', fontSize: '0.9rem', fontWeight: 600,
          }}
        >
          <X size={18} />
          {error}
        </motion.div>
      )}

      <button
        className="btn-primary"
        onClick={handleSubmit}
        disabled={!selectedFile || isLoading}
        style={{
          width: '100%',
          height: '60px',
          fontSize: '1.1rem',
          letterSpacing: '0.5px',
          textTransform: 'uppercase',
        }}
      >
        {isLoading ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            >
              <ShieldCheck size={24} />
            </motion.div>
            Analyzing Neural Layers...
          </div>
        ) : (
          <>
            <Zap size={20} fill="currentColor" />
            Analyze Document
          </>
        )}
      </button>
    </div>
  );
};
