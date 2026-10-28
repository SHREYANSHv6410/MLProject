import React, { useState } from 'react';
import { Settings, ShieldCheck, Database, HardDrive, KeyRound } from 'lucide-react';
import { NeumorphicCard } from '../components/NeumorphicCard';

export const SettingsPage: React.FC = () => {
  const [saveHistory, setSaveHistory] = useState<boolean>(() => {
    return localStorage.getItem('replysense_save_history') !== 'false';
  });

  const [defaultHorizon, setDefaultHorizon] = useState<number>(() => {
    return Number(localStorage.getItem('replysense_default_horizon') || '24');
  });

  const handleToggleHistory = (val: boolean) => {
    setSaveHistory(val);
    localStorage.setItem('replysense_save_history', val ? 'true' : 'false');
  };

  const handleChangeHorizon = (val: number) => {
    setDefaultHorizon(val);
    localStorage.setItem('replysense_default_horizon', val.toString());
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
          Preferences & Privacy Controls
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Configure local prediction persistence and data management boundaries.
        </p>
      </div>

      <div className="space-y-6">
        {/* Persistence Preferences */}
        <NeumorphicCard className="space-y-4">
          <h4 className="font-bold text-base text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-indigo-500" />
            <span>Local Persistence</span>
          </h4>

          <div className="flex items-center justify-between p-4 rounded-xl neu-inset">
            <div>
              <div className="font-bold text-sm text-slate-800 dark:text-slate-100">
                Log Predictions to Local SQLite Database
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md">
                Stores your message evaluation history locally on your machine. You can purge this at any time from the History tab.
              </p>
            </div>

            <button
              onClick={() => handleToggleHistory(!saveHistory)}
              className={`w-12 h-6 rounded-full p-1 transition-colors neu-inset ${
                saveHistory ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-700'
              }`}
            >
              <div
                className={`w-4 h-4 rounded-full bg-white transition-transform ${
                  saveHistory ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Default Reply Horizon */}
          <div className="p-4 rounded-xl neu-inset space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-slate-800 dark:text-slate-100">
                Default Reply Time Horizon
              </span>
              <span className="font-extrabold text-sm text-indigo-600 dark:text-indigo-400">
                {defaultHorizon} Hours
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              The baseline duration window used when evaluating unanswered messages.
            </p>
            <input
              type="range"
              min="2"
              max="72"
              step="2"
              value={defaultHorizon}
              onChange={(e) => handleChangeHorizon(Number(e.target.value))}
              className="w-full h-2 rounded-lg accent-indigo-600 cursor-pointer"
            />
          </div>
        </NeumorphicCard>

        {/* Privacy Framework */}
        <NeumorphicCard className="space-y-3 border-l-4 border-emerald-500">
          <h4 className="font-bold text-base text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <span>Zero Third-Party Data Transmission</span>
          </h4>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Chat exports contain sensitive personal and interpersonal dialogue. ReplySense does not transmit message text, usernames, or metadata to external cloud servers, third-party analytics vendors, or commercial LLM APIs. All feature extraction, tokenization, and model inference run exclusively on this machine.
          </p>
        </NeumorphicCard>
      </div>
    </div>
  );
};
