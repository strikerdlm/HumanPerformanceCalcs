import React, { useId } from 'react';
import { Info } from 'lucide-react';

interface SliderInputProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit?: string;
  onChange: (value: number) => void;
  tooltip?: string;
  formatValue?: (value: number) => string;
  showMinMax?: boolean;
  disabled?: boolean;
}

export const SliderInput: React.FC<SliderInputProps> = ({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
  tooltip,
  showMinMax = true,
  disabled = false,
}) => {
  const id = useId();
  
  // Calculate fill percentage for gradient
  const fillPercent = ((value - min) / (max - min)) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label 
          htmlFor={id}
          className="text-sm font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1"
        >
          {label}
          {tooltip && (
            <span className="group relative">
              <Info className="w-3.5 h-3.5 text-slate-400 cursor-help" />
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5
                bg-slate-800 text-white text-xs rounded-lg opacity-0 invisible
                group-hover:opacity-100 group-hover:visible transition-all
                whitespace-nowrap z-50">
                {tooltip}
              </span>
            </span>
          )}
        </label>
        <div className="flex items-center gap-1.5">
          <input
            type="number"
            value={value}
            onChange={(e) => onChange(parseFloat(e.target.value) || min)}
            min={min}
            max={max}
            step={step}
            disabled={disabled}
            className="w-20 px-2 py-1 text-sm text-right rounded-lg border border-slate-200 
              dark:border-slate-600 bg-white/50 dark:bg-slate-800/50
              focus:ring-2 focus:ring-primary-500 focus:border-primary-500
              disabled:opacity-50 disabled:cursor-not-allowed"
          />
          {unit && (
            <span className="text-sm text-slate-500 dark:text-slate-400 min-w-[40px]">
              {unit}
            </span>
          )}
        </div>
      </div>
      
      <div className="relative">
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          disabled={disabled}
          className="w-full h-2 rounded-full appearance-none cursor-pointer
            bg-slate-200 dark:bg-slate-700
            disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: `linear-gradient(to right, 
              rgb(59, 130, 246) 0%, 
              rgb(59, 130, 246) ${fillPercent}%, 
              rgb(226, 232, 240) ${fillPercent}%, 
              rgb(226, 232, 240) 100%)`
          }}
        />
        
        {showMinMax && (
          <div className="flex justify-between mt-1">
            <span className="text-xs text-slate-400">{min}{unit}</span>
            <span className="text-xs text-slate-400">{max}{unit}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default SliderInput;
