import React from 'react';
import { BarChart3, AlertCircle, UploadCloud } from 'lucide-react';
import { ConversationStats } from '../types';
import { InsightsCharts } from '../components/InsightsCharts';
import { NeumorphicCard } from '../components/NeumorphicCard';

interface InsightsPageProps {
  stats: ConversationStats | null;
  sender: string;
  recipient: string;
  onNavigateToTab: (tab: any) => void;
}

export const InsightsPage: React.FC<InsightsPageProps> = ({
  stats,
  sender,
  recipient,
  onNavigateToTab
}) => {
  if (!stats) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <div className="w-16 h-16 rounded-2xl neu-inset flex items-center justify-center mx-auto text-slate-400">
          <BarChart3 className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">
          No Active Conversation Loaded
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Upload a chat export or load our sample conversation to inspect temporal histograms, response time distributions, and reply trends.
        </p>
        <button
          onClick={() => onNavigateToTab('analyze')}
          className="neu-button px-5 py-2.5 rounded-xl text-xs font-bold text-indigo-600 dark:text-indigo-400 inline-flex items-center gap-2"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Go to Chat Ingestion</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
          Conversation Dynamics & Insights
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Empirical patterns observed between {sender} and {recipient} across all parsed turns.
        </p>
      </div>

      <InsightsCharts stats={stats} sender={sender} recipient={recipient} />
    </div>
  );
};
