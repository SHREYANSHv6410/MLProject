import React from 'react';
import {
  Users,
  Calendar,
  FileCheck2,
  Clock,
  AlertTriangle,
  Send,
  Sparkles,
  ArrowRight,
  RotateCcw
} from 'lucide-react';
import { ChatPreviewResponse, ChatMessage } from '../types';
import { NeumorphicCard } from './NeumorphicCard';

interface ConversationPreviewProps {
  preview: ChatPreviewResponse;
  selectedSender: string;
  setSelectedSender: (sender: string) => void;
  selectedRecipient: string;
  setSelectedRecipient: (recipient: string) => void;
  targetMessageId: string;
  setTargetMessageId: (id: string) => void;
  replyHorizonHours: number;
  setReplyHorizonHours: (hours: number) => void;
  onRunPrediction: () => void;
  onReset: () => void;
  isPredicting: boolean;
}

export const ConversationPreview: React.FC<ConversationPreviewProps> = ({
  preview,
  selectedSender,
  setSelectedSender,
  selectedRecipient,
  setSelectedRecipient,
  targetMessageId,
  setTargetMessageId,
  replyHorizonHours,
  setReplyHorizonHours,
  onRunPrediction,
  onReset,
  isPredicting
}) => {
  const formatDate = (isoString?: string) => {
    if (!isoString) return 'N/A';
    try {
      return new Date(isoString).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return isoString;
    }
  };

  const formatTime = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Metadata Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
            <FileCheck2 className="w-4 h-4 text-indigo-500" />
            <span>Format Detected</span>
          </div>
          <div className="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">
            {preview.detected_format}
          </div>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
            <Users className="w-4 h-4 text-emerald-500" />
            <span>Participants</span>
          </div>
          <div className="font-bold text-sm text-slate-800 dark:text-slate-100">
            {preview.participants.length} detected
          </div>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
            <Calendar className="w-4 h-4 text-amber-500" />
            <span>Date Span</span>
          </div>
          <div className="font-bold text-xs text-slate-800 dark:text-slate-100 truncate">
            {formatDate(preview.date_start)} – {formatDate(preview.date_end)}
          </div>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
            <Clock className="w-4 h-4 text-blue-500" />
            <span>Total Messages</span>
          </div>
          <div className="font-bold text-sm text-slate-800 dark:text-slate-100">
            {preview.total_messages.toLocaleString()}
          </div>
        </NeumorphicCard>
      </div>

      {/* Parsing Warnings */}
      {preview.warnings && preview.warnings.length > 0 && (
        <div className="p-4 rounded-xl neu-inset border border-amber-500/30 flex items-start gap-3 text-amber-700 dark:text-amber-400 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Parsing Notes:</span>
            <ul className="list-disc pl-4 space-y-0.5">
              {preview.warnings.slice(0, 3).map((w, idx) => (
                <li key={idx}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Role Configuration */}
      <NeumorphicCard className="space-y-5">
        <h4 className="font-bold text-base text-slate-800 dark:text-slate-100 flex items-center justify-between">
          <span>Configure Prediction Parameters</span>
          <button
            type="button"
            onClick={onReset}
            className="neu-button px-3 py-1 rounded-xl text-xs font-semibold text-slate-500 hover:text-rose-500 flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Change File</span>
          </button>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Sender Selector */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
              Sender (Message Author)
            </label>
            <select
              value={selectedSender}
              onChange={(e) => setSelectedSender(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl neu-inset bg-transparent font-medium text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              {preview.participants.map((p) => (
                <option key={p} value={p} className="bg-white dark:bg-slate-900">
                  {p} ({preview.participant_counts[p] || 0} msgs)
                </option>
              ))}
            </select>
          </div>

          {/* Recipient Selector */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
              Expected Recipient
            </label>
            <select
              value={selectedRecipient}
              onChange={(e) => setSelectedRecipient(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl neu-inset bg-transparent font-medium text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              {preview.participants
                .filter((p) => p !== selectedSender)
                .map((p) => (
                  <option key={p} value={p} className="bg-white dark:bg-slate-900">
                    {p} ({preview.participant_counts[p] || 0} msgs)
                  </option>
                ))}
            </select>
          </div>

          {/* Time Horizon */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Reply Horizon
              </label>
              <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                {replyHorizonHours} hours
              </span>
            </div>
            <input
              type="range"
              min="2"
              max="72"
              step="2"
              value={replyHorizonHours}
              onChange={(e) => setReplyHorizonHours(Number(e.target.value))}
              className="w-full h-2 rounded-lg neu-inset accent-indigo-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>2h (Immediate)</span>
              <span>24h (Standard)</span>
              <span>72h (Multi-day)</span>
            </div>
          </div>
        </div>

        {/* Message Selector */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
            Target Message To Evaluate
          </label>
          <select
            value={targetMessageId}
            onChange={(e) => setTargetMessageId(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl neu-inset bg-transparent font-medium text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 truncate"
          >
            {preview.candidate_target_messages
              .filter((m) => m.sender === selectedSender)
              .map((m) => (
                <option key={m.id} value={m.id} className="bg-white dark:bg-slate-900">
                  [{formatTime(m.timestamp)}] {m.text.slice(0, 80)}
                  {m.text.length > 80 ? '...' : ''}
                </option>
              ))}
          </select>
        </div>
      </NeumorphicCard>

      {/* Conversation Preview Timeline */}
      <NeumorphicCard className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
          <span className="font-bold text-sm text-slate-700 dark:text-slate-200">
            Recent Conversation Turns
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">
            Click any message by {selectedSender} to evaluate it
          </span>
        </div>

        <div className="max-h-80 overflow-y-auto pr-2 space-y-3">
          {preview.preview_messages.slice(-25).map((m) => {
            const isSender = m.sender === selectedSender;
            const isTarget = m.id === targetMessageId;

            return (
              <div
                key={m.id}
                onClick={() => isSender && setTargetMessageId(m.id)}
                className={`flex flex-col ${isSender ? 'items-end' : 'items-start'} ${
                  isSender ? 'cursor-pointer' : ''
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1 px-1 text-[11px] text-slate-400">
                  <span className="font-semibold">{m.sender}</span>
                  <span>•</span>
                  <span>{formatTime(m.timestamp)}</span>
                  {isTarget && (
                    <span className="ml-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-600 text-white">
                      TARGET
                    </span>
                  )}
                </div>

                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm transition-all ${
                    isTarget
                      ? 'neu-inset ring-2 ring-indigo-500 text-indigo-900 dark:text-indigo-200 font-medium'
                      : isSender
                      ? 'neu-raised bg-indigo-50/50 dark:bg-indigo-950/30 text-slate-800 dark:text-slate-100 hover:ring-1 hover:ring-indigo-300'
                      : 'neu-raised-sm text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {m.text}
                </div>
              </div>
            );
          })}
        </div>
      </NeumorphicCard>

      {/* Run Action Bar */}
      <div className="flex justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onRunPrediction}
          disabled={isPredicting || !targetMessageId}
          className="neu-button px-8 py-3.5 rounded-2xl font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 flex items-center gap-3 shadow-lg shadow-indigo-500/25 disabled:opacity-50"
        >
          {isPredicting ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Evaluating Features...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5 text-amber-300" />
              <span>Generate Prediction</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
