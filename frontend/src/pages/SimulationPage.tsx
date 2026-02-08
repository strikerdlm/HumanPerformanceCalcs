import React, { useState, useMemo } from 'react';
import {
  simulatePHSTrajectory, predictedHeatStrain,
  simulateMitlerTrajectory,
} from '../calculators';
import { ScientificChart, createHeatmapOption } from '../components/charts/ScientificChart';
import { MetricCard, SliderInput } from '../components/ui';
import { SCIENTIFIC_COLORS } from '../types';

type SimMode = 'phs' | 'mitler' | 'sweep';

const modes = [
  { id: 'phs', label: 'PHS Heat Strain Trajectory' },
  { id: 'mitler', label: 'Circadian 48h Forecast' },
  { id: 'sweep', label: 'Parameter Sweep Heatmap' },
];

export const SimulationPage: React.FC = () => {
  const [mode, setMode] = useState<SimMode>('phs');

  // PHS state
  const [phsMet, setPhsMet] = useState(350);
  const [phsAir, setPhsAir] = useState(34);
  const [phsRad, setPhsRad] = useState(40);
  const [phsRH, setPhsRH] = useState(60);
  const [phsWind, setPhsWind] = useState(0.5);
  const [phsClo, setPhsClo] = useState(0.9);
  const [phsDur, setPhsDur] = useState(180);
  const [phsMass, setPhsMass] = useState(75);
  const [phsCoreLim, setPhsCoreLim] = useState(38.5);
  const [phsDehydLim, setPhsDehydLim] = useState(5);

  // Mitler state
  const [mPhi, setMPhi] = useState(6);
  const [mSD, setMSD] = useState(2.5);
  const [mK, setMK] = useState(1.5);

  // Sweep state
  const [sweepMet, setSweepMet] = useState(300);

  // PHS trajectory
  const phsTrajectory = useMemo(() => (
    simulatePHSTrajectory(
      [phsMet, phsAir, phsRad, phsRH, phsWind, phsClo, phsDur, 0, phsMass, 1.9, 37.0, phsCoreLim, phsDehydLim], 5
    )
  ), [phsMet, phsAir, phsRad, phsRH, phsWind, phsClo, phsDur, phsMass, phsCoreLim, phsDehydLim]);

  const phsResult = useMemo(() => (
    predictedHeatStrain(phsMet, phsAir, phsRad, phsRH, phsWind, phsClo, phsDur, 0, phsMass, 1.9, 37.0, phsCoreLim, phsDehydLim)
  ), [phsMet, phsAir, phsRad, phsRH, phsWind, phsClo, phsDur, phsMass, phsCoreLim, phsDehydLim]);

  const phsChartOption = useMemo(() => {
    const times = phsTrajectory.map(p => p.time_min);
    const core = phsTrajectory.map(p => p.coreTemp_C);
    const dehy = phsTrajectory.map(p => p.dehydration_percent);
    return {
      tooltip: { trigger: 'axis' as const },
      legend: { top: 5, textStyle: { color: '#475569' } },
      grid: { left: 60, right: 60, top: 40, bottom: 50 },
      xAxis: { type: 'value' as const, name: 'Time (min)', nameLocation: 'middle' as const, nameGap: 30 },
      yAxis: [
        { type: 'value' as const, name: 'Core Temp (°C)', position: 'left' as const, min: 36.5, max: 40 },
        { type: 'value' as const, name: 'Dehydration (%)', position: 'right' as const, min: 0, max: Math.max(10, phsDehydLim * 1.5) },
      ],
      series: [
        {
          name: 'Core Temperature', type: 'line' as const,
          data: times.map((t, i) => [t, core[i]]), smooth: true, symbol: 'none',
          lineStyle: { width: 3, color: SCIENTIFIC_COLORS.danger },
          itemStyle: { color: SCIENTIFIC_COLORS.danger },
          markLine: { symbol: 'none', data: [{ yAxis: phsCoreLim, label: { formatter: `Core limit ${phsCoreLim}°C` }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.danger } }] },
        },
        {
          name: 'Dehydration', type: 'line' as const, yAxisIndex: 1,
          data: times.map((t, i) => [t, dehy[i]]), smooth: true, symbol: 'none',
          lineStyle: { width: 3, color: SCIENTIFIC_COLORS.warning },
          itemStyle: { color: SCIENTIFIC_COLORS.warning },
          areaStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${SCIENTIFIC_COLORS.warning}30` }, { offset: 1, color: `${SCIENTIFIC_COLORS.warning}05` }] } },
          markLine: { symbol: 'none', data: [{ yAxis: phsDehydLim, label: { formatter: `Dehydration limit ${phsDehydLim}%` }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.warning } }] },
        },
      ],
    };
  }, [phsTrajectory, phsCoreLim, phsDehydLim]);

  // Mitler 48h
  const mitlerChart = useMemo(() => {
    const traj = simulateMitlerTrajectory(mPhi, mSD, mK, 48, 10);
    return {
      tooltip: { trigger: 'axis' as const },
      grid: { left: 60, right: 30, top: 30, bottom: 50 },
      xAxis: { type: 'value' as const, name: 'Time (hours)', nameLocation: 'middle' as const, nameGap: 30 },
      yAxis: { type: 'value' as const, name: 'Performance (%)', nameLocation: 'middle' as const, nameGap: 45, min: 0, max: 120 },
      visualMap: { show: false, min: 50, max: 100, inRange: { color: [SCIENTIFIC_COLORS.danger, SCIENTIFIC_COLORS.warning, SCIENTIFIC_COLORS.success] } },
      series: [{
        type: 'line' as const,
        data: traj.map(p => [p.t_hours, p.performance * 100]),
        smooth: true, symbol: 'none',
        lineStyle: { width: 3 },
        areaStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${SCIENTIFIC_COLORS.primary}25` }, { offset: 1, color: `${SCIENTIFIC_COLORS.primary}05` }] } },
        markLine: { symbol: 'none', data: [
          { yAxis: 77, label: { formatter: 'Adequate' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.success } },
          { yAxis: 50, label: { formatter: 'Impaired' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.danger } },
        ] },
        markArea: { silent: true, data: [
          [{ xAxis: 22, itemStyle: { color: 'rgba(99,102,241,0.06)' } }, { xAxis: 30 }],
          [{ xAxis: 46, itemStyle: { color: 'rgba(99,102,241,0.06)' } }, { xAxis: 48 }],
        ] },
      }],
    };
  }, [mPhi, mSD, mK]);

  // 2D Sweep heatmap: Air Temp × RH → Allowable exposure
  const sweepData = useMemo(() => {
    const temps = Array.from({ length: 15 }, (_, i) => 25 + i * 2);
    const humids = Array.from({ length: 10 }, (_, i) => 20 + i * 10);
    const data: number[][] = [];
    for (const rh of humids) {
      const row: number[] = [];
      for (const t of temps) {
        try {
          const r = predictedHeatStrain(sweepMet, t, t + 5, rh, 0.5, 0.9, 480, 0, 75, 1.9, 37, 38.5, 5);
          row.push(Math.min(r.allowableExposure_min, 480));
        } catch {
          row.push(480);
        }
      }
      data.push(row);
    }
    return {
      temps: temps.map(t => `${t}°C`),
      humids: humids.map(h => `${h}%`),
      data,
    };
  }, [sweepMet]);

  const sweepOption = useMemo(() => (
    createHeatmapOption(sweepData.temps, sweepData.humids, sweepData.data, {
      xAxisName: 'Air Temperature', yAxisName: 'Relative Humidity',
      colorMin: SCIENTIFIC_COLORS.danger, colorMax: SCIENTIFIC_COLORS.success,
    })
  ), [sweepData]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">Simulation Studio</h1>
        <p className="text-slate-500 dark:text-slate-400">Forward trajectory simulation and multi-parameter sensitivity analysis</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {modes.map(m => (
          <button key={m.id} onClick={() => setMode(m.id as SimMode)}
            className={`tab-item ${mode === m.id ? 'active' : ''}`}>{m.label}</button>
        ))}
      </div>

      {/* PHS Trajectory */}
      {mode === 'phs' && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">♨️ Predicted Heat Strain Trajectory</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium text-slate-700 dark:text-slate-300">Work</h3>
                <SliderInput label="Metabolic Rate" value={phsMet} min={150} max={650} step={10} unit="W/m²" onChange={setPhsMet} />
                <SliderInput label="Clothing" value={phsClo} min={0.3} max={1.6} step={0.1} unit="clo" onChange={setPhsClo} />
                <SliderInput label="Duration" value={phsDur} min={15} max={480} step={15} unit="min" onChange={setPhsDur} />
              </div>
              <div className="space-y-4">
                <h3 className="font-medium text-slate-700 dark:text-slate-300">Environment</h3>
                <SliderInput label="Air Temp" value={phsAir} min={20} max={50} step={0.5} unit="°C" onChange={setPhsAir} />
                <SliderInput label="Radiant Temp" value={phsRad} min={20} max={60} step={0.5} unit="°C" onChange={setPhsRad} />
                <SliderInput label="RH" value={phsRH} min={10} max={100} step={5} unit="%" onChange={setPhsRH} />
                <SliderInput label="Wind" value={phsWind} min={0.1} max={3} step={0.1} unit="m/s" onChange={setPhsWind} />
              </div>
              <div className="space-y-4">
                <h3 className="font-medium text-slate-700 dark:text-slate-300">Limits</h3>
                <SliderInput label="Body Mass" value={phsMass} min={50} max={120} step={1} unit="kg" onChange={setPhsMass} />
                <SliderInput label="Core Limit" value={phsCoreLim} min={37.5} max={39.5} step={0.1} unit="°C" onChange={setPhsCoreLim} />
                <SliderInput label="Dehydration Limit" value={phsDehydLim} min={2} max={7} step={0.5} unit="%" onChange={setPhsDehydLim} />
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-4">
            <MetricCard value={phsResult.predictedCoreTemp_C.toFixed(2)} label="Predicted Core Temp" unit="°C"
              variant={phsResult.predictedCoreTemp_C > phsCoreLim ? 'danger' : 'primary'} />
            <MetricCard value={phsResult.requiredSweatRate_L_h.toFixed(2)} label="Required Sweat Rate" unit="L/h" variant="warning" />
            <MetricCard value={phsResult.dehydrationPercent.toFixed(1)} label="Dehydration" unit="%" variant={phsResult.dehydrationPercent > phsDehydLim ? 'danger' : 'warning'} />
            <MetricCard value={phsResult.allowableExposure_min.toFixed(0)} label="Allowable Exposure" unit="min"
              variant={phsResult.allowableExposure_min < phsDur ? 'danger' : 'success'} delta={phsResult.limitingFactor} />
          </div>

          <div className="glass-card p-6">
            <ScientificChart option={phsChartOption} title="Heat Strain Forward Simulation"
              subtitle={`${phsMet} W/m², ${phsAir}°C, ${phsRH}% RH`} height={450}
              caption="Dual-axis trajectory: core temperature (left, red) and dehydration (right, amber). Dashed lines indicate physiological limits. Model inspired by ISO 7933:2023." />
          </div>
        </div>
      )}

      {/* Mitler 48h */}
      {mode === 'mitler' && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">🧠 48-Hour Circadian Forecast</h2>
            <SliderInput label="Phase (φ)" value={mPhi} min={0} max={24} step={0.5} unit="h" onChange={setMPhi} />
            <SliderInput label="Sleep Debt (SD)" value={mSD} min={0.5} max={5} step={0.1} onChange={setMSD} />
            <SliderInput label="Scaling (K)" value={mK} min={0.5} max={3} step={0.1} onChange={setMK} />
            <div className="info-box">
              <strong>Shaded bands:</strong> Typical sleep windows (22:00–06:00).<br />
              Green line: adequate performance. Red line: impaired threshold.
            </div>
            <div className="citation">Reference: Mitler et al. (1988). Sleep 11(1).</div>
          </div>
          <div className="lg:col-span-2 glass-card p-6">
            <ScientificChart option={mitlerChart as import('echarts').EChartsOption} title="48-Hour Performance Envelope"
              subtitle={`φ=${mPhi}h, SD=${mSD}, K=${mK}`} height={450}
              caption="Circadian performance forecast showing predicted efficiency over 48 hours. Shaded bands represent sleep periods." />
          </div>
        </div>
      )}

      {/* Parameter Sweep */}
      {mode === 'sweep' && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">🔬 PHS 2D Parameter Sweep</h2>
            <div className="grid md:grid-cols-2 gap-6 max-w-xl">
              <SliderInput label="Metabolic Rate" value={sweepMet} min={150} max={500} step={25} unit="W/m²" onChange={setSweepMet} />
              <div className="info-box text-sm">
                Heatmap shows <strong>allowable exposure time</strong> (minutes, max 480) as a function of air temperature (x-axis) and relative humidity (y-axis).
              </div>
            </div>
          </div>
          <div className="glass-card p-6">
            <ScientificChart option={sweepOption} title="Allowable Exposure: Temperature × Humidity"
              subtitle={`Metabolic rate: ${sweepMet} W/m², 0.9 clo, 0.5 m/s wind`} height={500}
              caption="Green: longer safe exposure. Red: shorter allowable exposure due to heat strain limits. Model inspired by ISO 7933:2023." />
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationPage;
