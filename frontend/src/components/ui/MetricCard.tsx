import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  value: string | number;
  label: string;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  unit?: string;
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
}

const variantStyles = {
  default: 'text-slate-800 dark:text-slate-100',
  primary: 'text-primary-600 dark:text-primary-400',
  success: 'text-success-600 dark:text-success-400',
  warning: 'text-warning-600 dark:text-warning-400',
  danger: 'text-danger-600 dark:text-danger-400',
};

const sizeStyles = {
  sm: { value: 'text-xl', label: 'text-xs' },
  md: { value: 'text-3xl', label: 'text-sm' },
  lg: { value: 'text-4xl', label: 'text-base' },
};

export const MetricCard: React.FC<MetricCardProps> = ({
  value,
  label,
  delta,
  deltaType = 'neutral',
  unit,
  icon,
  size = 'md',
  variant = 'primary',
}) => {
  const getDeltaIcon = () => {
    switch (deltaType) {
      case 'positive':
        return <TrendingUp className="w-3 h-3" />;
      case 'negative':
        return <TrendingDown className="w-3 h-3" />;
      default:
        return <Minus className="w-3 h-3" />;
    }
  };

  const deltaColors = {
    positive: 'text-success-600 bg-success-50',
    negative: 'text-danger-600 bg-danger-50',
    neutral: 'text-slate-500 bg-slate-50',
  };

  return (
    <div className="metric-card group hover:scale-[1.02] transition-transform">
      {icon && (
        <div className="mb-2 text-slate-400 group-hover:text-primary-500 transition-colors">
          {icon}
        </div>
      )}
      
      <div className={`${sizeStyles[size].value} font-bold ${variantStyles[variant]} flex items-baseline justify-center gap-1`}>
        <span>{value}</span>
        {unit && (
          <span className="text-base font-normal text-slate-500 dark:text-slate-400">
            {unit}
          </span>
        )}
      </div>
      
      <div className={`${sizeStyles[size].label} text-slate-500 dark:text-slate-400 mt-1`}>
        {label}
      </div>
      
      {delta && (
        <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full 
          ${deltaColors[deltaType]} text-xs font-medium mt-2`}>
          {getDeltaIcon()}
          <span>{delta}</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;
