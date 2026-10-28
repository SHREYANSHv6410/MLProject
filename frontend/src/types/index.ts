export interface ChatMessage {
  id: string;
  timestamp: string;
  sender: string;
  text: string;
  is_media?: boolean;
  is_system?: boolean;
  raw?: string;
}

export interface ChatPreviewResponse {
  filename: string;
  detected_format: string;
  participants: string[];
  participant_counts: Record<string, number>;
  total_messages: number;
  date_start?: string;
  date_end?: string;
  warnings: string[];
  preview_messages: ChatMessage[];
  candidate_target_messages: ChatMessage[];
  default_sender?: string;
  default_recipient?: string;
  default_target_message_id?: string;
}

export interface FactorContribution {
  feature: string;
  display_name: string;
  value: any;
  contribution: number;
  direction: 'increases_reply_probability' | 'decreases_reply_probability' | 'neutral';
  impact: 'high' | 'medium' | 'low' | 'negligible';
  description: string;
}

export interface PredictionResult {
  outcome: 'Reply likely' | 'Reply less likely';
  probability: number;
  calibrated: boolean;
  uncertainty_level: 'Low' | 'Moderate' | 'Elevated';
  confidence_interval?: {
    lower: number;
    upper: number;
  };
  decision_threshold: number;
  target_message: ChatMessage;
  reply_horizon_hours: number;
  model_version: string;
  algorithm: string;
  key_factors: FactorContribution[];
  summary_verdict: string;
  disclaimer: string;
}

export interface HourlyActivity {
  hour: number;
  sender_count: number;
  recipient_count: number;
  total_count: number;
}

export interface DayOfWeekActivity {
  day: string;
  day_index: number;
  count: number;
}

export interface ResponseTimeBucket {
  bucket: string;
  count: number;
  percentage: number;
}

export interface ConversationStats {
  total_messages: number;
  sender_messages: number;
  recipient_messages: number;
  sender_ratio: number;
  recipient_ratio: number;
  historical_reply_rate?: number;
  avg_response_time_minutes?: number;
  median_response_time_minutes?: number;
  min_response_time_minutes?: number;
  max_response_time_minutes?: number;
  conversation_duration_days: number;
  avg_sender_words: number;
  avg_recipient_words: number;
  sender_question_count: number;
  recipient_question_count: number;
  sender_emoji_count: number;
  recipient_emoji_count: number;
  activity_by_hour: HourlyActivity[];
  activity_by_day: DayOfWeekActivity[];
  response_time_distribution: ResponseTimeBucket[];
  turn_taking_ratio: number;
  initiated_conversations_sender: number;
  initiated_conversations_recipient: number;
}

export interface ModelMetadata {
  model_name: string;
  algorithm: string;
  trained_at: string;
  dataset_info: string;
  sample_count: number;
  conversation_count: number;
  target_horizon_hours: number;
  is_calibrated: boolean;
  calibration_method?: string;
  features_used: string[];
  metrics: Record<string, number>;
  limitations: string[];
  status: 'ready' | 'untrained' | 'degraded';
}

export interface HistoryRecord {
  id: string;
  created_at: string;
  filename: string;
  sender: string;
  recipient: string;
  target_message_text: string;
  target_message_time: string;
  predicted_outcome: string;
  probability: number;
  uncertainty_level: string;
  key_factors_summary: string[];
  reply_horizon_hours: number;
}

export interface HistoryListResponse {
  enabled: boolean;
  total_count: number;
  items: HistoryRecord[];
}
