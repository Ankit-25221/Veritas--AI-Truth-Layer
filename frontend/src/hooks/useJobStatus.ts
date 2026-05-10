import { useState, useEffect, useRef, useCallback } from 'react';
import { getJobStatus, getReport } from '../api/client';
import type { JobStatusResponse, FactCheckReport } from '../types';

interface UseJobStatusReturn {
  status: JobStatusResponse | null;
  report: FactCheckReport | null;
  error: string | null;
  isPolling: boolean;
}

const POLL_INTERVAL_MS = 2000;
const INITIAL_DELAY_MS = 500;

export const useJobStatus = (jobId: string | null): UseJobStatusReturn => {
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [report, setReport] = useState<FactCheckReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // Ref lives for the component's lifetime — safe to mutate without re-render
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const poll = useCallback(async () => {
    if (!jobId || !isMountedRef.current) return;
    try {
      const s = await getJobStatus(jobId);
      if (!isMountedRef.current) return;
      setStatus(s);

      if (s.status === 'completed') {
        const r = await getReport(jobId);
        if (!isMountedRef.current) return;
        setReport(r);
        setIsPolling(false);
        return;
      }

      if (s.status === 'failed') {
        setError(s.message);
        setIsPolling(false);
        return;
      }

      // Schedule next poll
      timerRef.current = setTimeout(poll, POLL_INTERVAL_MS);
    } catch (e: unknown) {
      if (!isMountedRef.current) return;
      const msg = e instanceof Error ? e.message : 'Unknown polling error.';
      setError(msg);
      setIsPolling(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId) {
      // Reset state when jobId is cleared
      setStatus(null);
      setReport(null);
      setError(null);
      setIsPolling(false);
      clearTimer();
      return;
    }

    setIsPolling(true);
    setError(null);
    setReport(null);
    setStatus(null);

    // Small initial delay to avoid immediate fetch before server registers the job
    timerRef.current = setTimeout(poll, INITIAL_DELAY_MS);

    return clearTimer;
  }, [jobId, poll, clearTimer]);

  return { status, report, error, isPolling };
};
