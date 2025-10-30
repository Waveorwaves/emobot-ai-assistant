// API utilities for the Emobot frontend

import axios from 'axios';
import {
  BackendQueryResponse,
  BackendHealthResponse,
  ReasoningRequest,
  ReasoningResponse,
  CorrectionRequest,
  MetricsData,
} from '../types';

const API_BASE_URL =
  ((import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE_URL?.trim()) ||
  'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(
      `❌ API Error: ${error.response?.status} ${error.config?.url}`,
      error.response?.data
    );
    return Promise.reject(error);
  }
);

export const reasoningApi = {
  async submitRequest(request: ReasoningRequest): Promise<ReasoningResponse> {
    const started = performance.now();
    const {
      user_request,
      context_data,
      session_id = 'web-session',
      model_id = 'gemini-2.0-flash',
      user_id,
    } = request;

    const payload = {
      query: user_request,
      session_id,
      model_id,
      user_id,
      context: context_data,
    };

    const response = await api.post<BackendQueryResponse>('/api/query', payload);
    const elapsedSeconds = (performance.now() - started) / 1000;
    const data = response.data;
    const text = data.response;

    return {
      interaction_id: Date.now(),
      reasoning_steps: [
        {
          step: 1,
          action: 'Agent Response',
          reasoning: text,
          confidence: data.success ? 0.9 : 0.4,
        },
      ],
      final_plan: {
        summary: text,
      },
      overall_confidence: data.success ? 0.9 : 0.4,
      processing_time: elapsedSeconds,
      raw_response: data,
    };
  },

  async submitCorrections(
    corrections: CorrectionRequest
  ): Promise<{ success: boolean; message: string }> {
    console.warn(
      'submitCorrections is not supported by the backend yet. Request:',
      corrections
    );
    return {
      success: true,
      message: 'Corrections captured locally (no backend endpoint available).',
    };
  },

  async getMetrics(): Promise<MetricsData> {
    console.warn(
      'getMetrics is not supported by the backend yet. Returning placeholder data.'
    );
    return {
      accuracy_trends: [],
      correction_stats: {
        total_corrections: 0,
        avg_corrections_per_interaction: 0,
        correction_rate: 0,
      },
      user_satisfaction: {
        average: 0,
        trend: 'stable',
      },
      learning_progress: {
        total_interactions: 0,
        interactions_with_feedback: 0,
        learning_data_quality: 0,
        estimated_improvement: 0,
      },
    };
  },

  async healthCheck(): Promise<BackendHealthResponse> {
    const response = await api.get<BackendHealthResponse>('/api/health');
    return response.data;
  },
};

// Calendar API
export const calendarApi = {
  async getEvents() {
    const response = await api.get('/api/calendar/events');
    return response.data;
  },

  async createEvent(event: { title: string; time: string; duration?: string; description?: string }) {
    const response = await api.post('/api/calendar/events', event);
    return response.data;
  },
};

// Email API
export const emailApi = {
  async listEmails() {
    const response = await api.get('/api/email/list');
    return response.data;
  },

  async sendEmail(email: { to: string; subject: string; body: string }) {
    const response = await api.post('/api/email/send', email);
    return response.data;
  },

  async readEmail(emailId: string) {
    const response = await api.get(`/api/email/read/${emailId}`);
    return response.data;
  },
};

// Todo API
export const todoApi = {
  async listTodos() {
    const response = await api.get('/api/todo/list');
    return response.data;
  },

  async addTodo(todo: { title: string; description?: string; priority?: string }) {
    const response = await api.post('/api/todo/add', todo);
    return response.data;
  },

  async updateTodo(todoId: string, updates: any) {
    const response = await api.put(`/api/todo/update/${todoId}`, updates);
    return response.data;
  },

  async deleteTodo(todoId: string) {
    const response = await api.delete(`/api/todo/delete/${todoId}`);
    return response.data;
  },
};

export default api;
