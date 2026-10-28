import React from 'react';
import {
  Download,
  RotateCcw,
  BarChart3,
  MessageSquare,
  ShieldAlert,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { PredictionResult, ConversationStats } from '../types';
import { ProbabilityGauge } from '../components/ProbabilityGauge';
import { FactorContributions } from '../components/FactorContributions';
import { NeumorphicCard } from '../components/NeumorphicCard';

interface ResultsPageProps {
  result: PredictionResult;
  stats: ConversationStats | null;
  onNavigateToTab: (tab: any) => void;
  onSelectAnotherMessage: () => void;
  onUploadAnother: () => void;
}

export const ResultsPage: React.FC<ResultsPageProps> = ({
  result,
  stats,
  onNavigateToTab,
  onSelectAnotherMessage,
  onUploadAnother
}) => {
  const exportAsJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `replysense_prediction_${result.target_message.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const exportAsCSV = () => {
    const rows = [
      ['Metric', 'Value'],
      ['Outcome', result.outcome],
      ['Calibrated Probability', result.probability.toString()],
      ['Uncertainty Level', result.uncertainty_level],
      ['Reply Horizon Hours', result.reply_horizon_hours.toString()],
      ['Target Message Sender', result.target_message.sender],
      ['Target Message Timestamp', result.target_message.timestamp],
      ['Target Message Text', `"${result.target_message.text.replace(/"/g, '""')}"`],
      ['Algorithm', result.algorithm],
      ['Model Version', result.model_version],
    ];

    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((e) => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `replysense_prediction_${result.target_message.id}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header & Export Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Analysis Complete</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            Reply Likelihood Assessment
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportAsJSON}
            className="neu-button px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-indigo-600 flex items-center gap-1.5"
            title="Export Prediction JSON"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={exportAsCSV}
            className="neu-button px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-indigo-600 flex items-center gap-1.5"
            title="Export Prediction CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Target Message Focus Card */}
      <NeumorphicCard variant="inset" className="p-4 sm:p-5 border border-indigo-500/20 space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700 dark:text-slate-300">
              Evaluated Message:
            </span>
            <span className="font-semibold text-indigo-600 dark:text-indigo-400">
              {result.target_message.sender}
            </span>
          </div>
          <span>{new Date(result.target_message.timestamp).toLocaleString()}</span>
        </div>

        <p className="text-base font-semibold text-slate-800 dark:text-slate-100 italic">
          "{result.target_message.text}"
        </p>
      </NeumorphicCard>

      {/* Main Dual Grid: Gauge on Left, Factors on Right */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div className="md:col-span-5">
          <ProbabilityGauge
            probability={result.probability}
            outcome={result.outcome}
            uncertaintyLevel={result.uncertainty_level}
            confidenceInterval={result.confidence_interval}
            horizonHours={result.reply_horizon_hours}
            calibrated={result.calibrated}
          />
        </div>

        <div className="md:col-span-7">
          <FactorContributions factors={result.key_factors} />
        </div>
      </div>

      {/* Summary Verdict Callout */}
      <NeumorphicCard variant="raised-sm" className="space-y-2 border-l-4 border-indigo-500 p-5">
        <h4 className="font-bold text-sm text-slate-800 dark:text-slate-100">
          Analytical Verdict
        </h4>
        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          {result.summary_verdict}
        </p>
      </NeumorphicCard>

      {/* Action Footer Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200/50 dark:border-slate-800/50">
        <div className="flex items-center gap-3">
          <button
            onClick={onSelectAnotherMessage}
            className="neu-button px-4 py-2.5 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 hover:text-indigo-600 flex items-center gap-2"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Select Another Message</span>
          </button>

          <button
            onClick={onUploadAnother}
            className="neu-button px-4 py-2.5 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 hover:text-indigo-600 flex items-center gap-2"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Upload New Chat</span>
          </button>
        </div>

        <button
          onClick={() => onNavigateToTab('insights')}
          className="neu-button px-5 py-2.5 rounded-xl text-xs font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-2"
        >
          <BarChart3 className="w-4 h-4" />
          <span>Explore Conversation Insights</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Disclaimers & Ethics */}
      <div className="p-4 rounded-xl neu-inset text-xs text-slate-500 dark:text-slate-400 space-y-1">
        <div className="flex items-center gap-1.5 font-bold text-slate-600 dark:text-slate-300">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />
          <span>Probabilistic System Notice</span>
        </div>
        <p className="leading-relaxed">
          {result.disclaimer}
        </p>
      </div>
    </div>
  );
};
