import React, { useEffect, useState } from 'react';
import { History, Trash2, CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';
import { HistoryRecord } from '../types';
import { api } from '../services/api';
import { NeumorphicCard } from '../components/NeumorphicCard';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isClearing, setIsClearing] = useState<boolean>(false);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const res = await api.getHistory();
      setHistory(res.items);
    } catch {
      setHistory([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to permanently delete all prediction history?')) {
      return;
    }
    setIsClearing(true);
    try {
      await api.clearHistory();
      setHistory([]);
    } catch (err) {
      alert('Failed to clear history');
    } finally {
      setIsClearing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            Prediction History
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Local session logs stored privately in SQLite on your device.
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={handleClearHistory}
            disabled={isClearing}
            className="neu-button px-4 py-2 rounded-xl text-xs font-bold text-rose-600 dark:text-rose-400 hover:text-rose-700 flex items-center gap-1.5"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="py-16 text-center">
          <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs text-slate-500">Retrieving prediction log...</p>
        </div>
      ) : history.length === 0 ? (
        <NeumorphicCard className="py-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-xl neu-inset flex items-center justify-center mx-auto text-slate-400">
            <History className="w-6 h-6" />
          </div>
          <h4 className="font-bold text-base text-slate-700 dark:text-slate-300">
            No Saved Predictions
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            When you evaluate messages with history enabled in settings, past inferences and probabilities will appear here.
          </p>
        </NeumorphicCard>
      ) : (
        <div className="space-y-3">
          {history.map((record) => {
            const isLikely = record.predicted_outcome === 'Reply likely';
            const pct = Math.round(record.probability * 100);

            return (
              <NeumorphicCard key={record.id} variant="raised-sm" className="p-4 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-700 dark:text-slate-200">
                      {record.sender} → {record.recipient}
                    </span>
                    <span>•</span>
                    <span className="truncate max-w-[150px]">{record.filename}</span>
                  </div>

                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(record.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between gap-4">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-100 italic truncate max-w-lg">
                    "{record.target_message_text}"
                  </p>

                  <div className="flex items-center gap-2 shrink-0">
                    <div className="text-right">
                      <div className="font-extrabold text-sm text-slate-800 dark:text-slate-100">
                        {pct}%
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {record.reply_horizon_hours}h horizon
                      </div>
                    </div>

                    <div
                      className={`p-2 rounded-xl neu-inset ${
                        isLikely
                          ? 'text-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/40'
                          : 'text-rose-500 bg-rose-50/50 dark:bg-rose-950/40'
                      }`}
                    >
                      {isLikely ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                    </div>
                  </div>
                </div>
              </NeumorphicCard>
            );
          })}
        </div>
      )}
    </div>
  );
};
