import {
  ChatPreviewResponse,
  PredictionResult,
  ConversationStats,
  ModelMetadata,
  HistoryListResponse,
  ChatMessage
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const api = {
  async getHealth(): Promise<{ status: string; app: string; model_loaded: boolean }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async getModelInfo(): Promise<ModelMetadata> {
    const res = await fetch(`${API_BASE}/model/info`);
    if (!res.ok) throw new Error(`Failed to load model metadata: ${res.statusText}`);
    return res.json();
  },

  async previewChat(file: File): Promise<ChatPreviewResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/chat/preview`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to parse chat export.');
    }
    return res.json();
  },

  async predictReply(params: {
    messages: ChatMessage[];
    sender: string;
    recipient: string;
    target_message_id?: string;
    reply_horizon_hours: number;
  }): Promise<PredictionResult> {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Prediction request failed.');
    }
    return res.json();
  },

  async analyzeChat(params: {
    messages: ChatMessage[];
    sender: string;
    recipient: string;
    reply_horizon_hours: number;
  }): Promise<ConversationStats> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Analysis request failed.');
    }
    return res.json();
  },

  async getHistory(): Promise<HistoryListResponse> {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) throw new Error('Failed to retrieve history');
    return res.json();
  },

  async clearHistory(): Promise<void> {
    const res = await fetch(`${API_BASE}/history`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to clear history');
  }
};
