import React, { useState, useMemo } from 'react';
import {
  simulateMitlerTrajectory,
  simulateTwoProcess,
  jetLagDaysToAdjust,
  faa117Limits,
  easaMaxDailyFdp,
} from '../calculators';
import { ScientificChart, createLineChartOption } from '../components/charts/ScientificChart';
import { MetricCard, SliderInput } from '../components/ui';
import { SCIENTIFIC_COLORS } from '../types';

type CalcType = 'mitler' | 'twoprocess' | 'jetlag' | 'faa117' | 'easa';

const calculatorOptions = [
  { id: 'mitler', label: 'Mitler Circadian Model' },
  { id: 'twoprocess', label: 'Two-Process Sleep Model' },
  { id: 'jetlag', label: 'Jet Lag Recovery' },
  { id: 'faa117', label: 'FAA Part 117' },
  { id: 'easa', label: 'EASA ORO.FTL' },
];

export const FatiguePage: React.FC = () => {
  const [selectedCalc, setSelectedCalc] = useState<CalcType>('mitler');

  // Mitler state
  const [phi, setPhi] = useState(6);
  const [SD, setSD] = useState(2.5);
  const [K, setK] = useState(1.5);
  const [horizon, setHorizon] = useState(48);

  // Two-Process state
  const [wakeH, setWakeH] = useState(16);
  const [sleepH, setSleepH] = useState(8);
  const [cycles, setCycles] = useState(3);

  // Jet lag state
  const [timeZones, setTimeZones] = useState(6);
  const [direction, setDirection] = useState<'east' | 'west'>('east');

  // FAA 117 state
  const [reportTime, setReportTime] = useState('07:00');
  const [segments, setSegments] = useState(3);
  const [notAcclimated, setNotAcclimated] = useState(false);

  // EASA state
  const [easaReportTime, setEasaReportTime] = useState('08:00');
  const [easaSectors, setEasaSectors] = useState(3);
  const [easaState, setEasaState] = useState<'acclimatised' | 'unknown' | 'unknown_frm'>('acclimatised');

  // Mitler chart
  const mitlerChart = useMemo(() => {
    const traj = simulateMitlerTrajectory(phi, SD, K, horizon, 15);
    const times = traj.map(p => p.t_hours);
    const perfs = traj.map(p => p.performance * 100);

    return {
      tooltip: { trigger: 'axis' as const },
      legend: { top: 5 },
      grid: { left: 60, right: 30, top: 40, bottom: 50 },
      xAxis: {
        type: 'value' as const,
        name: 'Time (hours)',
        nameLocation: 'middle' as const,
        nameGap: 30,
      },
      yAxis: {
        type: 'value' as const,
        name: 'Performance (%)',
        nameLocation: 'middle' as const,
        nameGap: 45,
        min: 0,
        max: 120,
      },
      series: [{
        name: 'Circadian Performance',
        type: 'line' as const,
        data: times.map((t, i) => [t, perfs[i]]),
        smooth: true,
        lineStyle: { width: 3, color: SCIENTIFIC_COLORS.primary },
        itemStyle: { color: SCIENTIFIC_COLORS.primary },
        areaStyle: {
          color: {
            type: 'linear' as const,
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: `${SCIENTIFIC_COLORS.primary}30` },
              { offset: 1, color: `${SCIENTIFIC_COLORS.primary}05` },
            ],
          },
        },
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: 70, label: { formatter: '70% threshold' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.warning } },
          ],
        },
        markArea: {
          silent: true,
          data: Array.from({ length: Math.ceil(horizon / 24) }, (_, d) => [{
            xAxis: d * 24 + 22,
            itemStyle: { color: 'rgba(99, 102, 241, 0.08)' },
          }, {
            xAxis: Math.min(d * 24 + 30, horizon),
          }]),
        },
      }],
    };
  }, [phi, SD, K, horizon]);

  // Two-Process chart
  const twoProcessChart = useMemo(() => {
    const traj = simulateTwoProcess(wakeH, sleepH, cycles, 10);
    return {
      tooltip: { trigger: 'axis' as const },
      legend: { top: 5, textStyle: { color: '#475569' } },
      grid: { left: 60, right: 30, top: 40, bottom: 50 },
      xAxis: {
        type: 'value' as const, name: 'Time (hours)',
        nameLocation: 'middle' as const, nameGap: 30,
      },
      yAxis: {
        type: 'value' as const, name: 'Process Level',
        nameLocation: 'middle' as const, nameGap: 45,
      },
      series: [
        {
          name: 'S (Homeostatic)', type: 'line' as const,
          data: traj.map(p => [p.t_hours, p.S]),
          smooth: true,
          lineStyle: { width: 2.5, color: SCIENTIFIC_COLORS.danger },
          itemStyle: { color: SCIENTIFIC_COLORS.danger },
          symbol: 'none',
        },
        {
          name: 'C (Circadian)', type: 'line' as const,
          data: traj.map(p => [p.t_hours, p.C]),
          smooth: true,
          lineStyle: { width: 2.5, color: SCIENTIFIC_COLORS.primary, type: 'dashed' as const },
          itemStyle: { color: SCIENTIFIC_COLORS.primary },
          symbol: 'none',
        },
        {
          name: 'Alertness (S+C)', type: 'line' as const,
          data: traj.map(p => [p.t_hours, p.alertness]),
          smooth: true,
          lineStyle: { width: 3, color: SCIENTIFIC_COLORS.success },
          itemStyle: { color: SCIENTIFIC_COLORS.success },
          areaStyle: {
            color: {
              type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: `${SCIENTIFIC_COLORS.success}25` },
                { offset: 1, color: `${SCIENTIFIC_COLORS.success}05` },
              ],
            },
          },
          symbol: 'none',
        },
      ],
    };
  }, [wakeH, sleepH, cycles]);

  // Jet lag chart
  const jetLagResult = useMemo(() => jetLagDaysToAdjust(timeZones, direction), [timeZones, direction]);
  const jetLagChart = useMemo(() => {
    const zones = Array.from({ length: 13 }, (_, i) => i);
    const eastDays = zones.map(z => jetLagDaysToAdjust(z, 'east').daysToAdjust);
    const westDays = zones.map(z => jetLagDaysToAdjust(z, 'west').daysToAdjust);

    return createLineChartOption(zones, [
      { name: 'Eastward', data: eastDays, color: SCIENTIFIC_COLORS.danger, smooth: true },
      { name: 'Westward', data: westDays, color: SCIENTIFIC_COLORS.primary, smooth: true },
    ], {
      xAxisName: 'Time Zones Crossed', yAxisName: 'Recovery', yAxisUnit: 'days',
    });
  }, []);

  // FAA 117 result
  const faaResult = useMemo(() => {
    try { return faa117Limits(reportTime, segments, notAcclimated); }
    catch { return null; }
  }, [reportTime, segments, notAcclimated]);

  // FAA segments chart
  const faaChart = useMemo(() => {
    const segs = [1, 2, 3, 4, 5, 6, 7];
    const fdps = segs.map(s => {
      try { return faa117Limits(reportTime, s, notAcclimated).maxFdpHours; }
      catch { return 0; }
    });

    return {
      tooltip: { trigger: 'axis' as const },
      grid: { left: 60, right: 30, top: 30, bottom: 50 },
      xAxis: {
        type: 'category' as const,
        data: segs.map(s => `${s}`),
        name: 'Flight Segments',
        nameLocation: 'middle' as const,
        nameGap: 30,
      },
      yAxis: {
        type: 'value' as const,
        name: 'Max FDP (hours)',
        nameLocation: 'middle' as const,
        nameGap: 45,
        min: 8, max: 15,
      },
      series: [{
        type: 'bar' as const,
        data: fdps.map(v => ({
          value: v,
          itemStyle: { color: v >= 12 ? SCIENTIFIC_COLORS.success : v >= 10 ? SCIENTIFIC_COLORS.warning : SCIENTIFIC_COLORS.danger },
        })),
        barWidth: '50%',
        label: { show: true, position: 'top' as const, formatter: '{c}h', fontSize: 11 },
      }],
    };
  }, [reportTime, notAcclimated]);

  // EASA result
  const easaResult = useMemo(() => {
    try { return easaMaxDailyFdp(easaReportTime, easaSectors, easaState); }
    catch { return null; }
  }, [easaReportTime, easaSectors, easaState]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
          Fatigue & Circadian Calculators
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Circadian performance modeling, sleep regulation, jet lag recovery, and regulatory duty limits
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {calculatorOptions.map(opt => (
          <button key={opt.id} onClick={() => setSelectedCalc(opt.id as CalcType)}
            className={`tab-item ${selectedCalc === opt.id ? 'active' : ''}`}>{opt.label}</button>
        ))}
      </div>

      {/* Mitler Circadian */}
      {selectedCalc === 'mitler' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">🧠 Mitler Circadian Performance</h2>
            <SliderInput label="Phase Offset (φ)" value={phi} min={0} max={24} step={0.5} unit="h" onChange={setPhi} />
            <SliderInput label="Sleep Debt (SD)" value={SD} min={0.5} max={5} step={0.1} onChange={setSD} />
            <SliderInput label="Scaling (K)" value={K} min={0.5} max={3} step={0.1} onChange={setK} />
            <SliderInput label="Horizon" value={horizon} min={24} max={96} step={12} unit="h" onChange={setHorizon} />
            <div className="info-box">
              <strong>Model:</strong> P = (1/K)[K − cos²θ × (1 − cosθ/SD)²], θ = 2π(t+φ)/24
            </div>
            <div className="citation">Reference: Mitler et al. (1988). Catastrophes, sleep, and public policy. Sleep 11(1).</div>
          </div>
          <div className="glass-card p-6">
            <ScientificChart option={mitlerChart as import('echarts').EChartsOption} title="Circadian Performance Envelope"
              subtitle={`φ=${phi}h, SD=${SD}, K=${K}`} height={420}
              caption="Shaded regions indicate typical sleep windows (22:00–06:00). Dashed line: 70% performance threshold." />
          </div>
        </div>
      )}

      {/* Two-Process */}
      {selectedCalc === 'twoprocess' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">😴 Two-Process Sleep Model</h2>
            <SliderInput label="Wake Duration" value={wakeH} min={12} max={24} step={1} unit="h" onChange={setWakeH} />
            <SliderInput label="Sleep Duration" value={sleepH} min={4} max={12} step={1} unit="h" onChange={setSleepH} />
            <SliderInput label="Cycles" value={cycles} min={1} max={5} step={1} onChange={setCycles} />
            <div className="info-box">
              <strong>Process S (homeostatic):</strong> Exponential rise during wake, exponential decay during sleep<br />
              <strong>Process C (circadian):</strong> Cosine oscillation with ~24h period
            </div>
            <div className="citation">Reference: Borbély, A.A. (1982). A two-process model of sleep regulation. Human Neurobiology 1:195-204.</div>
          </div>
          <div className="glass-card p-6">
            <ScientificChart option={twoProcessChart} title="Two-Process Model Dynamics"
              subtitle={`${wakeH}h wake / ${sleepH}h sleep × ${cycles} cycles`} height={420}
              caption="Red: homeostatic sleep pressure (S). Blue dashed: circadian process (C). Green: combined alertness (S+C)." />
          </div>
        </div>
      )}

      {/* Jet Lag */}
      {selectedCalc === 'jetlag' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">✈️ Jet Lag Recovery Estimator</h2>
            <SliderInput label="Time Zones Crossed" value={timeZones} min={0} max={12} step={1} onChange={setTimeZones} />
            <div className="flex gap-3">
              {(['east', 'west'] as const).map(d => (
                <button key={d} onClick={() => setDirection(d)}
                  className={`flex-1 py-3 rounded-xl font-semibold transition-all ${direction === d
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg'
                    : 'bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'}`}>
                  {d === 'east' ? '→ Eastward' : '← Westward'}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <MetricCard value={jetLagResult.daysToAdjust.toFixed(1)} label="Recovery Time" unit="days"
                variant={jetLagResult.daysToAdjust > 7 ? 'danger' : jetLagResult.daysToAdjust > 4 ? 'warning' : 'success'} />
              <MetricCard value={jetLagResult.adjustmentRateMinPerDay.toFixed(0)} label="Adjustment Rate" unit="min/day" variant="primary" />
            </div>
            <div className={jetLagResult.daysToAdjust > 5 ? 'warning-box' : 'info-box'}>
              Eastward travel is generally harder to adjust to (~60 min/day) compared to westward (~90 min/day).
            </div>
          </div>
          <div className="glass-card p-6">
            <ScientificChart option={jetLagChart} title="Jet Lag Recovery by Direction" height={400}
              caption="Eastward adjustment is typically slower due to the body's natural tendency toward a >24h circadian period." />
          </div>
        </div>
      )}

      {/* FAA Part 117 */}
      {selectedCalc === 'faa117' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">🛩️ FAA Part 117 Duty Limits</h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-1">Report Time (local)</label>
                <input type="time" value={reportTime} onChange={e => setReportTime(e.target.value)}
                  className="input-scientific" />
              </div>
              <SliderInput label="Flight Segments" value={segments} min={1} max={7} step={1} onChange={setSegments} />
              <div className="flex items-center gap-3">
                <input type="checkbox" id="notAccl" checked={notAcclimated} onChange={e => setNotAcclimated(e.target.checked)}
                  className="w-4 h-4 rounded" />
                <label htmlFor="notAccl" className="text-sm text-slate-700 dark:text-slate-300">Not acclimated (−30 min FDP)</label>
              </div>
            </div>
            {faaResult && (
              <div className="grid grid-cols-2 gap-4">
                <MetricCard value={faaResult.maxFlightTimeHours.toFixed(1)} label="Max Flight Time" unit="hours" variant="primary" />
                <MetricCard value={faaResult.maxFdpHours.toFixed(1)} label="Max FDP" unit="hours" variant="success" />
                <MetricCard value={faaResult.minRestHours.toFixed(0)} label="Min Rest" unit="hours" variant="warning" />
                <MetricCard value={faaResult.timeWindow} label="Time Window" variant="default" />
              </div>
            )}
            <div className="citation">Reference: 14 CFR Part 117, Tables A & B (unaugmented operations).</div>
          </div>
          <div className="glass-card p-6">
            <ScientificChart option={faaChart} title="FDP Limits by Segment Count"
              subtitle={`Report time: ${reportTime}${notAcclimated ? ' (not acclimated)' : ''}`} height={400}
              caption="Max FDP decreases with additional flight segments. Green ≥12h, Yellow ≥10h, Red <10h." />
          </div>
        </div>
      )}

      {/* EASA */}
      {selectedCalc === 'easa' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">🇪🇺 EASA ORO.FTL Duty Limits</h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-1">Report Time (local)</label>
                <input type="time" value={easaReportTime} onChange={e => setEasaReportTime(e.target.value)}
                  className="input-scientific" />
              </div>
              <SliderInput label="Flight Sectors" value={easaSectors} min={1} max={10} step={1} onChange={setEasaSectors} />
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 block mb-1">Acclimatisation State</label>
                <select value={easaState} onChange={e => setEasaState(e.target.value as typeof easaState)}
                  className="input-scientific">
                  <option value="acclimatised">Acclimatised</option>
                  <option value="unknown">Unknown</option>
                  <option value="unknown_frm">Unknown (under FRM)</option>
                </select>
              </div>
            </div>
            {easaResult && (
              <div className="grid grid-cols-2 gap-4">
                <MetricCard value={easaResult.maxDailyFdpHours.toFixed(1)} label="Max Daily FDP" unit="hours"
                  variant={easaResult.maxDailyFdpHours >= 12 ? 'success' : easaResult.maxDailyFdpHours >= 10 ? 'warning' : 'danger'} />
                <div className="info-box">
                  <strong>Source:</strong> {easaResult.sourceTable}
                </div>
              </div>
            )}
            <div className="info-box">
              <strong>EASA Cumulative Limits (ORO.FTL.210):</strong>
              <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                <span>7-day duty: ≤60h</span>
                <span>14-day duty: ≤110h</span>
                <span>28-day duty: ≤190h</span>
                <span>28-day flight: ≤100h</span>
                <span>Calendar year: ≤900h</span>
                <span>12 months: ≤1000h</span>
              </div>
            </div>
            <div className="citation">Reference: EASA Part-ORO Subpart FTL (Regulation (EU) No 965/2012).</div>
          </div>
          <div className="glass-card p-6">
            {(() => {
              const sectors = Array.from({ length: 10 }, (_, i) => i + 1);
              const fdps = sectors.map(s => {
                try { return easaMaxDailyFdp(easaReportTime, s, easaState).maxDailyFdpHours; }
                catch { return 0; }
              });
              const option = {
                tooltip: { trigger: 'axis' as const },
                grid: { left: 60, right: 30, top: 30, bottom: 50 },
                xAxis: {
                  type: 'category' as const, data: sectors.map(String),
                  name: 'Sectors', nameLocation: 'middle' as const, nameGap: 30,
                },
                yAxis: {
                  type: 'value' as const, name: 'Max FDP (hours)',
                  nameLocation: 'middle' as const, nameGap: 45, min: 8, max: 15,
                },
                series: [{
                  type: 'bar' as const,
                  data: fdps.map(v => ({
                    value: v,
                    itemStyle: { color: v >= 12 ? SCIENTIFIC_COLORS.success : v >= 10 ? SCIENTIFIC_COLORS.warning : SCIENTIFIC_COLORS.danger,
                      borderRadius: [4, 4, 0, 0] },
                  })),
                  barWidth: '45%',
                  label: { show: true, position: 'top' as const, formatter: '{c}h', fontSize: 10 },
                }],
              };
              return <ScientificChart option={option} title="EASA FDP vs Sectors"
                subtitle={`${easaState}, report: ${easaReportTime}`} height={400}
                caption="Maximum daily FDP based on sector count and acclimatisation state." />;
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default FatiguePage;
