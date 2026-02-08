import React, { useState } from 'react';
import { Layout } from './components/Layout';
import {
  HomePage, AtmosphericPage, EnvironmentalPage,
  FatiguePage, SimulationPage, VisualizationPage, RiskAssessmentPage,
} from './pages';
import type { CalculatorCategory } from './types';

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
        return <HomePage onNavigate={setCurrentCategory} />;
      
      case 'fatigue':
        return <FatiguePage />;
      
      case 'simulation':
        return <SimulationPage />;
      
      case 'visualization':
        return <VisualizationPage />;
      
      case 'risk':
        return <RiskAssessmentPage />;
      
      case 'occupational':
        return <HomePage onNavigate={setCurrentCategory} />;
      
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
