import axios from 'axios';
import type {
  ModelConfig,
  PatientCreate,
  PatientResponse,
  OperationCreate,
  OperationResponse,
  PredictRequest,
  PredictResponse,
  TaskStatus,
} from '@/types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
});

// ─── Config ──────────────────────────────────────────────────────────────────

export const fetchModelConfig = async (version?: string): Promise<ModelConfig> => {
  const params = version ? { version } : {};
  const { data } = await api.get<ModelConfig>('/predictions/config', { params });
  return data;
};

// ─── Predictions ─────────────────────────────────────────────────────────────

export const predict = async (req: PredictRequest): Promise<PredictResponse> => {
  const { data } = await api.post<PredictResponse>('/predictions/predict', req);
  return data;
};

export const fetchTaskStatus = async (taskId: string): Promise<TaskStatus> => {
  const { data } = await api.get<TaskStatus>(`/predictions/status/${taskId}`);
  return data;
};

// ─── Patients ────────────────────────────────────────────────────────────────

export const createPatient = async (patient: PatientCreate): Promise<PatientResponse> => {
  const { data } = await api.post<PatientResponse>('/patients', patient);
  return data;
};

export const fetchPatient = async (id: number): Promise<PatientResponse> => {
  const { data } = await api.get<PatientResponse>(`/patients/${id}`);
  return data;
};

// ─── Operations ──────────────────────────────────────────────────────────────

export const createOperation = async (operation: OperationCreate): Promise<OperationResponse> => {
  const { data } = await api.post<OperationResponse>('/operations', operation);
  return data;
};
