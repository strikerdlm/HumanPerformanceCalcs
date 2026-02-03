import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { HomePage, AtmosphericPage, EnvironmentalPage } from './pages';
import type { CalculatorCategory } from './types';
import { Construction } from 'lucide-react';

// Placeholder component for sections under development
const ComingSoonPage: React.FC<{ title: string; description: string }> = ({ title, description }) => (
  <div className="animate-fade-in">
    <div className="glass-card p-8 text-center max-w-2xl mx-auto mt-12">
      <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-amber-400 to-orange-500 
        flex items-center justify-center text-white mb-6">
        <Construction className="w-10 h-10" />
      </div>
      <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-3">
        {title}
      </h2>
      <p className="text-slate-500 dark:text-slate-400 mb-6">
        {description}
      </p>
      <div className="badge badge-warning">Coming Soon</div>
    </div>
  </div>
);

const App: React.FC = () => {
  const [currentCategory, setCurrentCategory] = useState<CalculatorCategory>('home');

  const renderPage = () => {
    switch (currentCategory) {
      case 'home':
        return <HomePage onNavigate={setCurrentCategory} />;
      
      case 'atmospheric':
        return <AtmosphericPage />;
      
      case 'environmental':
        return <EnvironmentalPage />;
      
      case 'clinical':
        return (
          <ComingSoonPage 
            title="Clinical Calculators" 
            description="BMR (Mifflin-St Jeor), BSA formulas, eGFR (CKD-EPI), P/F ratio, Oxygen Index, 6MWD, Wells DVT/PE scores, A-a gradient, and oxygen delivery calculations."
          />
        );
      
      case 'fatigue':
        return (
          <ComingSoonPage 
            title="Fatigue & Circadian Calculators" 
            description="Mitler circadian performance model, Two-Process sleep model, jet lag recovery estimation, SAFTE effectiveness forecasting, and FAA Part 117 / EASA ORO.FTL duty time limit calculators."
          />
        );
      
      case 'simulation':
        return (
          <ComingSoonPage 
            title="Simulation Studio" 
            description="Forward trajectory simulation for time-steppable models including ISO 7933 PHS heat strain trajectories and Mitler circadian performance envelope forecasting."
          />
        );
      
      case 'visualization':
        return (
          <ComingSoonPage 
            title="Visualization Studio" 
            description="Custom 2D/3D scientific plots with multiple visualization themes. Export capabilities for PNG, SVG, PDF, and interactive HTML. Real-time parameter adjustment."
          />
        );
      
      case 'risk':
        return (
          <ComingSoonPage 
            title="Risk Assessment Tools" 
            description="Spatial Disorientation (SD) risk assessment, NVG/EO target acquisition (Johnson/ACQUIRE cycles), Whole-body vibration exposure (ISO 2631-1), Motion sickness susceptibility (MSSQ-short), and chemical risk dashboards."
          />
        );
      
      case 'occupational':
        return (
          <ComingSoonPage 
            title="Occupational Health & Safety" 
            description="Chemical exposure assessment (ACGIH TLV/BEI 2024), Time-weighted average calculator, mixed chemical exposure, unusual work schedule TLV adjustments, and comprehensive exposure reporting."
          />
        );
      
      default:
        return <HomePage onNavigate={setCurrentCategory} />;
    }
  };

  return (
    <Layout 
      currentCategory={currentCategory} 
      onCategoryChange={setCurrentCategory}
    >
      {renderPage()}
    </Layout>
  );
};

export default App;
