import axios, { AxiosError } from 'axios';
import type { UploadResponse, JobStatusResponse, FactCheckReport } from '../types';

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? '';

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30_000,
});

/** Normalise Axios errors into plain Error objects with a useful message. */
function handleError(err: unknown): never {
  if (err instanceof AxiosError) {
    const detail = err.response?.data?.detail;
    const msg =
      typeof detail === 'string'
        ? detail
        : err.message ?? 'An unexpected error occurred.';
    throw new Error(msg);
  }
  throw err;
}

export const uploadPDF = async (file: File): Promise<UploadResponse> => {
  try {
    const form = new FormData();
    form.append('file', file);
    const { data } = await api.post<UploadResponse>('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  } catch (err) {
    handleError(err);
  }
};

export const getJobStatus = async (jobId: string): Promise<JobStatusResponse> => {
  try {
    const { data } = await api.get<JobStatusResponse>(`/status/${jobId}`);
    return data;
  } catch (err) {
    handleError(err);
  }
};

export const getReport = async (jobId: string): Promise<FactCheckReport> => {
  try {
    const { data } = await api.get<FactCheckReport>(`/report/${jobId}`);
    return data;
  } catch (err) {
    handleError(err);
  }
};
