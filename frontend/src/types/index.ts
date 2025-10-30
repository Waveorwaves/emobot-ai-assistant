// Types for AI Reasoning Assistant

export interface BackendQueryResponse {
  success: boolean;
  response: string;
  session_id: string;
  timestamp: string;
  memory_stats?: Record<string, any>;
}

export interface BackendHealthResponse {
  status: string;
  mcp_server: string;
  active_sessions: number;
  timestamp: string;
}

export interface ReasoningStep {
  step: number;
  action: string;
  reasoning: string;
  confidence: number;
}

export interface ReasoningRequest {
  user_request: string;
  context_data?: Record<string, any>;
  session_id?: string;
  model_id?: string;
  user_id?: string;
}

export interface ReasoningResponse {
  interaction_id: number;
  reasoning_steps: ReasoningStep[];
  final_plan: Record<string, any>;
  overall_confidence: number;
  processing_time: number;
  raw_response?: BackendQueryResponse;
}

export interface CorrectionRequest {
  interaction_id: number;
  step_corrections: Record<number, string>;
  satisfaction_rating: number;
  feedback?: string;
}

export interface MetricsData {
  accuracy_trends: Array<{
    date: string;
    accuracy: number;
    satisfaction: number;
    interactions: number;
  }>;
  correction_stats: {
    total_corrections: number;
    avg_corrections_per_interaction: number;
    correction_rate: number;
  };
  user_satisfaction: {
    average: number;
    trend: string;
  };
  learning_progress: {
    total_interactions: number;
    interactions_with_feedback: number;
    learning_data_quality: number;
    estimated_improvement: number;
  };
}

export interface ApiError {
  detail: string;
}
