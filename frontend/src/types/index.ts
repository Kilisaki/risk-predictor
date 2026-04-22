// ─── Model & Config ─────────────────────────────────────────────────────────

export interface ModelVersionInfo {
  is_current: boolean;
  features_count: number;
  framework: string;
  model_type: string;
  loaded_at?: string;
  file_size_mb?: number;
}

export interface ModelConfig {
  available_versions: string[];
  current_version: string;
  features: string[];
  top_features: string[];
  categorical_features: string[];
}

// ─── Patient ─────────────────────────────────────────────────────────────────

export interface PatientCreate {
  sex: string;
  birth_date: string; // ISO date string "YYYY-MM-DD"
}

export interface PatientResponse {
  id: number;
  sex: string;
  birth_date: string;
  created_at: string;
}

// ─── Operation ───────────────────────────────────────────────────────────────

export interface OperationCreate {
  patient_id: number;
  type: string;
  date: string; // ISO date string "YYYY-MM-DD"
}

export interface OperationResponse {
  id: number;
  patient_id: number;
  type: string;
  date: string;
  created_at: string;
}

// ─── Prediction ───────────────────────────────────────────────────────────────

export interface PredictRequest {
  features: Record<string, unknown>;
  model_version?: string;
  operation_id?: number;
}

export interface PredictResultAnonymous {
  status: 'completed';
  saved: false;
  result: {
    risk_score: number;
    risk_level: 'low' | 'medium' | 'high';
    version: string;
    framework?: string;
    risk_percent?: number;
  };
}

export interface PredictResultAsync {
  task_id: string;
  status: 'pending';
}

export type PredictResponse = PredictResultAnonymous | PredictResultAsync;

export interface TaskStatus {
  status: 'pending' | 'completed' | 'failed';
  operation_id?: number;
  result?: {
    risk_score: number;
    risk_level: 'low' | 'medium' | 'high';
    version: string;
    framework?: string;
    risk_percent?: number;
  };
  error?: string;
}

// ─── UI State ────────────────────────────────────────────────────────────────

export type RiskLevel = 'low' | 'medium' | 'high';

export interface PredictionResult {
  risk_score: number;
  risk_level: RiskLevel;
  version: string;
  framework?: string;
}
