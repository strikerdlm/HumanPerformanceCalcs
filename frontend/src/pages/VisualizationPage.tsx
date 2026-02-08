import React, { useState, useMemo, useRef, useCallback } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import {
  standardAtmosphere,
  simulatePHSTrajectory,
  simulateMitlerTrajectory,
  predictedHeatStrain,
} from '../calculators';
import { createHeatmapOption } from '../components/charts/ScientificChart';
import { SCIENTIFIC_COLORS, PUBLICATION_THEME } from '../types';
import { Download, Image, FileText, Palette, Eye, RotateCcw } from 'lucide-react';

// ── Palette definitions ─────────────────────────────────────────────
interface ColorPalette {
  id: string;
  name: string;
  colors: readonly string[];
  bg: string;
}
const PALETTES: readonly ColorPalette[] = [
  { id: 'default', name: 'Scientific', colors: [SCIENTIFIC_COLORS.primary, SCIENTIFIC_COLORS.danger, SCIENTIFIC_COLORS.success, SCIENTIFIC_COLORS.warning, SCIENTIFIC_COLORS.secondary, SCIENTIFIC_COLORS.physiology], bg: 'transparent' },
  { id: 'nature', name: 'Nature', colors: ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51', '#606c38'], bg: 'transparent' },
  { id: 'ocean', name: 'Ocean', colors: ['#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#caf0f8', '#48cae4'], bg: 'transparent' },
  { id: 'monochrome', name: 'Monochrome', colors: ['#111827', '#374151', '#6b7280', '#9ca3af', '#d1d5db', '#e5e7eb'], bg: 'transparent' },
  { id: 'warm', name: 'Warm', colors: ['#7f1d1d', '#b91c1c', '#dc2626', '#f97316', '#fbbf24', '#facc15'], bg: 'transparent' },
  { id: 'colorblind', name: 'Colorblind Safe', colors: ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00'], bg: 'transparent' },
] as const;

// ── Data source generators ──────────────────────────────────────────
type DataSourceId = 'atmosphere' | 'circadian' | 'phs_trajectory' | 'phs_sweep';

interface DataSource {
  id: DataSourceId;
  name: string;
  description: string;
  chartTypes: string[];
}

const DATA_SOURCES: readonly DataSource[] = [
  { id: 'atmosphere', name: 'Atmospheric Profile', description: 'ISA temperature, pressure, density vs altitude', chartTypes: ['line'] },
  { id: 'circadian', name: 'Circadian Performance', description: '48h Mitler circadian trajectory', chartTypes: ['line'] },
  { id: 'phs_trajectory', name: 'PHS Heat Strain', description: 'Core temp and dehydration over time', chartTypes: ['line'] },
  { id: 'phs_sweep', name: 'PHS Exposure Heatmap', description: 'Allowable exposure: Temp × Humidity', chartTypes: ['heatmap'] },
] as const;

// ── Preset gallery ──────────────────────────────────────────────────
interface Preset {
  id: string;
  name: string;
  description: string;
  source: DataSourceId;
  palette: string;
}
const PRESETS: readonly Preset[] = [
  { id: 'isa-profile', name: 'ISA Atmospheric Profile', description: 'Temperature, pressure, and density across the troposphere and stratosphere', source: 'atmosphere', palette: 'default' },
  { id: 'circadian-48h', name: '48h Circadian Envelope', description: 'Performance variation across two circadian cycles', source: 'circadian', palette: 'ocean' },
  { id: 'heat-strain', name: 'Heat Strain Trajectory', description: 'Core temperature and dehydration during thermal work', source: 'phs_trajectory', palette: 'warm' },
  { id: 'exposure-map', name: 'Thermal Exposure Heatmap', description: 'Allowable exposure time mapped across temperature and humidity', source: 'phs_sweep', palette: 'nature' },
] as const;

// ── Generate chart data ─────────────────────────────────────────────
function generateOption(source: DataSourceId, palette: ColorPalette): EChartsOption {
  const c = palette.colors;
  switch (source) {
    case 'atmosphere': {
      const alts = Array.from({ length: 41 }, (_, i) => i * 500);
      const temps: number[] = [];
      const pressures: number[] = [];
      const densities: number[] = [];
      for (const a of alts) {
        const isa = standardAtmosphere(a);
        temps.push(isa.temperature_K - 273.15);
        pressures.push(isa.pressure_Pa / 101325);
        densities.push(isa.density_kg_m3);
      }
      return {
        tooltip: { trigger: 'axis' as const },
        legend: { top: 5, textStyle: { color: '#475569' } },
        grid: { left: 70, right: 70, top: 40, bottom: 50 },
        xAxis: { type: 'value' as const, name: 'Altitude (m)', nameLocation: 'middle' as const, nameGap: 30 },
        yAxis: [
          { type: 'value' as const, name: 'Temperature (°C)', position: 'left' as const },
          { type: 'value' as const, name: 'Pressure (atm)', position: 'right' as const },
        ],
        series: [
          { name: 'Temperature', type: 'line' as const, data: alts.map((a, i) => [a, temps[i]]), smooth: true, symbol: 'none', lineStyle: { width: 3, color: c[0] }, itemStyle: { color: c[0] } },
          { name: 'Pressure', type: 'line' as const, yAxisIndex: 1, data: alts.map((a, i) => [a, +pressures[i].toFixed(4)]), smooth: true, symbol: 'none', lineStyle: { width: 3, color: c[1] }, itemStyle: { color: c[1] } },
          { name: 'Density', type: 'line' as const, yAxisIndex: 1, data: alts.map((a, i) => [a, +densities[i].toFixed(4)]), smooth: true, symbol: 'none', lineStyle: { width: 2, color: c[2], type: 'dashed' as const }, itemStyle: { color: c[2] } },
        ],
      };
    }
    case 'circadian': {
      const traj = simulateMitlerTrajectory(6, 2.5, 1.5, 48, 10);
      return {
        tooltip: { trigger: 'axis' as const },
        grid: { left: 60, right: 30, top: 30, bottom: 50 },
        xAxis: { type: 'value' as const, name: 'Time (hours)', nameLocation: 'middle' as const, nameGap: 30 },
        yAxis: { type: 'value' as const, name: 'Performance (%)', nameLocation: 'middle' as const, nameGap: 45, min: 0, max: 120 },
        visualMap: { show: false, min: 50, max: 100, inRange: { color: [c[1] ?? SCIENTIFIC_COLORS.danger, c[3] ?? SCIENTIFIC_COLORS.warning, c[2] ?? SCIENTIFIC_COLORS.success] } },
        series: [{
          type: 'line' as const,
          data: traj.map(p => [p.t_hours, +(p.performance * 100).toFixed(1)]),
          smooth: true, symbol: 'none', lineStyle: { width: 3 },
          areaStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${c[0]}30` }, { offset: 1, color: `${c[0]}05` }] } },
          markLine: { symbol: 'none', data: [
            { yAxis: 77, label: { formatter: 'Adequate' }, lineStyle: { type: 'dashed' as const, color: c[2] } },
            { yAxis: 50, label: { formatter: 'Impaired' }, lineStyle: { type: 'dashed' as const, color: c[1] } },
          ] },
        }],
      };
    }
    case 'phs_trajectory': {
      const traj = simulatePHSTrajectory([350, 36, 42, 55, 0.5, 0.9, 240, 0, 75, 1.9, 37, 38.5, 5], 5);
      return {
        tooltip: { trigger: 'axis' as const },
        legend: { top: 5, textStyle: { color: '#475569' } },
        grid: { left: 60, right: 60, top: 40, bottom: 50 },
        xAxis: { type: 'value' as const, name: 'Time (min)', nameLocation: 'middle' as const, nameGap: 30 },
        yAxis: [
          { type: 'value' as const, name: 'Core Temp (°C)', position: 'left' as const, min: 36.5, max: 40 },
          { type: 'value' as const, name: 'Dehydration (%)', position: 'right' as const, min: 0 },
        ],
        series: [
          { name: 'Core Temperature', type: 'line' as const, data: traj.map(p => [p.time_min, +p.coreTemp_C.toFixed(2)]), smooth: true, symbol: 'none', lineStyle: { width: 3, color: c[1] ?? SCIENTIFIC_COLORS.danger }, itemStyle: { color: c[1] } },
          { name: 'Dehydration', type: 'line' as const, yAxisIndex: 1, data: traj.map(p => [p.time_min, +p.dehydration_percent.toFixed(2)]), smooth: true, symbol: 'none', lineStyle: { width: 3, color: c[3] ?? SCIENTIFIC_COLORS.warning }, itemStyle: { color: c[3] },
            areaStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${c[3] ?? SCIENTIFIC_COLORS.warning}25` }, { offset: 1, color: `${c[3] ?? SCIENTIFIC_COLORS.warning}05` }] } },
          },
        ],
      };
    }
    case 'phs_sweep': {
      const temps = Array.from({ length: 12 }, (_, i) => 26 + i * 2);
      const humids = Array.from({ length: 8 }, (_, i) => 20 + i * 10);
      const data: number[][] = [];
      for (const rh of humids) {
        const row: number[] = [];
        for (const t of temps) {
          try {
            const r = predictedHeatStrain(300, t, t + 5, rh, 0.5, 0.9, 480, 0, 75, 1.9, 37, 38.5, 5);
            row.push(Math.min(r.allowableExposure_min, 480));
          } catch { row.push(480); }
        }
        data.push(row);
      }
      return createHeatmapOption(
        temps.map(t => `${t}°C`), humids.map(h => `${h}%`), data,
        { xAxisName: 'Air Temperature', yAxisName: 'Relative Humidity', colorMin: c[1], colorMax: c[2] },
      );
    }
  }
}

// ── Export helpers ───────────────────────────────────────────────────
function downloadChart(ref: ReactECharts | null, filename: string, format: 'png' | 'svg'): void {
  if (!ref) return;
  const inst = ref.getEchartsInstance();
  if (format === 'svg') {
    // ECharts SVG renderer not available; export as high-res PNG instead
    const url = inst.getDataURL({ type: 'png', pixelRatio: 4, backgroundColor: '#fff' });
    const link = document.createElement('a');
    link.download = `${filename}.png`;
    link.href = url;
    link.click();
    return;
  }
  const url = inst.getDataURL({ type: 'png', pixelRatio: 3, backgroundColor: '#fff' });
  const link = document.createElement('a');
  link.download = `${filename}.png`;
  link.href = url;
  link.click();
}

// ── Main Page ───────────────────────────────────────────────────────
export const VisualizationPage: React.FC = () => {
  const [source, setSource] = useState<DataSourceId>('atmosphere');
  const [paletteId, setPaletteId] = useState('default');
  const [showGrid, setShowGrid] = useState(true);
  const [smooth, setSmooth] = useState(true);
  const chartRef = useRef<ReactECharts>(null);

  const palette = PALETTES.find(p => p.id === paletteId) ?? PALETTES[0];

  const chartOption = useMemo(() => {
    const opt = generateOption(source, palette);
    // Apply grid toggle
    if (!showGrid) {
      const stripGrid = (ax: unknown): unknown => {
        if (ax && typeof ax === 'object') return { ...ax as object, splitLine: { show: false } };
        return ax;
      };
      if (opt.xAxis) (opt as Record<string, unknown>).xAxis = Array.isArray(opt.xAxis) ? opt.xAxis.map(stripGrid) : stripGrid(opt.xAxis);
      if (opt.yAxis) (opt as Record<string, unknown>).yAxis = Array.isArray(opt.yAxis) ? opt.yAxis.map(stripGrid) : stripGrid(opt.yAxis);
    }
    // Apply smooth toggle
    if (Array.isArray(opt.series)) {
      for (const s of opt.series) {
        if (s && typeof s === 'object' && 'type' in s && s.type === 'line') {
          (s as Record<string, unknown>).smooth = smooth;
        }
      }
    }
    return { ...PUBLICATION_THEME, ...opt, title: { show: false } };
  }, [source, palette, showGrid, smooth]);

  const sourceMeta = DATA_SOURCES.find(d => d.id === source) ?? DATA_SOURCES[0];

  const applyPreset = useCallback((preset: Preset) => {
    setSource(preset.source);
    setPaletteId(preset.palette);
  }, []);

  const handleExport = useCallback((fmt: 'png' | 'svg') => {
    downloadChart(chartRef.current, `${sourceMeta.name.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}`, fmt);
  }, [sourceMeta]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">Visualization Studio</h1>
        <p className="text-slate-500 dark:text-slate-400">Build and export publication-quality scientific figures</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Left sidebar — controls */}
        <div className="space-y-4">
          {/* Data source */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-1.5"><Eye className="w-4 h-4" /> Data Source</h3>
            <div className="space-y-2">
              {DATA_SOURCES.map(ds => (
                <button key={ds.id} onClick={() => setSource(ds.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${source === ds.id
                    ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 ring-1 ring-primary-200 dark:ring-primary-700'
                    : 'hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400'}`}>
                  <div className="font-medium">{ds.name}</div>
                  <div className="text-xs opacity-70 mt-0.5">{ds.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Palette */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-1.5"><Palette className="w-4 h-4" /> Color Palette</h3>
            <div className="space-y-2">
              {PALETTES.map(p => (
                <button key={p.id} onClick={() => setPaletteId(p.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${paletteId === p.id
                    ? 'bg-primary-50 dark:bg-primary-900/30 ring-1 ring-primary-200 dark:ring-primary-700'
                    : 'hover:bg-slate-50 dark:hover:bg-slate-700'}`}>
                  <div className="flex gap-0.5">
                    {p.colors.slice(0, 5).map((color, i) => (
                      <div key={i} className="w-4 h-4 rounded-sm" style={{ backgroundColor: color }} />
                    ))}
                  </div>
                  <span className="text-slate-700 dark:text-slate-300">{p.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Plot options */}
          <div className="glass-card p-5 space-y-3">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">Plot Options</h3>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={showGrid} onChange={e => setShowGrid(e.target.checked)} className="rounded border-slate-300" />
              <span className="text-sm text-slate-600 dark:text-slate-400">Show grid lines</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={smooth} onChange={e => setSmooth(e.target.checked)} className="rounded border-slate-300" />
              <span className="text-sm text-slate-600 dark:text-slate-400">Smooth curves</span>
            </label>
          </div>

          {/* Export */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-1.5"><Download className="w-4 h-4" /> Export</h3>
            <div className="flex gap-2">
              <button onClick={() => handleExport('png')}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-primary-500 text-white text-sm font-medium hover:bg-primary-600 transition-colors">
                <Image className="w-4 h-4" /> PNG 3×
              </button>
              <button onClick={() => handleExport('svg')}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-200 text-sm font-medium hover:bg-slate-300 dark:hover:bg-slate-500 transition-colors">
                <FileText className="w-4 h-4" /> Hi-Res
              </button>
            </div>
          </div>
        </div>

        {/* Main chart area */}
        <div className="lg:col-span-3 space-y-4">
          <div className="glass-card p-6">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-800 dark:text-white">{sourceMeta.name}</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">{sourceMeta.description} — <em>{palette.name}</em> palette</p>
              </div>
              <button onClick={() => { setSource('atmosphere'); setPaletteId('default'); setShowGrid(true); setSmooth(true); }}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors" title="Reset">
                <RotateCcw className="w-4 h-4 text-slate-500" />
              </button>
            </div>
            <ReactECharts ref={chartRef} option={chartOption} style={{ height: '480px' }} notMerge lazyUpdate />
            <p className="publication-figure-caption mt-2">
              Publication-quality figure. Use toolbar to zoom/pan, or export buttons for high-resolution output.
            </p>
          </div>

          {/* Preset gallery */}
          <div>
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Preset Gallery</h3>
            <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-3">
              {PRESETS.map(preset => {
                const presetPalette = PALETTES.find(p => p.id === preset.palette) ?? PALETTES[0];
                return (
                  <button key={preset.id} onClick={() => applyPreset(preset)}
                    className="glass-card p-4 text-left hover:ring-2 hover:ring-primary-300 dark:hover:ring-primary-600 transition-all group">
                    <div className="flex gap-0.5 mb-2">
                      {presetPalette.colors.slice(0, 4).map((color, i) => (
                        <div key={i} className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
                      ))}
                    </div>
                    <div className="text-sm font-medium text-slate-800 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{preset.name}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{preset.description}</div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualizationPage;
