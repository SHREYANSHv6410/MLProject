import React from 'react';
import {
  MessageSquareText,
  UploadCloud,
  Sparkles,
  ShieldCheck,
  BrainCircuit,
  ArrowRight,
  TrendingUp,
  Clock,
  History as HistoryIcon
} from 'lucide-react';
import { NeumorphicCard } from '../components/NeumorphicCard';
import { UploadZone } from '../components/UploadZone';

interface OverviewPageProps {
  onFileSelected: (file: File) => void;
  onLoadDemo: () => void;
  onNavigateToTab: (tab: any) => void;
  isLoading: boolean;
  modelReady: boolean;
  historyCount: number;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  onFileSelected,
  onLoadDemo,
  onNavigateToTab,
  isLoading,
  modelReady,
  historyCount
}) => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Hero Section */}
      <NeumorphicCard className="relative overflow-hidden p-8 sm:p-10 border border-indigo-500/10">
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full neu-inset text-xs font-bold text-indigo-600 dark:text-indigo-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Probabilistic Dialogue Analytics</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-800 dark:text-slate-100 leading-tight">
            Understand the patterns behind every unanswered message.
          </h1>

          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
            ReplySense parses your conversation history, analyzes linguistic and turn-taking signals, and calculates calibrated reply probabilities with transparent factor explanations.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={() => onNavigateToTab('analyze')}
              className="neu-button px-6 py-3 rounded-2xl font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 flex items-center gap-2 shadow-lg shadow-indigo-500/25"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Upload Chat Export</span>
            </button>

            <button
              onClick={onLoadDemo}
              disabled={isLoading}
              className="neu-button px-5 py-3 rounded-2xl font-bold text-slate-700 dark:text-slate-200 hover:text-indigo-600 flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>Try with Sample Chat</span>
            </button>
          </div>
        </div>

        {/* Decorative background element */}
        <div className="hidden lg:block absolute -right-12 -bottom-12 w-64 h-64 rounded-full bg-gradient-to-tr from-indigo-500/10 to-violet-500/20 blur-2xl pointer-events-none" />
      </NeumorphicCard>

      {/* Upload Drop Zone in Overview */}
      <div className="space-y-2">
        <h3 className="font-bold text-base text-slate-800 dark:text-slate-200 px-1">
          Quick Ingestion
        </h3>
        <UploadZone
          onFileSelected={onFileSelected}
          onLoadDemo={onLoadDemo}
          isLoading={isLoading}
        />
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <NeumorphicCard variant="raised-sm" className="space-y-3">
          <div className="w-10 h-10 rounded-xl neu-inset flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
            Leak-Free ML Pipeline
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Strict chronological temporal boundaries ensure historical reply rates and active hour distributions never peek at future dialogue.
          </p>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="space-y-3">
          <div className="w-10 h-10 rounded-xl neu-inset flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <TrendingUp className="w-5 h-5" />
          </div>
          <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
            Calibrated Probabilities
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Outputs true empirical posterior probabilities calibrated via Platt scaling (sigmoid CV) rather than arbitrary heuristic scores.
          </p>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="space-y-3">
          <div className="w-10 h-10 rounded-xl neu-inset flex items-center justify-center text-blue-600 dark:text-blue-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
            100% Privacy by Design
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            All chat parsing and feature transformations execute locally in ephemeral memory without transmitting private conversations to third parties.
          </p>
        </NeumorphicCard>
      </div>
    </div>
  );
};
