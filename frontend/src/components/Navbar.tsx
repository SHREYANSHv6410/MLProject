import React from 'react';
import { MessageSquareText, ShieldCheck, Activity } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface NavbarProps {
  serverStatus: 'online' | 'offline' | 'checking';
  modelReady: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ serverStatus, modelReady }) => {
  return (
    <header className="sticky top-0 z-40 w-full px-6 py-4 backdrop-blur-md bg-neu-bg-light/80 dark:bg-neu-bg-dark/80 border-b border-slate-200/40 dark:border-slate-800/40 transition-colors">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <MessageSquareText className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                ReplySense
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200/50 dark:border-indigo-800/50">
                PRO
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
              Understand the patterns behind every unanswered message.
            </p>
          </div>
        </div>

        {/* Status Indicators & Controls */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl neu-inset text-xs text-slate-600 dark:text-slate-300">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>100% Local & Private</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl neu-inset text-xs font-medium">
            <span
              className={`w-2 h-2 rounded-full ${
                serverStatus === 'online'
                  ? modelReady
                    ? 'bg-emerald-500 animate-pulse'
                    : 'bg-amber-500'
                  : serverStatus === 'offline'
                  ? 'bg-rose-500'
                  : 'bg-slate-400 animate-ping'
              }`}
            />
            <span className="text-slate-600 dark:text-slate-300">
              {serverStatus === 'online'
                ? modelReady
                  ? 'Model Ready'
                  : 'API Online (Model Standby)'
                : serverStatus === 'offline'
                ? 'Backend Offline'
                : 'Connecting...'}
            </span>
          </div>

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};
