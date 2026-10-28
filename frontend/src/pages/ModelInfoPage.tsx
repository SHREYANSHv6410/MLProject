import React, { useEffect, useState } from 'react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Database,
  ShieldCheck,
  Activity,
  BarChart,
  RefreshCw
} from 'lucide-react';
import { ModelMetadata } from '../types';
import { api } from '../services/api';
import { NeumorphicCard } from '../components/NeumorphicCard';

export const ModelInfoPage: React.FC = () => {
  const [metadata, setMetadata] = useState<ModelMetadata | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchModelInfo = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getModelInfo();
      setMetadata(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch model info');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModelInfo();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            Model Architecture & Evaluation
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Empirical validation metrics and documented system boundaries.
          </p>
        </div>

        <button
          onClick={fetchModelInfo}
          className="neu-button p-2.5 rounded-xl text-slate-600 dark:text-slate-300 hover:text-indigo-600"
          title="Refresh Metadata"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {isLoading && (
        <div className="py-16 text-center">
          <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs text-slate-500">Loading model telemetry...</p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl neu-inset border border-rose-500/30 text-rose-600 dark:text-rose-400 text-sm">
          Failed to load model details: {error}
        </div>
      )}

      {metadata && !isLoading && (
        <div className="space-y-6">
          {/* Main Architecture Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <NeumorphicCard variant="raised-sm" className="p-4">
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <Cpu className="w-4 h-4 text-indigo-500" />
                <span>Algorithm</span>
              </div>
              <div className="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">
                {metadata.algorithm}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Version: {metadata.model_name}
              </div>
            </NeumorphicCard>

            <NeumorphicCard variant="raised-sm" className="p-4">
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                <span>Calibration</span>
              </div>
              <div className="font-bold text-sm text-slate-800 dark:text-slate-100">
                {metadata.is_calibrated ? 'Calibrated via Platt Scaling' : 'Uncalibrated'}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Method: {metadata.calibration_method || 'sigmoid (3-fold)'}
              </div>
            </NeumorphicCard>

            <NeumorphicCard variant="raised-sm" className="p-4">
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-1">
                <Database className="w-4 h-4 text-amber-500" />
                <span>Benchmark Training Data</span>
              </div>
              <div className="font-bold text-sm text-slate-800 dark:text-slate-100">
                {metadata.sample_count} instances ({metadata.conversation_count} chats)
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Target Horizon: {metadata.target_horizon_hours}h
              </div>
            </NeumorphicCard>
          </div>

          {/* Genuine Held-out Test Evaluation Metrics */}
          <NeumorphicCard className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
              <div>
                <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
                  Held-Out Test Set Metrics
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Evaluated on conversation-grouped test splits with zero temporal leakage
                </p>
              </div>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/70 text-emerald-600 dark:text-emerald-400">
                Verified Benchmark
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-3.5 rounded-xl neu-inset text-center space-y-1">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  ROC-AUC
                </span>
                <div className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
                  {metadata.metrics.roc_auc !== undefined ? metadata.metrics.roc_auc.toFixed(3) : 'N/A'}
                </div>
                <span className="text-[10px] text-slate-400">Discrimination Ability</span>
              </div>

              <div className="p-3.5 rounded-xl neu-inset text-center space-y-1">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  PR-AUC
                </span>
                <div className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
                  {metadata.metrics.pr_auc !== undefined ? metadata.metrics.pr_auc.toFixed(3) : 'N/A'}
                </div>
                <span className="text-[10px] text-slate-400">Precision-Recall Curve</span>
              </div>

              <div className="p-3.5 rounded-xl neu-inset text-center space-y-1">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  F1 Score
                </span>
                <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">
                  {metadata.metrics.f1_score !== undefined ? metadata.metrics.f1_score.toFixed(3) : 'N/A'}
                </div>
                <span className="text-[10px] text-slate-400">Harmonic Mean</span>
              </div>

              <div className="p-3.5 rounded-xl neu-inset text-center space-y-1">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Brier Score
                </span>
                <div className="text-2xl font-extrabold text-amber-600 dark:text-amber-400">
                  {metadata.metrics.brier_score !== undefined ? metadata.metrics.brier_score.toFixed(3) : 'N/A'}
                </div>
                <span className="text-[10px] text-slate-400">Calibration Quality (Lower=Better)</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-2 text-center text-xs text-slate-600 dark:text-slate-300">
              <div className="neu-raised-sm p-2 rounded-xl">
                Accuracy: <span className="font-bold">{metadata.metrics.accuracy ? `${(metadata.metrics.accuracy * 100).toFixed(1)}%` : 'N/A'}</span>
              </div>
              <div className="neu-raised-sm p-2 rounded-xl">
                Precision: <span className="font-bold">{metadata.metrics.precision ? `${(metadata.metrics.precision * 100).toFixed(1)}%` : 'N/A'}</span>
              </div>
              <div className="neu-raised-sm p-2 rounded-xl">
                Recall: <span className="font-bold">{metadata.metrics.recall ? `${(metadata.metrics.recall * 100).toFixed(1)}%` : 'N/A'}</span>
              </div>
            </div>
          </NeumorphicCard>

          {/* Feature Engineering Schema */}
          <NeumorphicCard className="space-y-3">
            <h4 className="font-bold text-base text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-500" />
              <span>Features Extracted at Inference ({metadata.features_used.length} dimensions)</span>
            </h4>
            <div className="flex flex-wrap gap-2 pt-1">
              {metadata.features_used.map((feat) => (
                <span
                  key={feat}
                  className="px-2.5 py-1 rounded-lg neu-inset text-xs font-mono text-slate-600 dark:text-slate-300"
                >
                  {feat}
                </span>
              ))}
            </div>
          </NeumorphicCard>

          {/* Documented Limitations */}
          <NeumorphicCard className="space-y-3 border-l-4 border-amber-500">
            <h4 className="font-bold text-base text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span>Documented Limitations & Failure Modes</span>
            </h4>
            <ul className="list-disc pl-5 space-y-1.5 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {metadata.limitations.map((lim, idx) => (
                <li key={idx}>{lim}</li>
              ))}
            </ul>
          </NeumorphicCard>
        </div>
      )}
    </div>
  );
};
