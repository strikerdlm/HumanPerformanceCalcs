import React, { useState, useMemo } from 'react';
import { 
  standardAtmosphere, 
  alveolarPO2, 
  spo2Unacclimatized, 
  spo2Acclimatized,
  estimateTUC,
  gLocTime,
  cosmicDoseRate,
  amsProbability,
  tissueRatio,
  interpretTR,
  feetToMeters,
} from '../calculators';
import { ScientificChart, createLineChartOption } from '../components/charts/ScientificChart';
import { MetricCard, SliderInput } from '../components/ui';
import { SCIENTIFIC_COLORS } from '../types';

type CalculatorType = 
  | 'isa' 
  | 'pao2' 
  | 'hypoxia' 
  | 'ams' 
  | 'tuc' 
  | 'gforce' 
  | 'radiation'
  | 'decompression';

const calculatorOptions = [
  { id: 'isa', label: 'Standard Atmosphere (ISA)' },
  { id: 'pao2', label: 'Alveolar Oxygen Pressure (PAO₂)' },
  { id: 'hypoxia', label: 'SpO₂ vs Altitude' },
  { id: 'ams', label: 'Acute Mountain Sickness Risk' },
  { id: 'tuc', label: 'Time of Useful Consciousness' },
  { id: 'gforce', label: 'G-Force Tolerance' },
  { id: 'radiation', label: 'Cosmic Radiation Dose' },
  { id: 'decompression', label: 'Decompression Tissue Ratio' },
];

export const AtmosphericPage: React.FC = () => {
  const [selectedCalc, setSelectedCalc] = useState<CalculatorType>('isa');
  
  // ISA state
  const [isaAltitudeFt, setIsaAltitudeFt] = useState(35000);
  
  // PAO2 state
  const [pao2AltitudeFt, setPao2AltitudeFt] = useState(25000);
  const [pao2FiO2, setPao2FiO2] = useState(0.21);
  const [pao2PaCO2, setPao2PaCO2] = useState(40);
  const [pao2RQ, setPao2RQ] = useState(0.8);
  
  // Hypoxia state
  const [hypoxiaAltitudeFt, setHypoxiaAltitudeFt] = useState(15000);
  
  // AMS state
  const [amsAAE, setAmsAAE] = useState(2.5);
  
  // TUC state
  const [tucAltitudeFt, setTucAltitudeFt] = useState(35000);
  
  // G-force state
  const [gforceGz, setGforceGz] = useState(6.0);
  
  // Radiation state
  const [radAltitudeFt, setRadAltitudeFt] = useState(35000);
  const [radPolar, setRadPolar] = useState(false);
  const [radFlightHours, setRadFlightHours] = useState(500);
  
  // Decompression state
  const [decompAltitudeFt, setDecompAltitudeFt] = useState(25000);

  // ISA calculations
  const isaResult = useMemo(() => {
    try {
      return standardAtmosphere(feetToMeters(isaAltitudeFt));
    } catch {
      return null;
    }
  }, [isaAltitudeFt]);

  // ISA profile chart data
  const isaChartOption = useMemo(() => {
    const altitudes = Array.from({ length: 50 }, (_, i) => i * 400);
    const temps = altitudes.map(alt => {
      try {
        return standardAtmosphere(feetToMeters(alt)).temperature_C;
      } catch {
        return 0;
      }
    });
    
    return createLineChartOption(
      altitudes,
      [{ name: 'Temperature', data: temps, color: SCIENTIFIC_COLORS.primary, smooth: true }],
      { xAxisName: 'Altitude', xAxisUnit: 'ft', yAxisName: 'Temperature', yAxisUnit: '°C' }
    );
  }, []);

  // PAO2 calculation
  const pao2Result = useMemo(() => {
    try {
      return alveolarPO2(feetToMeters(pao2AltitudeFt), pao2FiO2, pao2PaCO2, pao2RQ);
    } catch {
      return null;
    }
  }, [pao2AltitudeFt, pao2FiO2, pao2PaCO2, pao2RQ]);

  // PAO2 chart
  const pao2ChartOption = useMemo(() => {
    const altitudes = Array.from({ length: 40 }, (_, i) => i * 1000);
    const values = altitudes.map(alt => {
      try {
        return alveolarPO2(feetToMeters(alt), pao2FiO2, pao2PaCO2, pao2RQ);
      } catch {
        return 0;
      }
    });
    
    return createLineChartOption(
      altitudes,
      [{ name: `PAO₂ (FiO₂=${pao2FiO2.toFixed(2)})`, data: values, color: SCIENTIFIC_COLORS.primary, smooth: true }],
      { 
        xAxisName: 'Altitude', xAxisUnit: 'ft', 
        yAxisName: 'PAO₂', yAxisUnit: 'mmHg',
        markLines: [{ value: 60, label: 'Hypoxic threshold', color: SCIENTIFIC_COLORS.danger }]
      }
    );
  }, [pao2FiO2, pao2PaCO2, pao2RQ]);

  // SpO2 chart
  const hypoxiaChartOption = useMemo(() => {
    const altitudes = Array.from({ length: 60 }, (_, i) => i * 100);
    const unaccl = altitudes.map(alt => spo2Unacclimatized(alt));
    const accl = altitudes.map(alt => spo2Acclimatized(alt));
    
    return createLineChartOption(
      altitudes,
      [
        { name: 'Unacclimatized', data: unaccl, color: SCIENTIFIC_COLORS.primary, smooth: true },
        { name: 'Acclimatized', data: accl, color: SCIENTIFIC_COLORS.success, smooth: true },
      ],
      { 
        xAxisName: 'Altitude', xAxisUnit: 'm', 
        yAxisName: 'SpO₂', yAxisUnit: '%',
        markLines: [
          { value: 90, label: 'Normal lower limit', color: SCIENTIFIC_COLORS.warning },
          { value: 80, label: 'Significant hypoxia', color: SCIENTIFIC_COLORS.danger },
        ]
      }
    );
  }, []);

  // AMS chart
  const amsChartOption = useMemo(() => {
    const aaeValues = Array.from({ length: 60 }, (_, i) => i * 0.1);
    const probs = aaeValues.map(aae => amsProbability(aae) * 100);
    
    return createLineChartOption(
      aaeValues,
      [{ name: 'AMS Probability', data: probs, color: SCIENTIFIC_COLORS.warning, smooth: true, areaStyle: true }],
      { 
        xAxisName: 'Accumulated Altitude Exposure', xAxisUnit: 'km·days', 
        yAxisName: 'Probability', yAxisUnit: '%',
        markLines: [{ value: 50, label: '50% threshold', color: SCIENTIFIC_COLORS.neutral }]
      }
    );
  }, []);

  // TUC chart
  const tucChartOption = useMemo(() => {
    const altitudes = Array.from({ length: 35 }, (_, i) => 18000 + i * 1000);
    const tucValues = altitudes.map(alt => {
      const tuc = estimateTUC(alt);
      return isFinite(tuc) ? tuc : 600;
    });
    
    return createLineChartOption(
      altitudes,
      [{ name: 'TUC', data: tucValues, color: SCIENTIFIC_COLORS.danger, smooth: true }],
      { 
        xAxisName: 'Altitude', xAxisUnit: 'ft', 
        yAxisName: 'Time of Useful Consciousness', yAxisUnit: 'sec',
        markLines: [{ value: 60, label: '1 minute', color: SCIENTIFIC_COLORS.warning }]
      }
    );
  }, []);

  // G-LOC chart
  const gforceChartOption = useMemo(() => {
    const gValues = Array.from({ length: 40 }, (_, i) => 5 + i * 0.1);
    const times = gValues.map(g => {
      const time = gLocTime(g);
      return isFinite(time) ? Math.min(time, 120) : 120;
    });
    
    return createLineChartOption(
      gValues,
      [{ name: 'Tolerance Time', data: times, color: SCIENTIFIC_COLORS.physiology, smooth: true }],
      { 
        xAxisName: '+Gz', xAxisUnit: 'g', 
        yAxisName: 'Estimated Tolerance', yAxisUnit: 'sec',
      }
    );
  }, []);

  // Current calculations
  const currentSpo2 = spo2Unacclimatized(feetToMeters(hypoxiaAltitudeFt));
  const currentAmsProb = amsProbability(amsAAE);
  const currentTuc = estimateTUC(tucAltitudeFt);
  const currentGloc = gLocTime(gforceGz);
  const currentRadDose = cosmicDoseRate(radAltitudeFt, radPolar);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
          Atmospheric & Physiological Calculators
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          ISA model, altitude physiology, hypoxia assessment, and G-force tolerance
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

      {/* ISA Calculator */}
      {selectedCalc === 'isa' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🌍 International Standard Atmosphere (ISA)
            </h2>
            
            <SliderInput
              label="Altitude"
              value={isaAltitudeFt}
              min={0}
              max={60000}
              step={1000}
              unit="ft"
              onChange={setIsaAltitudeFt}
              tooltip="ISA model valid 0-47km"
            />
            
            {isaResult && (
              <div className="grid grid-cols-2 gap-4">
                <MetricCard
                  value={isaResult.temperature_C.toFixed(1)}
                  label="Temperature"
                  unit="°C"
                  variant="primary"
                />
                <MetricCard
                  value={isaResult.pressure_hPa.toFixed(1)}
                  label="Pressure"
                  unit="hPa"
                  variant="primary"
                />
                <MetricCard
                  value={isaResult.density_kg_m3.toFixed(4)}
                  label="Density"
                  unit="kg/m³"
                  variant="default"
                />
                <MetricCard
                  value={isaResult.pO2_mmHg.toFixed(1)}
                  label="O₂ Partial Pressure"
                  unit="mmHg"
                  variant="success"
                />
              </div>
            )}
            
            <div className="citation">
              Reference: ISO 2533:1975. International Standard Atmosphere.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={isaChartOption}
              title="ISA Temperature Profile"
              subtitle="Temperature vs Altitude (0-20km)"
              height={400}
              caption="Fig. 1: International Standard Atmosphere temperature profile showing tropospheric lapse rate and stratospheric isothermal layer."
            />
          </div>
        </div>
      )}

      {/* PAO2 Calculator */}
      {selectedCalc === 'pao2' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🫁 Alveolar Oxygen Pressure (PAO₂)
            </h2>
            
            <div className="space-y-4">
              <SliderInput
                label="Altitude"
                value={pao2AltitudeFt}
                min={0}
                max={40000}
                step={1000}
                unit="ft"
                onChange={setPao2AltitudeFt}
              />
              
              <SliderInput
                label="Inspired O₂ Fraction (FiO₂)"
                value={pao2FiO2}
                min={0.1}
                max={1.0}
                step={0.01}
                onChange={setPao2FiO2}
                formatValue={(v) => v.toFixed(2)}
              />
              
              <SliderInput
                label="Arterial CO₂ (PaCO₂)"
                value={pao2PaCO2}
                min={20}
                max={60}
                step={1}
                unit="mmHg"
                onChange={setPao2PaCO2}
              />
              
              <SliderInput
                label="Respiratory Quotient (RQ)"
                value={pao2RQ}
                min={0.5}
                max={1.2}
                step={0.05}
                onChange={setPao2RQ}
                formatValue={(v) => v.toFixed(2)}
              />
            </div>
            
            {pao2Result !== null && (
              <div className="grid grid-cols-2 gap-4">
                <MetricCard
                  value={pao2Result.toFixed(1)}
                  label="Alveolar PAO₂"
                  unit="mmHg"
                  variant={pao2Result < 60 ? 'danger' : pao2Result < 80 ? 'warning' : 'success'}
                />
                <div className={`info-box ${pao2Result < 60 ? 'danger-box' : pao2Result < 80 ? 'warning-box' : ''}`}>
                  <strong>Assessment:</strong>{' '}
                  {pao2Result < 60 ? 'Severe hypoxia' : pao2Result < 80 ? 'Mild hypoxia' : 'Normal range'}
                </div>
              </div>
            )}
            
            <div className="info-box">
              <strong>Formula:</strong> PAO₂ = FiO₂ × (Pb − PH₂O) − PaCO₂/RQ
            </div>
            
            <div className="citation">
              Reference: West, J.B. (2011). Respiratory Physiology: The Essentials (9th ed.)
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={pao2ChartOption}
              title="Alveolar Oxygen vs Altitude"
              height={400}
              caption="Fig. 2: Alveolar oxygen partial pressure decreases with altitude due to reduced barometric pressure."
            />
          </div>
        </div>
      )}

      {/* SpO2/Hypoxia Calculator */}
      {selectedCalc === 'hypoxia' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🏔️ SpO₂ at Altitude
            </h2>
            
            <SliderInput
              label="Altitude"
              value={hypoxiaAltitudeFt}
              min={0}
              max={30000}
              step={500}
              unit="ft"
              onChange={setHypoxiaAltitudeFt}
            />
            
            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                value={spo2Unacclimatized(feetToMeters(hypoxiaAltitudeFt)).toFixed(1)}
                label="SpO₂ (Unacclimatized)"
                unit="%"
                variant={currentSpo2 < 80 ? 'danger' : currentSpo2 < 90 ? 'warning' : 'success'}
              />
              <MetricCard
                value={spo2Acclimatized(feetToMeters(hypoxiaAltitudeFt)).toFixed(1)}
                label="SpO₂ (Acclimatized)"
                unit="%"
                variant="primary"
              />
            </div>
            
            <div className="citation">
              Reference: West, J.B. & Schoene, R.B. (2001). High Altitude Medicine and Physiology.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={hypoxiaChartOption}
              title="Oxygen Saturation vs Altitude"
              height={400}
              caption="Fig. 3: SpO₂ decline with altitude for acclimatized and unacclimatized individuals. Yellow line: normal lower limit (90%), red line: significant hypoxia (80%)."
            />
          </div>
        </div>
      )}

      {/* AMS Calculator */}
      {selectedCalc === 'ams' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🩺 Acute Mountain Sickness Risk
            </h2>
            
            <SliderInput
              label="Accumulated Altitude Exposure (AAE)"
              value={amsAAE}
              min={0}
              max={6}
              step={0.1}
              unit="km·days"
              onChange={setAmsAAE}
              tooltip="AAE = (altitude in km) × (days at altitude)"
            />
            
            <MetricCard
              value={(currentAmsProb * 100).toFixed(1)}
              label="AMS Probability"
              unit="%"
              variant={currentAmsProb > 0.5 ? 'danger' : currentAmsProb > 0.2 ? 'warning' : 'success'}
            />
            
            <div className={`${currentAmsProb > 0.5 ? 'danger-box' : currentAmsProb > 0.2 ? 'warning-box' : 'success-box'}`}>
              <strong>Risk Level:</strong>{' '}
              {currentAmsProb < 0.2 ? 'Low' : currentAmsProb < 0.5 ? 'Moderate' : 'High'}
            </div>
            
            <div className="citation">
              Reference: Roach, R.C. et al. (1993). Lake Louise AMS Scoring System.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={amsChartOption}
              title="AMS Probability vs Altitude Exposure"
              height={400}
              caption="Fig. 4: Probability of developing Acute Mountain Sickness based on accumulated altitude exposure (AAE = altitude × duration)."
            />
          </div>
        </div>
      )}

      {/* TUC Calculator */}
      {selectedCalc === 'tuc' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              ⏱️ Time of Useful Consciousness (TUC)
            </h2>
            
            <SliderInput
              label="Altitude"
              value={tucAltitudeFt}
              min={18000}
              max={50000}
              step={1000}
              unit="ft"
              onChange={setTucAltitudeFt}
            />
            
            <MetricCard
              value={isFinite(currentTuc) ? currentTuc.toFixed(0) : '∞'}
              label="Estimated TUC"
              unit="sec"
              variant={currentTuc < 60 ? 'danger' : currentTuc < 180 ? 'warning' : 'success'}
              delta={isFinite(currentTuc) ? `~${(currentTuc / 60).toFixed(1)} min` : undefined}
            />
            
            <div className={`${currentTuc < 60 ? 'danger-box' : currentTuc < 180 ? 'warning-box' : 'info-box'}`}>
              {currentTuc < 60 
                ? 'Extremely limited time - immediate action required'
                : currentTuc < 180 
                  ? 'Very limited time available'
                  : 'Sufficient time for emergency procedures'}
            </div>
            
            <div className="citation">
              Reference: Ernsting, J. & Nicholson, A.N. (2016). Aviation Medicine (4th ed.)
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={tucChartOption}
              title="Time of Useful Consciousness vs Altitude"
              height={400}
              caption="Fig. 5: TUC decreases rapidly above FL250. Values interpolated from USAF reference data."
            />
          </div>
        </div>
      )}

      {/* G-Force Calculator */}
      {selectedCalc === 'gforce' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🎯 G-Force Tolerance
            </h2>
            
            <SliderInput
              label="Sustained +Gz"
              value={gforceGz}
              min={1}
              max={9}
              step={0.1}
              unit="g"
              onChange={setGforceGz}
            />
            
            <MetricCard
              value={isFinite(currentGloc) ? currentGloc.toFixed(0) : '∞'}
              label="Estimated Tolerance Time"
              unit="sec"
              variant={currentGloc < 15 ? 'danger' : currentGloc < 60 ? 'warning' : 'success'}
            />
            
            <div className={`${currentGloc < 15 ? 'danger-box' : currentGloc < 60 ? 'warning-box' : 'info-box'}`}>
              {gforceGz < 5 
                ? 'Below ~5g, most subjects tolerate indefinitely'
                : currentGloc < 15 
                  ? 'Very short tolerance - high G-LOC risk'
                  : currentGloc < 60 
                    ? 'Limited tolerance time'
                    : 'Reasonable tolerance time (with straining maneuvers)'}
            </div>
            
            <div className="citation">
              Reference: Whinnery, J.E. & Forster, E.M. (2006). Aviation, Space, and Environmental Medicine.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <ScientificChart
              option={gforceChartOption}
              title="G-Force Tolerance Time"
              height={400}
              caption="Fig. 6: Estimated tolerance time decreases exponentially above +5Gz. Simplified Stoll curve approximation."
            />
          </div>
        </div>
      )}

      {/* Radiation Calculator */}
      {selectedCalc === 'radiation' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              ☢️ Cosmic Radiation Dose
            </h2>
            
            <SliderInput
              label="Flight Altitude"
              value={radAltitudeFt}
              min={0}
              max={45000}
              step={1000}
              unit="ft"
              onChange={setRadAltitudeFt}
            />
            
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="polar"
                checked={radPolar}
                onChange={(e) => setRadPolar(e.target.checked)}
                className="w-4 h-4 rounded"
              />
              <label htmlFor="polar" className="text-sm text-slate-700 dark:text-slate-300">
                Polar route (&gt;60° latitude) - Higher exposure
              </label>
            </div>
            
            <SliderInput
              label="Annual Flight Hours"
              value={radFlightHours}
              min={0}
              max={1200}
              step={50}
              unit="hours"
              onChange={setRadFlightHours}
            />
            
            <div className="grid grid-cols-2 gap-4">
              <MetricCard
                value={currentRadDose.toFixed(2)}
                label="Dose Rate"
                unit="µSv/h"
                variant="primary"
              />
              <MetricCard
                value={(currentRadDose * radFlightHours).toFixed(0)}
                label="Annual Dose"
                unit="µSv/yr"
                variant={(currentRadDose * radFlightHours) > 1000 ? 'danger' : 'success'}
              />
            </div>
            
            <div className={(currentRadDose * radFlightHours) > 1000 ? 'warning-box' : 'info-box'}>
              {(currentRadDose * radFlightHours) > 1000 
                ? 'Above 1 mSv/year public exposure guideline'
                : 'Within public exposure guidelines'}
            </div>
            
            <div className="citation">
              Reference: Friedberg, W. et al. (1992). Radiation Protection Dosimetry.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <div className="h-[400px] flex items-center justify-center text-slate-500">
              Radiation profile chart would show dose rate vs altitude for polar and non-polar routes
            </div>
          </div>
        </div>
      )}

      {/* Decompression Calculator */}
      {selectedCalc === 'decompression' && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-6">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              🫧 Decompression Tissue Ratio
            </h2>
            
            <SliderInput
              label="Altitude"
              value={decompAltitudeFt}
              min={0}
              max={40000}
              step={1000}
              unit="ft"
              onChange={setDecompAltitudeFt}
            />
            
            {(() => {
              const isa = standardAtmosphere(feetToMeters(decompAltitudeFt));
              const seaLevelN2 = 0.78 * 760;
              const tr = tissueRatio(seaLevelN2, isa.pressure_mmHg);
              const interpretation = interpretTR(tr);
              
              return (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <MetricCard
                      value={isa.pressure_mmHg.toFixed(1)}
                      label="Ambient Pressure"
                      unit="mmHg"
                      variant="default"
                    />
                    <MetricCard
                      value={tr.toFixed(2)}
                      label="Tissue Ratio"
                      variant={tr > 2.0 ? 'danger' : tr > 1.7 ? 'warning' : 'success'}
                    />
                  </div>
                  
                  <div className={`${tr > 2.0 ? 'danger-box' : tr > 1.7 ? 'warning-box' : 'info-box'}`}>
                    <strong>DCS Risk Assessment:</strong> {interpretation}
                  </div>
                </>
              );
            })()}
            
            <div className="info-box">
              Assumes tissues saturated at sea-level N₂ partial pressure prior to ascent.
            </div>
          </div>
          
          <div className="glass-card p-6">
            <div className="h-[400px] flex items-center justify-center text-slate-500">
              Tissue Ratio vs Altitude chart
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AtmosphericPage;
