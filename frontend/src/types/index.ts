/**
 * Type definitions for the Aerospace Medicine Dashboard
 */

export type CalculatorCategory = 
  | 'home'
  | 'atmospheric'
  | 'clinical'
  | 'occupational'
  | 'environmental'
  | 'fatigue'
  | 'simulation'
  | 'visualization'
  | 'risk';

export interface NavigationItem {
  id: CalculatorCategory;
  label: string;
  icon: string;
  description: string;
}

export interface MetricCardProps {
  value: string | number;
  label: string;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  unit?: string;
  icon?: React.ReactNode;
}

export interface SliderInputProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit?: string;
  onChange: (value: number) => void;
  tooltip?: string;
  formatValue?: (value: number) => string;
}

export interface ChartConfig {
  title: string;
  subtitle?: string;
  xAxis: {
    name: string;
    unit?: string;
    type: 'value' | 'category';
  };
  yAxis: {
    name: string;
    unit?: string;
    type: 'value' | 'log';
  };
  series: ChartSeries[];
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  animation?: boolean;
}

export interface ChartSeries {
  name: string;
  type: 'line' | 'bar' | 'scatter' | 'area' | 'gauge' | 'heatmap';
  data: [number, number][] | number[];
  color?: string;
  smooth?: boolean;
  areaStyle?: boolean;
  markLine?: MarkLineConfig;
  markArea?: MarkAreaConfig;
}

export interface MarkLineConfig {
  data: Array<{
    yAxis?: number;
    xAxis?: number;
    label?: { formatter: string };
    lineStyle?: { type: 'solid' | 'dashed' | 'dotted'; color?: string };
  }>;
}

export interface MarkAreaConfig {
  data: Array<[{ xAxis?: number; yAxis?: number }, { xAxis?: number; yAxis?: number }]>;
  itemStyle?: { color: string; opacity: number };
}

export interface Reference {
  authors: string;
  year: number;
  title: string;
  journal?: string;
  doi?: string;
  url?: string;
}

export interface CalculatorMeta {
  name: string;
  description: string;
  references: Reference[];
  limitations: string[];
  version: string;
}

// Scientific color palette for publication-quality figures
export const SCIENTIFIC_COLORS = {
  primary: '#2563eb',     // Blue - main data
  secondary: '#7c3aed',   // Purple - secondary data
  success: '#22c55e',     // Green - positive/safe
  warning: '#f59e0b',     // Amber - caution
  danger: '#ef4444',      // Red - danger/limit
  physiology: '#0ea5e9',  // Cyan - physiological
  environment: '#16a34a', // Emerald - environmental
  clinical: '#8b5cf6',    // Violet - clinical
  neutral: '#64748b',     // Slate - neutral
  
  // Sequential palette for heatmaps
  sequential: [
    '#eef2ff', '#c7d2fe', '#a5b4fc', '#818cf8', 
    '#6366f1', '#4f46e5', '#4338ca', '#3730a3'
  ],
  
  // Diverging palette for comparison
  diverging: [
    '#dc2626', '#f87171', '#fca5a5', '#fecaca',
    '#d1fae5', '#a7f3d0', '#6ee7b7', '#10b981'
  ],
} as const;

// ECharts theme configuration for publication
export const PUBLICATION_THEME = {
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: 'Inter, system-ui, sans-serif',
    color: '#1e293b',
  },
  title: {
    textStyle: {
      fontWeight: 600,
      fontSize: 16,
      color: '#0f172a',
    },
    subtextStyle: {
      fontSize: 12,
      color: '#64748b',
    },
  },
  legend: {
    textStyle: {
      color: '#475569',
    },
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e2e8f0',
    textStyle: {
      color: '#1e293b',
    },
    extraCssText: 'box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);',
  },
  xAxis: {
    axisLine: { lineStyle: { color: '#cbd5e1' } },
    axisTick: { lineStyle: { color: '#cbd5e1' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
  },
  yAxis: {
    axisLine: { lineStyle: { color: '#cbd5e1' } },
    axisTick: { lineStyle: { color: '#cbd5e1' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#f1f5f9' } },
  },
  grid: {
    left: 60,
    right: 30,
    top: 60,
    bottom: 50,
    containLabel: true,
  },
} as const;
