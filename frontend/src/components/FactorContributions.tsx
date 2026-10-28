import React from 'react';
import { TrendingUp, TrendingDown, Minus, HelpCircle } from 'lucide-react';
import { FactorContribution } from '../types';
import { NeumorphicCard } from './NeumorphicCard';

interface FactorContributionsProps {
  factors: FactorContribution[];
}

export const FactorContributions: React.FC<FactorContributionsProps> = ({ factors }) => {
  return (
    <NeumorphicCard className="space-y-4">
      <div className="flex items-center justify-between border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
        <div>
          <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
            Influential Predictive Factors
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            How individual timing and conversational cues shifted the statistical probability
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {factors.map((factor, idx) => {
          const isPositive = factor.direction === 'increases_reply_probability';
          const isNegative = factor.direction === 'decreases_reply_probability';

          let impactBadge = 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400';
          if (factor.impact === 'high') {
            impactBadge = 'bg-indigo-100 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-300 border border-indigo-300/40';
          } else if (factor.impact === 'medium') {
            impactBadge = 'bg-blue-100 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 border border-blue-300/40';
          }

          return (
            <div
              key={idx}
              className="p-3.5 rounded-xl neu-raised-sm hover:scale-[1.005] transition-transform space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-800 dark:text-slate-100">
                    {factor.display_name}
                  </span>
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${impactBadge}`}>
                    {factor.impact} impact
                  </span>
                </div>

                <div className="flex items-center gap-1.5 font-bold text-xs">
                  {isPositive ? (
                    <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                      <TrendingUp className="w-3.5 h-3.5" />
                      <span>+{Math.round(factor.contribution * 100)}%</span>
                    </span>
                  ) : isNegative ? (
                    <span className="flex items-center gap-1 text-rose-600 dark:text-rose-400">
                      <TrendingDown className="w-3.5 h-3.5" />
                      <span>{Math.round(factor.contribution * 100)}%</span>
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-slate-400">
                      <Minus className="w-3.5 h-3.5" />
                      <span>Neutral</span>
                    </span>
                  )}
                </div>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                {factor.description}
              </p>
            </div>
          );
        })}
      </div>
    </NeumorphicCard>
  );
};
