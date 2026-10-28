import React from 'react';
import { ChatPreviewResponse } from '../types';
import { UploadZone } from '../components/UploadZone';
import { ConversationPreview } from '../components/ConversationPreview';

interface AnalyzePageProps {
  preview: ChatPreviewResponse | null;
  onFileSelected: (file: File) => void;
  onLoadDemo: () => void;
  onReset: () => void;
  selectedSender: string;
  setSelectedSender: (sender: string) => void;
  selectedRecipient: string;
  setSelectedRecipient: (recipient: string) => void;
  targetMessageId: string;
  setTargetMessageId: (id: string) => void;
  replyHorizonHours: number;
  setReplyHorizonHours: (hours: number) => void;
  onRunPrediction: () => void;
  isLoading: boolean;
  isPredicting: boolean;
  error?: string | null;
}

export const AnalyzePage: React.FC<AnalyzePageProps> = ({
  preview,
  onFileSelected,
  onLoadDemo,
  onReset,
  selectedSender,
  setSelectedSender,
  selectedRecipient,
  setSelectedRecipient,
  targetMessageId,
  setTargetMessageId,
  replyHorizonHours,
  setReplyHorizonHours,
  onRunPrediction,
  isLoading,
  isPredicting,
  error
}) => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
          Analyze Chat Conversation
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Upload and configure your chat export to evaluate response patterns.
        </p>
      </div>

      {!preview ? (
        <UploadZone
          onFileSelected={onFileSelected}
          onLoadDemo={onLoadDemo}
          isLoading={isLoading}
          error={error}
        />
      ) : (
        <ConversationPreview
          preview={preview}
          selectedSender={selectedSender}
          setSelectedSender={setSelectedSender}
          selectedRecipient={selectedRecipient}
          setSelectedRecipient={setSelectedRecipient}
          targetMessageId={targetMessageId}
          setTargetMessageId={setTargetMessageId}
          replyHorizonHours={replyHorizonHours}
          setReplyHorizonHours={setReplyHorizonHours}
          onRunPrediction={onRunPrediction}
          onReset={onReset}
          isPredicting={isPredicting}
        />
      )}
    </div>
  );
};
