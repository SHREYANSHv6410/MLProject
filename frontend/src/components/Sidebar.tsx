import React from 'react';
import {
  LayoutDashboard,
  UploadCloud,
  Sparkles,
  BarChart3,
  Cpu,
  History,
  Settings
} from 'lucide-react';

export type NavTab = 'overview' | 'analyze' | 'results' | 'insights' | 'model' | 'history' | 'settings';

interface SidebarProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  hasActiveConversation: boolean;
  hasPrediction: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  hasActiveConversation,
  hasPrediction
}) => {
  const navItems = [
    { id: 'overview' as NavTab, label: 'Overview', icon: LayoutDashboard },
    { id: 'analyze' as NavTab, label: 'Analyze Chat', icon: UploadCloud, badge: hasActiveConversation ? 'Active' : undefined },
    { id: 'results' as NavTab, label: 'Prediction', icon: Sparkles, disabled: !hasPrediction },
    { id: 'insights' as NavTab, label: 'Insights & Charts', icon: BarChart3, disabled: !hasActiveConversation },
    { id: 'model' as NavTab, label: 'Model Info & Metrics', icon: Cpu },
    { id: 'history' as NavTab, label: 'Prediction History', icon: History },
    { id: 'settings' as NavTab, label: 'Settings & Privacy', icon: Settings },
  ];

  return (
    <aside className="w-full md:w-64 p-4 flex md:flex-col gap-2 shrink-0 overflow-x-auto md:overflow-x-visible">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        const isDisabled = item.disabled;

        return (
          <button
            key={item.id}
            onClick={() => !isDisabled && setActiveTab(item.id)}
            disabled={isDisabled}
            className={`flex items-center justify-between px-4 py-3 rounded-xl text-sm font-semibold transition-all whitespace-nowrap md:whitespace-normal ${
              isActive
                ? 'neu-inset text-indigo-600 dark:text-indigo-400 font-bold'
                : isDisabled
                ? 'opacity-40 cursor-not-allowed text-slate-400 dark:text-slate-600'
                : 'neu-button text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400'
            }`}
          >
            <div className="flex items-center gap-3">
              <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600 dark:text-indigo-400' : ''}`} />
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/70 text-emerald-600 dark:text-emerald-400 border border-emerald-300/40">
                {item.badge}
              </span>
            )}
          </button>
        );
      })}
    </aside>
  );
};
