import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, Info } from 'lucide-react';
import { NeumorphicCard } from './NeumorphicCard';

interface ProbabilityGaugeProps {
  probability: number;
  outcome: 'Reply likely' | 'Reply less likely';
  uncertaintyLevel: 'Low' | 'Moderate' | 'Elevated';
  confidenceInterval?: { lower: number; upper: number };
  horizonHours: number;
  calibrated: boolean;
}

export const ProbabilityGauge: React.FC<ProbabilityGaugeProps> = ({
  probability,
  outcome,
  uncertaintyLevel,
  confidenceInterval,
  horizonHours,
  calibrated
}) => {
  const percentage = Math.round(probability * 100);
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (probability * circumference);

  const isLikely = outcome === 'Reply likely';

  let uncertaintyColor = 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-800';
  if (uncertaintyLevel === 'Moderate') {
    uncertaintyColor = 'text-amber-500 bg-amber-50 dark:bg-amber-950/60 border-amber-300 dark:border-amber-800';
  } else if (uncertaintyLevel === 'Elevated') {
    uncertaintyColor = 'text-rose-500 bg-rose-50 dark:bg-rose-950/60 border-rose-300 dark:border-rose-800';
  }

  return (
    <NeumorphicCard className="flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
      {/* Background radial accent */}
      <div
        className={`absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none ${
          isLikely ? 'bg-emerald-500' : 'bg-rose-500'
        }`}
      />

      {/* Outcome Banner */}
      <div className="flex items-center gap-2 mb-6">
        {isLikely ? (
          <div className="flex items-center gap-2 px-4 py-1.5 rounded-full neu-raised text-emerald-600 dark:text-emerald-400 font-extrabold text-sm tracking-wide">
            <CheckCircle2 className="w-4 h-4" />
            <span>REPLY LIKELY</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-4 py-1.5 rounded-full neu-raised text-rose-600 dark:text-rose-400 font-extrabold text-sm tracking-wide">
            <XCircle className="w-4 h-4" />
            <span>REPLY LESS LIKELY</span>
          </div>
        )}

        <div className={`px-3 py-1 rounded-full text-xs font-bold border ${uncertaintyColor}`}>
          Uncertainty: {uncertaintyLevel}
        </div>
      </div>

      {/* SVG Radial Meter */}
      <div className="relative w-52 h-52 flex items-center justify-center mb-6">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
          {/* Track */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            className="text-slate-200 dark:text-slate-800"
            strokeWidth="14"
            stroke="currentColor"
            fill="transparent"
          />
          {/* Progress Indicator */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke={isLikely ? '#0d9488' : '#e11d48'}
            strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Readout */}
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold tracking-tight text-slate-800 dark:text-slate-100">
            {percentage}%
          </span>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mt-1">
            Likelihood
          </span>
          {calibrated && (
            <span className="text-[9px] font-bold text-indigo-500 uppercase tracking-widest mt-0.5">
              Calibrated
            </span>
          )}
        </div>
      </div>

      {/* Confidence Bounds */}
      {confidenceInterval && (
        <div className="neu-inset px-4 py-2 rounded-xl text-xs text-slate-600 dark:text-slate-300 mb-4 flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
          <span>
            90% Confidence Interval: [{Math.round(confidenceInterval.lower * 100)}% – {Math.round(confidenceInterval.upper * 100)}%]
          </span>
        </div>
      )}

      {/* Explanation Legend */}
      <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm leading-relaxed">
        Estimated posterior probability that the recipient will send a reply message within{' '}
        <span className="font-semibold text-slate-700 dark:text-slate-200">{horizonHours} hours</span>{' '}
        of your message.
      </p>
    </NeumorphicCard>
  );
};
