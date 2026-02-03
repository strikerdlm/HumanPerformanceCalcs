import React, { useState, useMemo } from 'react';
import { 
  wbgtOutdoor,
  wbgtRiskAssessment,
  heatStressIndex,
  hsiAssessment,
  predictedHeatStrain,
  utci,
  simulatePHSTrajectory,
} from '../calculators';
import { ScientificChart, createGaugeChartOption } from '../components/charts/ScientificChart';
import { MetricCard, SliderInput } from '../components/ui';
import { SCIENTIFIC_COLORS } from '../types';

type CalculatorType = 'wbgt' | 'hsi' | 'phs' | 'utci';

const calculatorOptions = [
  { id: 'wbgt', label: 'WBGT (ISO 7243)' },
  { id: 'hsi', label: 'Heat Stress Index' },
  { id: 'phs', label: 'Predicted Heat Strain (ISO 7933)' },
  { id: 'utci', label: 'UTCI Thermal Index' },
];

export const EnvironmentalPage: React.FC = () => {
  const [selectedCalc, setSelectedCalc] = useState<CalculatorType>('phs');

  // WBGT state
  const [wbgtDryBulb, setWbgtDryBulb] = useState(32);
  const [wbgtGlobe, setWbgtGlobe] = useState(45);
  const [wbgtRH, setWbgtRH] = useState(65);

  // HSI state
  const [hsiMetabolic, setHsiMetabolic] = useState(300);
  const [hsiTemp, setHsiTemp] = useState(32);
  const [hsiRH, setHsiRH] = useState(60);
  const [hsiWind, setHsiWind] = useState(0.5);

  // PHS state
  const [phsMetabolic, setPhsMetabolic] = useState(380);
  const [phsAirTemp, setPhsAirTemp] = useState(32);
  const [phsRadiant, setPhsRadiant] = useState(38);
  const [phsRH, setPhsRH] = useState(55);
  const [phsWind, setPhsWind] = useState(0.6);
  const [phsClo, setPhsClo] = useState(0.9);
  const [phsDuration, setPhsDuration] = useState(120);
  const [phsBodyMass, setPhsBodyMass] = useState(75);
  const [phsCoreLimit, setPhsCoreLimit] = useState(38.5);
  const [phsDehydLimit, setPhsDehydLimit] = useState(5);

  // UTCI state
  const [utciAirTemp, setUtciAirTemp] = useState(25);
  const [utciRadiant, setUtciRadiant] = useState(30);
  const [utciWind, setUtciWind] = useState(2);
  const [utciRH, setUtciRH] = useState(50);

  // WBGT calculation
  const wbgtResult = useMemo(() => {
    const wbgt = wbgtOutdoor(null, wbgtGlobe, wbgtDryBulb, wbgtRH);
    return wbgtRiskAssessment(wbgt);
  }, [wbgtDryBulb, wbgtGlobe, wbgtRH]);

  // HSI calculation
  const hsiResult = useMemo(() => {
    const hsi = heatStressIndex(hsiMetabolic, hsiTemp, hsiRH, hsiWind);
    return hsiAssessment(hsi);
  }, [hsiMetabolic, hsiTemp, hsiRH, hsiWind]);

  // PHS calculation
  const phsResult = useMemo(() => {
    return predictedHeatStrain(
      phsMetabolic,
      phsAirTemp,
      phsRadiant,
      phsRH,
      phsWind,
      phsClo,
      phsDuration,
      0, // mechanical power
      phsBodyMass,
      1.9, // BSA
      37.0, // baseline core
      phsCoreLimit,
      phsDehydLimit
    );
  }, [phsMetabolic, phsAirTemp, phsRadiant, phsRH, phsWind, phsClo, phsDuration, phsBodyMass, phsCoreLimit, phsDehydLimit]);

  // PHS Trajectory
  const phsTrajectory = useMemo(() => {
    return simulatePHSTrajectory(
      [phsMetabolic, phsAirTemp, phsRadiant, phsRH, phsWind, phsClo, phsDuration, 0, phsBodyMass, 1.9, 37.0, phsCoreLimit, phsDehydLimit],
      5
    );
  }, [phsMetabolic, phsAirTemp, phsRadiant, phsRH, phsWind, phsClo, phsDuration, phsBodyMass, phsCoreLimit, phsDehydLimit]);

  // PHS Chart
  const phsChartOption = useMemo(() => {
    const times = phsTrajectory.map(p => p.time_min);
    const coreTemps = phsTrajectory.map(p => p.coreTemp_C);
    const dehydration = phsTrajectory.map(p => p.dehydration_percent);

    return {
      tooltip: { trigger: 'axis' as const },
      legend: { top: 5 },
      grid: { left: 60, right: 60, top: 50, bottom: 50 },
      xAxis: {
        type: 'value' as const,
        name: 'Time (min)',
        nameLocation: 'middle' as const,
        nameGap: 30,
      },
      yAxis: [
        {
          type: 'value' as const,
          name: 'Core Temp (°C)',
          position: 'left' as const,
          min: 36.5,
          max: 40,
        },
        {
          type: 'value' as const,
          name: 'Dehydration (%)',
          position: 'right' as const,
          min: 0,
          max: Math.max(10, phsDehydLimit * 1.5),
        },
      ],
      series: [
        {
          name: 'Core Temperature',
          type: 'line' as const,
          data: times.map((t, i) => [t, coreTemps[i]]),
          smooth: true,
          lineStyle: { width: 3, color: SCIENTIFIC_COLORS.danger },
          itemStyle: { color: SCIENTIFIC_COLORS.danger },
          markLine: {
            symbol: 'none',
            data: [{ yAxis: phsCoreLimit, label: { formatter: 'Core Limit' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.danger } }],
          },
        },
        {
          name: 'Dehydration',
          type: 'line' as const,
          yAxisIndex: 1,
          data: times.map((t, i) => [t, dehydration[i]]),
          smooth: true,
          lineStyle: { width: 3, color: SCIENTIFIC_COLORS.warning },
          itemStyle: { color: SCIENTIFIC_COLORS.warning },
          areaStyle: {
            color: {
              type: 'linear' as const,
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: `${SCIENTIFIC_COLORS.warning}40` },
                { offset: 1, color: `${SCIENTIFIC_COLORS.warning}05` },
              ],
            },
          },
          markLine: {
            symbol: 'none',
            data: [{ yAxis: phsDehydLimit, label: { formatter: 'Dehydration Limit' }, lineStyle: { type: 'dashed' as const, color: SCIENTIFIC_COLORS.warning } }],
          },
        },
      ],
    };
  }, [phsTrajectory, phsCoreLimit, phsDehydLimit]);

  // UTCI calculation
  const utciResult = useMemo(() => {
    return utci(utciAirTemp, utciRadiant, utciWind, utciRH);
  }, [utciAirTemp, utciRadiant, utciWind, utciRH]);

  // WBGT gauge
  const wbgtGaugeOption = useMemo(() => 
    createGaugeChartOption(wbgtResult.wbgt, {
      min: 15,
      max: 40,
      title: 'WBGT',
      unit: '°C',
      thresholds: [
        { value: 0.35, color: SCIENTIFIC_COLORS.success },
        { value: 0.55, color: SCIENTIFIC_COLORS.warning },
        { value: 0.75, color: '#f97316' },
        { value: 1, color: SCIENTIFIC_COLORS.danger },
      ],
    }), [wbgtResult.wbgt]);

  // HSI gauge
  const hsiGaugeOption = useMemo(() =>
    createGaugeChartOption(hsiResult.hsi, {
      min: 0,
      max: 100,
      title: 'HSI',
      unit: '%',
      thresholds: [
        { value: 0.2, color: SCIENTIFIC_COLORS.success },
        { value: 0.4, color: '#84cc16' },
        { value: 0.7, color: SCIENTIFIC_COLORS.warning },
        { value: 1, color: SCIENTIFIC_COLORS.danger },
      ],
    }), [hsiResult.hsi]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
          Environmental Monitoring
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Heat stress assessment, thermal comfort indices, and exposure limits
        </p>
      </div>

      {/* Calculator selector */}
      <div className="flex flex-wrap gap-2">
        {calculatorOptions.map((opt) => (
          <button
            key={opt.id}
            onClick={() => setSelectedCalc(opt.id as CalculatorType)}
            className={`tab-item ${selectedCalc === opt.id ? 'active' : ''}`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* PHS Calculator - Featured */}
      {selectedCalc === 'phs' && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">
              ♨️ Predicted Heat Strain (ISO 7933 inspired)
            </h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium text-slate-700 dark:text-slate-300">Work Parameters</h3>
                <SliderInput label="Metabolic Rate" value={phsMetabolic} min={150} max={650} step={10} unit="W/m²" onChange={setPhsMetabolic} />
                <SliderInput label="Clothing Insulation" value={phsClo} min={0.3} max={1.6} step={0.1} unit="clo" onChange={setPhsClo} />
                <SliderInput label="Exposure Duration" value={phsDuration} min={15} max={480} step={15} unit="min" onChange={setPhsDuration} />
              </div>
              
              <div className="space-y-4">
                <h3 className="font-medium text-slate-700 dark:text-slate-300">Environment</h3>
                <SliderInput label="Air Temperature" value={phsAirTemp} min={20} max={50} step={0.5} unit="°C" onChange={setPhsAirTemp} />
                <SliderInput label="Mean Radiant Temp" value={phsRadiant} min={20} max={60} step={0.5} unit="°C" onChange={setPhsRadiant} />
                <SliderInput label="Relative Humidity" value={phsRH} min={10} max={100} step={5} unit="%" onChange={setPhsRH} />
                <SliderInput label="Air Velocity" value={phsWind} min={0.1} max={3} step={0.1} unit="m/s" onChange={setPhsWind} />
              </div>
              
              <div className="space-y-4">
                <h3 className="font-medium text-slate-700 dark:text-slate-300">Physiology Limits</h3>
                <SliderInput label="Body Mass" value={phsBodyMass} min={50} max={120} step={1} unit="kg" onChange={setPhsBodyMass} />
                <SliderInput label="Core Temp Limit" value={phsCoreLimit} min={37.5} max={39.5} step={0.1} unit="°C" onChange={setPhsCoreLimit} />
                <SliderInput label="Dehydration Limit" value={phsDehydLimit} min={2} max={7} step={0.5} unit="%" onChange={setPhsDehydLimit} />
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="grid md:grid-cols-4 gap-4">
            <MetricCard
              value={phsResult.predictedCoreTemp_C.toFixed(2)}
              label="Predicted Core Temp"
              unit="°C"
              variant={phsResult.predictedCoreTemp_C > phsCoreLimit ? 'danger' : 'primary'}
              delta={`+${(phsResult.predictedCoreTemp_C - 37).toFixed(2)} °C from baseline`}
            />
            <MetricCard
              value={phsResult.requiredSweatRate_L_h.toFixed(2)}
              label="Required Sweat Rate"
              unit="L/h"
              variant="warning"
            />
            <MetricCard
              value={phsResult.dehydrationPercent.toFixed(1)}
              label="Predicted Dehydration"
              unit="% body mass"
              variant={phsResult.dehydrationPercent > phsDehydLimit ? 'danger' : 'warning'}
            />
            <MetricCard
              value={phsResult.allowableExposure_min.toFixed(0)}
              label="Allowable Exposure"
              unit="min"
              variant={phsResult.allowableExposure_min < phsDuration ? 'danger' : 'success'}
              delta={phsResult.limitingFactor}
            />
          </div>

          {/* Trajectory Chart */}
          <div className="glass-card p-6">
            <ScientificChart
              option={phsChartOption}
              title="Heat Strain Trajectory"
              subtitle={`Metabolic rate: ${phsMetabolic} W/m², Environment: ${phsAirTemp}°C/${phsRH}% RH`}
              height={450}
              caption="Fig. 1: Predicted core temperature and dehydration over exposure duration. Dashed lines indicate physiological limits. Model inspired by ISO 7933:2023."
            />
          </div>

          {/* Interpretation */}
          <div className={phsResult.allowableExposure_min < phsDuration ? 'danger-box' : 'info-box'}>
            <strong>Interpretation:</strong>{' '}
            {phsResult.limitingFactor === 'None'
              ? 'Exposure within physiological limits for the planned duration.'
              : phsResult.limitingFactor === 'Core temperature limit'
                ? `Core temperature limit (${phsCoreLimit}°C) will be reached before planned duration. Reduce exposure or improve cooling.`
                : `Dehydration limit (${phsDehydLimit}%) will be reached. Ensure adequate hydration or reduce exposure time.`}
          </div>

          <div className="citation">
            Reference: ISO 7933:2023. Ergonomics of the thermal environment — Analytical determination and interpretation of heat stress using calculation of the predicted heat strain.
          </div>
        </div>
      )}

      {/* WBGT Calculator */}
      {selectedCalc === 'wbgt' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🌡️ Wet Bulb Globe Temperature (WBGT)
            </h2>
            
            <div className="space-y-4">
              <SliderInput label="Dry Bulb Temperature" value={wbgtDryBulb} min={15} max={50} step={0.5} unit="°C" onChange={setWbgtDryBulb} />
              <SliderInput label="Globe Temperature" value={wbgtGlobe} min={15} max={70} step={0.5} unit="°C" onChange={setWbgtGlobe} />
              <SliderInput label="Relative Humidity" value={wbgtRH} min={0} max={100} step={5} unit="%" onChange={setWbgtRH} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                value={wbgtResult.wbgt.toFixed(1)}
                label="WBGT Index"
                unit="°C"
                variant={wbgtResult.riskCategory === 'Extreme' ? 'danger' : wbgtResult.riskCategory === 'High' ? 'warning' : 'success'}
              />
              <div className={`${wbgtResult.riskCategory === 'Extreme' || wbgtResult.riskCategory === 'High' ? 'danger-box' : wbgtResult.riskCategory === 'Moderate' ? 'warning-box' : 'success-box'} flex items-center`}>
                <div>
                  <strong>Risk: {wbgtResult.riskCategory}</strong>
                  <p className="text-sm mt-1">{wbgtResult.recommendation}</p>
                </div>
              </div>
            </div>

            <div className="citation">
              Reference: ISO 7243:2017. Hot environments — Estimation of the heat stress on working man, based on the WBGT-index.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={wbgtGaugeOption}
              height={350}
              title="WBGT Heat Stress Gauge"
              caption="Fig. 2: WBGT index with risk zones: Green (<28°C), Yellow (28-30°C), Orange (30-32°C), Red (>32°C)."
            />
          </div>
        </div>
      )}

      {/* HSI Calculator */}
      {selectedCalc === 'hsi' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🔥 Heat Stress Index (HSI)
            </h2>
            
            <div className="space-y-4">
              <SliderInput label="Metabolic Rate" value={hsiMetabolic} min={100} max={600} step={25} unit="W/m²" onChange={setHsiMetabolic} />
              <SliderInput label="Air Temperature" value={hsiTemp} min={15} max={50} step={0.5} unit="°C" onChange={setHsiTemp} />
              <SliderInput label="Relative Humidity" value={hsiRH} min={0} max={100} step={5} unit="%" onChange={setHsiRH} />
              <SliderInput label="Air Velocity" value={hsiWind} min={0} max={5} step={0.1} unit="m/s" onChange={setHsiWind} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                value={hsiResult.hsi.toFixed(1)}
                label="Heat Stress Index"
                unit="%"
                variant={hsiResult.hsi >= 100 ? 'danger' : hsiResult.hsi >= 70 ? 'warning' : 'success'}
              />
              <div className={`${hsiResult.hsi >= 100 ? 'danger-box' : hsiResult.hsi >= 40 ? 'warning-box' : 'success-box'}`}>
                <strong>{hsiResult.category}</strong>
                <p className="text-sm mt-1">{hsiResult.recommendation}</p>
              </div>
            </div>

            <div className="citation">
              Reference: Belding, H.S. & Hatch, T.F. (1955). Index for evaluating heat stress. Heating, Piping and Air Conditioning.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={hsiGaugeOption}
              height={350}
              title="Heat Stress Index Gauge"
              caption="Fig. 3: HSI percentage. Values >100% indicate uncompensable heat stress where the body cannot maintain thermal balance."
            />
          </div>
        </div>
      )}

      {/* UTCI Calculator */}
      {selectedCalc === 'utci' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🧊 Universal Thermal Climate Index (UTCI)
            </h2>
            
            <div className="space-y-4">
              <SliderInput label="Air Temperature" value={utciAirTemp} min={-30} max={50} step={1} unit="°C" onChange={setUtciAirTemp} />
              <SliderInput label="Mean Radiant Temperature" value={utciRadiant} min={-30} max={70} step={1} unit="°C" onChange={setUtciRadiant} />
              <SliderInput label="Wind Speed (10m)" value={utciWind} min={0.5} max={17} step={0.5} unit="m/s" onChange={setUtciWind} />
              <SliderInput label="Relative Humidity" value={utciRH} min={0} max={100} step={5} unit="%" onChange={setUtciRH} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                value={utciResult.utci_C.toFixed(1)}
                label="UTCI 'Feels Like'"
                unit="°C"
                variant={utciResult.stressLevel > 2 ? 'danger' : utciResult.stressLevel < -2 ? 'primary' : 'success'}
              />
              <div className={`${Math.abs(utciResult.stressLevel) > 2 ? 'warning-box' : 'info-box'}`}>
                <strong>{utciResult.category}</strong>
                <p className="text-sm mt-1">Stress level: {utciResult.stressLevel > 0 ? '+' : ''}{utciResult.stressLevel}/4</p>
              </div>
            </div>

            <div className="info-box">
              <strong>UTCI Categories:</strong>
              <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                <span>&gt;46°C: Extreme heat stress</span>
                <span>38-46°C: Very strong heat stress</span>
                <span>32-38°C: Strong heat stress</span>
                <span>26-32°C: Moderate heat stress</span>
                <span>9-26°C: No thermal stress</span>
                <span>&lt;9°C: Cold stress categories</span>
              </div>
            </div>

            <div className="citation">
              Reference: Bröde, P. et al. (2012). Deriving the operational procedure for the Universal Thermal Climate Index (UTCI). Int J Biometeorol.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <div className="h-[400px] flex items-center justify-center text-slate-500">
              UTCI thermal comfort scale visualization
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnvironmentalPage;
