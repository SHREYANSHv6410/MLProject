import React from 'react';

interface NeumorphicCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'raised' | 'raised-sm' | 'inset' | 'flat';
  className?: string;
  children: React.ReactNode;
}

export const NeumorphicCard: React.FC<NeumorphicCardProps> = ({
  variant = 'raised',
  className = '',
  children,
  ...props
}) => {
  let shadowClass = 'neu-raised';
  if (variant === 'raised-sm') shadowClass = 'neu-raised-sm';
  else if (variant === 'inset') shadowClass = 'neu-inset';
  else if (variant === 'flat') shadowClass = 'bg-neu-surface-light dark:bg-neu-surface-dark border border-slate-200/50 dark:border-slate-800/50';

  return (
    <div
      className={`rounded-2xl p-6 transition-all duration-200 ${shadowClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
