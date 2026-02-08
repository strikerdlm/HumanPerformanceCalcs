import React, { useState, useMemo } from 'react';
import {
  spatialDisorientationRisk,
  assessTargetAcquisition,
  rangeForRequiredCycles,
  computeWbvExposure,
  computeMssqShort,
  MSSQ_ITEMS,
} from '../calculators';
import type {
  SDInputs, CriteriaFamily, DiscriminationLevel, ImagingSystem, Target,
} from '../calculators';
import { ScientificChart, createGaugeChartOption } from '../components/charts/ScientificChart';
import { MetricCard, SliderInput } from '../components/ui';
import { SCIENTIFIC_COLORS } from '../types';

type RiskCalc = 'sd' | 'nvg' | 'wbv' | 'mssq';
const tabs = [
  { id: 'sd', label: 'Spatial Disorientation' },
  { id: 'nvg', label: 'NVG / Target Acquisition' },
  { id: 'wbv', label: 'Whole-Body Vibration' },
  { id: 'mssq', label: 'Motion Sickness (MSSQ)' },
];

// ── SD Risk Sub-calculator ──────────────────────────────────────────
const SDPanel: React.FC = () => {
  const [imc, setImc] = useState(true);
  const [night, setNight] = useState(true);
  const [nvg, setNvg] = useState(false);
  const [timeSinceHorizon, setTimeSinceHorizon] = useState(30);
  const [yawRate, setYawRate] = useState(5);
  const [turnDuration, setTurnDuration] = useState(15);
  const [headMove, setHeadMove] = useState(false);
  const [fwdAccel, setFwdAccel] = useState(1.5);
  const [workload, setWorkload] = useState(0.5);

  const result = useMemo(() => {
    const inputs: SDInputs = {
      imc, night, nvg,
      timeSinceHorizonS: timeSinceHorizon,
      yawRateDegS: yawRate,
      sustainedTurnDurationS: turnDuration,
      headMovementDuringTurn: headMove,
      forwardAccelMS2: fwdAccel,
      workload,
    };
    return spatialDisorientationRisk(inputs);
  }, [imc, night, nvg, timeSinceHorizon, yawRate, turnDuration, headMove, fwdAccel, workload]);

  const gaugeOption = useMemo(() => createGaugeChartOption(
    Math.round(result.riskIndex),
    { min: 0, max: 100, unit: '', title: 'SD Index',
      thresholds: [
        { value: 0.25, color: SCIENTIFIC_COLORS.success },
        { value: 0.5, color: SCIENTIFIC_COLORS.warning },
        { value: 0.75, color: '#f97316' },
        { value: 1, color: SCIENTIFIC_COLORS.danger },
      ],
    },
  ), [result.riskIndex]);

  const radarOption = useMemo(() => ({
    radar: {
      indicator: [
        { name: 'Cue Deprivation', max: 1 },
        { name: 'Leans', max: 1 },
        { name: 'Canal Entrainment', max: 1 },
        { name: 'Coriolis', max: 1 },
        { name: 'Somatogravic', max: 1 },
      ],
      shape: 'polygon' as const,
      splitArea: { areaStyle: { color: ['rgba(99,102,241,0.03)', 'rgba(99,102,241,0.07)'] } },
      axisLine: { lineStyle: { color: '#cbd5e1' } },
      splitLine: { lineStyle: { color: '#e2e8f0' } },
    },
    series: [{
      type: 'radar' as const,
      data: [{
        value: [
          result.cueDeprivationComponent,
          result.leansComponent,
          result.canalEntrainmentComponent,
          result.coriolisComponent,
          result.somatogravicComponent,
        ],
        name: 'Component Scores',
        areaStyle: { color: `${SCIENTIFIC_COLORS.primary}25` },
        lineStyle: { width: 2, color: SCIENTIFIC_COLORS.primary },
        itemStyle: { color: SCIENTIFIC_COLORS.primary },
      }],
    }],
  }), [result]);

  const riskColor = result.riskLevel === 'Low' ? 'success'
    : result.riskLevel === 'Moderate' ? 'warning'
    : 'danger';

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="glass-card p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white">🛩️ Flight Conditions</h2>
          <div className="space-y-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={imc} onChange={e => setImc(e.target.checked)} className="rounded border-slate-300" />
              <span className="text-sm text-slate-700 dark:text-slate-300">IMC (Instrument Meteorological Conditions)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={night} onChange={e => setNight(e.target.checked)} className="rounded border-slate-300" />
              <span className="text-sm text-slate-700 dark:text-slate-300">Night Flight</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={nvg} onChange={e => setNvg(e.target.checked)} className="rounded border-slate-300" />
              <span className="text-sm text-slate-700 dark:text-slate-300">NVG Operations</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={headMove} onChange={e => setHeadMove(e.target.checked)} className="rounded border-slate-300" />
              <span className="text-sm text-slate-700 dark:text-slate-300">Head Movement During Turn</span>
            </label>
          </div>
          <SliderInput label="Time Since Horizon" value={timeSinceHorizon} min={0} max={120} step={5} unit="s" onChange={setTimeSinceHorizon} />
          <SliderInput label="Yaw Rate" value={yawRate} min={0} max={40} step={0.5} unit="°/s" onChange={setYawRate} />
          <SliderInput label="Turn Duration" value={turnDuration} min={0} max={60} step={1} unit="s" onChange={setTurnDuration} />
          <SliderInput label="Forward Acceleration" value={fwdAccel} min={0} max={10} step={0.1} unit="m/s²" onChange={setFwdAccel} />
          <SliderInput label="Workload" value={workload} min={0} max={1} step={0.05} onChange={setWorkload} />
        </div>

        {/* Gauge + illusions */}
        <div className="space-y-4">
          <div className="glass-card p-6">
            <ScientificChart option={gaugeOption} title="SD Risk Index" height={280} showToolbox={false}
              caption="0–25 Low, 25–50 Moderate, 50–75 High, 75–100 Very High" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard value={result.riskIndex.toFixed(0)} label="Risk Index" variant={riskColor} />
            <MetricCard value={result.riskLevel} label="Risk Level" variant={riskColor} />
            <MetricCard value={result.somatogravicTiltDeg.toFixed(1)} label="Somatogravic Tilt" unit="°" variant="warning" />
            <MetricCard value={result.likelyIllusions.length.toString()} label="Active Illusions" variant={result.likelyIllusions.length > 0 ? 'danger' : 'success'} />
          </div>
        </div>

        {/* Radar */}
        <div className="glass-card p-6">
          <ScientificChart option={radarOption} title="Component Breakdown" height={320} showToolbox={false}
            caption="Radar plot of vestibular and environmental risk components (0–1 scale)" />
          {result.likelyIllusions.length > 0 && (
            <div className="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
              <p className="text-xs font-semibold text-red-700 dark:text-red-400 mb-1">⚠️ Likely Illusions</p>
              <ul className="text-xs text-red-600 dark:text-red-300 space-y-0.5">
                {result.likelyIllusions.map((ill, i) => <li key={i}>• {ill}</li>)}
              </ul>
            </div>
          )}
          <div className="citation mt-3">
            Reference: FAA Spatial Disorientation Training; Houben et al. (2022). PubMed: 34924407
          </div>
        </div>
      </div>
    </div>
  );
};

// ── NVG / Target Acquisition Sub-calculator ─────────────────────────
const NVGPanel: React.FC = () => {
  const [criteria, setCriteria] = useState<CriteriaFamily>('johnson');
  const [hPixels, setHPixels] = useState(1920);
  const [vPixels, setVPixels] = useState(1080);
  const [hFov, setHFov] = useState(40);
  const [vFov, setVFov] = useState(30);
  const [tgtW, setTgtW] = useState(2.5);
  const [tgtH, setTgtH] = useState(2.0);
  const [range, setRange] = useState(2000);

  const system: ImagingSystem = { horizontalPixels: hPixels, verticalPixels: vPixels, horizontalFovDeg: hFov, verticalFovDeg: vFov };
  const target: Target = { widthM: tgtW, heightM: tgtH };

  const levels: DiscriminationLevel[] = criteria === 'johnson'
    ? ['detection', 'orientation', 'recognition', 'identification']
    : ['detection', 'classification', 'recognition', 'identification'];

  const results = useMemo(() =>
    levels.map(lvl => {
      try { return assessTargetAcquisition(criteria, lvl, system, target, range); }
      catch { return null; }
    }),
    [criteria, hPixels, vPixels, hFov, vFov, tgtW, tgtH, range],
  );

  const maxRanges = useMemo(() =>
    levels.map(lvl => {
      try {
        const table: Record<string, number> = criteria === 'johnson'
          ? { detection: 1.0, orientation: 1.4, recognition: 4.0, identification: 6.4 }
          : { detection: 0.75, classification: 1.5, recognition: 3.0, identification: 6.0 };
        const n50 = table[lvl];
        if (n50 === undefined) return null;
        return { lvl, range: rangeForRequiredCycles(system, target, n50) };
      } catch { return null; }
    }).filter(Boolean) as Array<{ lvl: string; range: number }>,
    [criteria, hPixels, vPixels, hFov, vFov, tgtW, tgtH],
  );

  const barOption = useMemo(() => ({
    tooltip: { trigger: 'axis' as const },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: { type: 'category' as const, data: levels.map(l => l.charAt(0).toUpperCase() + l.slice(1)) },
    yAxis: [
      { type: 'value' as const, name: 'Cycles on Target', position: 'left' as const },
      { type: 'value' as const, name: 'N₅₀ Required', position: 'right' as const },
    ],
    series: [
      {
        name: 'Achieved Cycles', type: 'bar' as const,
        data: results.map(r => r ? +r.cyclesOnTarget.toFixed(2) : 0),
        itemStyle: { color: SCIENTIFIC_COLORS.primary, borderRadius: [4, 4, 0, 0] },
      },
      {
        name: 'Required (N₅₀)', type: 'bar' as const, yAxisIndex: 0,
        data: results.map(r => r ? r.requiredCyclesN50 : 0),
        itemStyle: { color: SCIENTIFIC_COLORS.danger + '60', borderRadius: [4, 4, 0, 0] },
      },
    ],
  }), [results, levels]);

  const maxRangeChart = useMemo(() => ({
    tooltip: { trigger: 'axis' as const },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: { type: 'category' as const, data: maxRanges.map(r => r.lvl.charAt(0).toUpperCase() + r.lvl.slice(1)) },
    yAxis: { type: 'value' as const, name: 'Max Range (m)' },
    series: [{
      type: 'bar' as const,
      data: maxRanges.map(r => Math.round(r.range)),
      itemStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: SCIENTIFIC_COLORS.primary }, { offset: 1, color: SCIENTIFIC_COLORS.secondary }] }, borderRadius: [4, 4, 0, 0] },
      markLine: { symbol: 'none', data: [{ yAxis: range, label: { formatter: `Current: ${range}m` }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.danger } }] },
    }],
  }), [maxRanges, range]);

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="glass-card p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white">🔭 System & Target</h2>
          <div className="flex gap-2">
            <button className={`tab-item ${criteria === 'johnson' ? 'active' : ''}`} onClick={() => setCriteria('johnson')}>Johnson</button>
            <button className={`tab-item ${criteria === 'acquire' ? 'active' : ''}`} onClick={() => setCriteria('acquire')}>ACQUIRE</button>
          </div>
          <SliderInput label="H-Pixels" value={hPixels} min={320} max={4096} step={64} onChange={setHPixels} />
          <SliderInput label="V-Pixels" value={vPixels} min={240} max={2160} step={60} onChange={setVPixels} />
          <SliderInput label="H-FOV" value={hFov} min={5} max={120} step={1} unit="°" onChange={setHFov} />
          <SliderInput label="V-FOV" value={vFov} min={5} max={90} step={1} unit="°" onChange={setVFov} />
          <SliderInput label="Target Width" value={tgtW} min={0.5} max={15} step={0.5} unit="m" onChange={setTgtW} />
          <SliderInput label="Target Height" value={tgtH} min={0.5} max={10} step={0.5} unit="m" onChange={setTgtH} />
          <SliderInput label="Range" value={range} min={100} max={10000} step={100} unit="m" onChange={setRange} />
        </div>

        <div className="glass-card p-6">
          <ScientificChart option={barOption} title="Achieved vs Required Cycles" subtitle={`${criteria.toUpperCase()} criteria at ${range}m`} height={350}
            caption="Blue: achieved line-pair cycles on target. Red: minimum N₅₀ threshold." />
        </div>

        <div className="glass-card p-6">
          <ScientificChart option={maxRangeChart} title="Maximum Acquisition Range" subtitle={`${hPixels}×${vPixels}, ${hFov}°×${vFov}° FOV`} height={350}
            caption="Maximum range to achieve N₅₀ cycles for each discrimination level. Dashed line: current range." />
        </div>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        {results.map((r, i) => r && (
          <MetricCard key={levels[i]} value={r.cyclesOnTarget.toFixed(1)} label={levels[i].charAt(0).toUpperCase() + levels[i].slice(1)}
            unit="cycles" variant={r.meetsN50 ? 'success' : 'danger'} delta={r.meetsN50 ? '≥ N₅₀' : '< N₅₀'} deltaType={r.meetsN50 ? 'positive' : 'negative'} />
        ))}
      </div>
      <div className="citation">Reference: Sjaardema et al. (2015). SAND2015-6368 (Johnson Criteria); ACQUIRE model.</div>
    </div>
  );
};

// ── WBV Sub-calculator ──────────────────────────────────────────────
const WBVPanel: React.FC = () => {
  const [awx, setAwx] = useState(0.3);
  const [awy, setAwy] = useState(0.25);
  const [awz, setAwz] = useState(0.5);
  const [dur, setDur] = useState(8);

  const result = useMemo(() =>
    computeWbvExposure({ awxMS2: awx, awyMS2: awy, awzMS2: awz, exposureDurationS: dur * 3600 }),
    [awx, awy, awz, dur],
  );

  const gaugeOption = useMemo(() => createGaugeChartOption(
    +result.a8.toFixed(3), { min: 0, max: 2, unit: 'm/s²', title: 'A(8)',
      thresholds: [
        { value: 0.47 / 2, color: SCIENTIFIC_COLORS.success },
        { value: 0.93 / 2, color: SCIENTIFIC_COLORS.warning },
        { value: 1, color: SCIENTIFIC_COLORS.danger },
      ] },
  ), [result.a8]);

  const zone = result.a8Zone;
  const zoneColor = zone === 'below_lower' ? 'success' : zone === 'within_hgcz' ? 'warning' : 'danger';
  const zoneLabel = zone === 'below_lower' ? 'Below Action Level' : zone === 'within_hgcz' ? 'Health Guidance Caution Zone' : 'Above Exposure Limit';

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-white">📳 Vibration Input</h2>
        <SliderInput label="aᵤₓ (X-axis)" value={awx} min={0} max={2} step={0.01} unit="m/s²" onChange={setAwx} />
        <SliderInput label="aᵤᵧ (Y-axis)" value={awy} min={0} max={2} step={0.01} unit="m/s²" onChange={setAwy} />
        <SliderInput label="aᵤᵤ (Z-axis)" value={awz} min={0} max={2} step={0.01} unit="m/s²" onChange={setAwz} />
        <SliderInput label="Exposure Duration" value={dur} min={0.5} max={12} step={0.5} unit="h" onChange={setDur} />
        <div className="info-box text-sm">
          Weighting factors: <strong>kₓ=1.4, kᵧ=1.4, kᵤ=1.0</strong> per ISO 2631-1.<br />
          Action level: 0.47 m/s². Limit: 0.93 m/s².
        </div>
        <div className="citation">Reference: ISO 2631-1:1997; Mansfield et al. (2009). Industrial Health 47(4).</div>
      </div>

      <div className="space-y-4">
        <div className="glass-card p-6">
          <ScientificChart option={gaugeOption} title="A(8) Daily Exposure" height={300} showToolbox={false}
            caption="8-hour normalised acceleration. Green < 0.47, Yellow 0.47–0.93, Red > 0.93 m/s²." />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <MetricCard value={result.awCombined.toFixed(3)} label="Combined aₘ" unit="m/s²" variant="primary" />
          <MetricCard value={result.a8.toFixed(3)} label="A(8)" unit="m/s²" variant={zoneColor} />
        </div>
      </div>

      <div className="space-y-4">
        <div className={`glass-card p-6 border-l-4 ${zone === 'below_lower' ? 'border-l-green-500' : zone === 'within_hgcz' ? 'border-l-amber-500' : 'border-l-red-500'}`}>
          <h3 className="font-semibold text-slate-800 dark:text-white mb-2">Zone Classification</h3>
          <span className={`badge ${zone === 'below_lower' ? 'badge-success' : zone === 'within_hgcz' ? 'badge-warning' : 'badge-danger'}`}>
            {zoneLabel}
          </span>
          <div className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-300">
            {result.timeToA8LowerH !== null && (
              <p>Time to action level (0.47): <strong>{result.timeToA8LowerH.toFixed(1)} h</strong></p>
            )}
            {result.timeToA8UpperH !== null && (
              <p>Time to exposure limit (0.93): <strong>{result.timeToA8UpperH.toFixed(1)} h</strong></p>
            )}
          </div>
        </div>
        <div className="glass-card p-6">
          <h3 className="font-semibold text-slate-800 dark:text-white mb-3">Exposure Timeline</h3>
          <ScientificChart option={{
            grid: { left: 50, right: 20, top: 20, bottom: 40 },
            xAxis: { type: 'value' as const, name: 'Duration (h)', nameLocation: 'middle' as const, nameGap: 25, min: 0, max: 12 },
            yAxis: { type: 'value' as const, name: 'A(8) m/s²', min: 0, max: 2 },
            series: [{
              type: 'line' as const, symbol: 'none', smooth: true,
              data: Array.from({ length: 49 }, (_, i) => {
                const h = i * 0.25;
                const a8val = result.awCombined * Math.sqrt((h * 3600) / (8 * 3600));
                return [h, +a8val.toFixed(3)];
              }),
              lineStyle: { width: 3, color: SCIENTIFIC_COLORS.primary },
              areaStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${SCIENTIFIC_COLORS.primary}30` }, { offset: 1, color: `${SCIENTIFIC_COLORS.primary}05` }] } },
              markLine: { symbol: 'none', data: [
                { yAxis: 0.47, label: { formatter: 'Action' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.warning } },
                { yAxis: 0.93, label: { formatter: 'Limit' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.danger } },
              ] },
            }],
          }} height={220} showToolbox={false} caption="A(8) growth over exposure duration for current vibration levels." />
        </div>
      </div>
    </div>
  );
};

// ── MSSQ Sub-calculator ─────────────────────────────────────────────
const MSSQPanel: React.FC = () => {
  const [sectionA, setSectionA] = useState<number[]>(new Array(9).fill(0));
  const [sectionB, setSectionB] = useState<number[]>(new Array(9).fill(0));

  const updateA = (idx: number, val: number) => {
    const next = [...sectionA];
    next[idx] = val;
    setSectionA(next);
  };
  const updateB = (idx: number, val: number) => {
    const next = [...sectionB];
    next[idx] = val;
    setSectionB(next);
  };

  const result = useMemo(() => computeMssqShort(sectionA, sectionB), [sectionA, sectionB]);

  const bandColor = result.percentileBand === '<P25' ? 'success'
    : result.percentileBand === 'P25-P50' ? 'primary'
    : result.percentileBand === 'P50-P75' ? 'warning'
    : 'danger';

  const barOption = useMemo(() => ({
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category' as const, data: MSSQ_ITEMS.map((_, i) => `${i + 1}`), name: 'Item', nameLocation: 'middle' as const, nameGap: 25 },
    yAxis: { type: 'value' as const, name: 'Score', min: 0, max: 3 },
    tooltip: { trigger: 'axis' as const },
    series: [
      { name: 'Section A (childhood)', type: 'bar' as const, data: sectionA, itemStyle: { color: SCIENTIFIC_COLORS.primary, borderRadius: [3, 3, 0, 0] }, barGap: '10%' },
      { name: 'Section B (recent)', type: 'bar' as const, data: sectionB, itemStyle: { color: SCIENTIFIC_COLORS.secondary, borderRadius: [3, 3, 0, 0] } },
    ],
    legend: { top: 0, textStyle: { color: '#475569' } },
  }), [sectionA, sectionB]);

  const scoreLabels = ['Never (0)', 'Rarely (1)', 'Sometimes (2)', 'Frequently (3)'];

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Section A */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-1">Section A — Childhood (before age 12)</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">How often did you feel sick in each situation?</p>
          <div className="space-y-3">
            {MSSQ_ITEMS.map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-sm text-slate-700 dark:text-slate-300 w-48 shrink-0">{item}</span>
                <div className="flex gap-1 flex-wrap">
                  {[0, 1, 2, 3].map(v => (
                    <button key={v} onClick={() => updateA(i, v)}
                      className={`px-2 py-1 rounded text-xs font-medium transition-all ${sectionA[i] === v
                        ? 'bg-primary-500 text-white shadow-sm' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200'}`}>
                      {scoreLabels[v]}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section B */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-1">Section B — Last 10 Years</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">How often have you felt sick recently?</p>
          <div className="space-y-3">
            {MSSQ_ITEMS.map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-sm text-slate-700 dark:text-slate-300 w-48 shrink-0">{item}</span>
                <div className="flex gap-1 flex-wrap">
                  {[0, 1, 2, 3].map(v => (
                    <button key={v} onClick={() => updateB(i, v)}
                      className={`px-2 py-1 rounded text-xs font-medium transition-all ${sectionB[i] === v
                        ? 'bg-secondary-500 text-white shadow-sm' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200'}`}>
                      {scoreLabels[v]}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="grid md:grid-cols-4 gap-4">
        <MetricCard value={result.sectionASum.toString()} label="Section A (Childhood)" unit="/27" variant="primary" />
        <MetricCard value={result.sectionBSum.toString()} label="Section B (Recent)" unit="/27" variant="primary" />
        <MetricCard value={result.totalSum.toString()} label="Total Score" unit="/54" variant={bandColor} />
        <MetricCard value={result.percentileBand} label="Percentile Band" variant={bandColor} />
      </div>

      <div className="glass-card p-6">
        <ScientificChart option={barOption} title="Item-Level Scores" subtitle="Section A (childhood) vs Section B (recent 10 years)" height={300}
          caption="Per-item MSSQ-short scores. Higher values indicate greater motion sickness susceptibility." />
      </div>
      <div className="citation">Reference: Rivera et al. (2022). Rev Otorrinolaringol 82(2); Golding (2006). Autonomic Neuroscience 129(1-2).</div>
    </div>
  );
};

// ── Main Page ───────────────────────────────────────────────────────
export const RiskAssessmentPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<RiskCalc>('sd');

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">Risk Assessment</h1>
        <p className="text-slate-500 dark:text-slate-400">Multi-domain risk profiling for aerospace and occupational environments</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id as RiskCalc)}
            className={`tab-item ${activeTab === t.id ? 'active' : ''}`}>{t.label}</button>
        ))}
      </div>

      {activeTab === 'sd' && <SDPanel />}
      {activeTab === 'nvg' && <NVGPanel />}
      {activeTab === 'wbv' && <WBVPanel />}
      {activeTab === 'mssq' && <MSSQPanel />}
    </div>
  );
};

export default RiskAssessmentPage;
