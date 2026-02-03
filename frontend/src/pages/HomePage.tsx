import React from 'react';
import { 
  Activity, Thermometer, Heart, Brain, 
  AlertTriangle, 
  ArrowRight, Zap, Shield, Globe
} from 'lucide-react';
import { MetricCard } from '../components/ui';
import type { CalculatorCategory } from '../types';

interface HomePageProps {
  onNavigate: (category: CalculatorCategory) => void;
}

const featureCards = [
  {
    icon: Activity,
    title: 'Atmospheric Physiology',
    description: 'ISA model, hypoxia cascade, TUC, G-force tolerance, and decompression assessment',
    stats: '9+ calculators',
    color: 'from-blue-500 to-cyan-500',
    category: 'atmospheric' as CalculatorCategory,
  },
  {
    icon: Thermometer,
    title: 'Environmental Monitoring',
    description: 'WBGT, UTCI, ISO 7933 PHS, cold water survival, and noise exposure',
    stats: '7+ calculators',
    color: 'from-emerald-500 to-green-500',
    category: 'environmental' as CalculatorCategory,
  },
  {
    icon: Heart,
    title: 'Clinical Calculators',
    description: 'BMR, BSA, eGFR, Wells scores, A-a gradient, and oxygen delivery',
    stats: '8+ calculators',
    color: 'from-violet-500 to-purple-500',
    category: 'clinical' as CalculatorCategory,
  },
  {
    icon: Brain,
    title: 'Fatigue & Circadian',
    description: 'Mitler performance, SAFTE forecasting, FAA/EASA duty limits',
    stats: '6+ calculators',
    color: 'from-pink-500 to-rose-500',
    category: 'fatigue' as CalculatorCategory,
  },
];

const roadmapItems = [
  { name: 'ISO 7933 Predicted Heat Strain', status: 'Live' },
  { name: 'Bühlmann ZH-L16 Decompression', status: 'Live' },
  { name: 'AGSM Effectiveness Model', status: 'Live' },
  { name: 'Spatial Disorientation Risk', status: 'Live' },
];

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 p-8 text-white">
        <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='30' height='30' viewBox='0 0 30 30' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M15 0v30M0 15h30' stroke='%23fff' stroke-width='.5' opacity='.1'/%3E%3C/svg%3E\")" }} />
        
        <div className="relative z-10 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 text-sm mb-4">
              <Zap className="w-4 h-4" />
              <span>Publication-Ready Visualizations</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Aerospace Medicine & Human Performance
            </h1>
            
            <p className="text-lg text-white/90 mb-6">
              Research-grade computational tools for extreme environment medicine. 
              29+ scientifically validated calculators with interactive dashboards 
              and publication-quality exports.
            </p>
            
            <div className="flex flex-wrap gap-3">
              <button 
                onClick={() => onNavigate('atmospheric')}
                className="btn-primary bg-white text-primary-600 hover:bg-white/90"
              >
                Explore Calculators
                <ArrowRight className="w-4 h-4 ml-2 inline" />
              </button>
              <button 
                onClick={() => onNavigate('simulation')}
                className="btn-secondary bg-white/10 border-white/30 text-white hover:bg-white/20"
              >
                Simulation Studio
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card bg-white/10 backdrop-blur-md p-4 text-center">
              <div className="text-4xl font-bold">29+</div>
              <div className="text-sm text-white/80">Referenced Formulas</div>
            </div>
            <div className="glass-card bg-white/10 backdrop-blur-md p-4 text-center">
              <div className="text-4xl font-bold">Q1</div>
              <div className="text-sm text-white/80">Journal Ready</div>
            </div>
            <div className="glass-card bg-white/10 backdrop-blur-md p-4 text-center">
              <div className="text-4xl font-bold">ISO</div>
              <div className="text-sm text-white/80">Standards Based</div>
            </div>
            <div className="glass-card bg-white/10 backdrop-blur-md p-4 text-center">
              <div className="text-4xl font-bold">ACGIH</div>
              <div className="text-sm text-white/80">TLV® 2024</div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section>
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6">
          Calculator Categories
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {featureCards.map((card) => (
            <button
              key={card.category}
              onClick={() => onNavigate(card.category)}
              className="glass-card p-6 text-left group"
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} 
                flex items-center justify-center text-white mb-4
                group-hover:scale-110 transition-transform`}>
                <card.icon className="w-6 h-6" />
              </div>
              
              <h3 className="font-semibold text-slate-800 dark:text-white mb-2">
                {card.title}
              </h3>
              
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                {card.description}
              </p>
              
              <div className="flex items-center justify-between">
                <span className="badge badge-info">{card.stats}</span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-primary-500 
                  group-hover:translate-x-1 transition-all" />
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* Quick Stats */}
      <section className="grid md:grid-cols-4 gap-4">
        <MetricCard 
          value="29+"
          label="Calculators"
          variant="primary"
        />
        <MetricCard 
          value="ISO 7933"
          label="Heat Strain Model"
          variant="success"
        />
        <MetricCard 
          value="ACGIH"
          label="TLV/BEI 2024"
          variant="warning"
        />
        <MetricCard 
          value="100%"
          label="Open Source"
          variant="primary"
        />
      </section>

      {/* Roadmap */}
      <section className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-800 dark:text-white">
            Roadmap Progress
          </h2>
          <span className="badge badge-success">Phase 1 Complete</span>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {roadmapItems.map((item, i) => (
            <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50">
              <div className="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center">
                <Shield className="w-4 h-4 text-success-600" />
              </div>
              <div>
                <div className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  {item.name}
                </div>
                <div className="text-xs text-success-600">{item.status}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Scientific Foundation */}
      <section className="grid md:grid-cols-2 gap-6">
        <div className="info-box">
          <h3 className="font-semibold text-slate-800 dark:text-white mb-3 flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary-500" />
            Scientific Foundation
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
            All calculators are based on peer-reviewed scientific literature and 
            established international standards including ISO, ACGIH, FAA, and EASA.
          </p>
          <ul className="text-sm text-slate-600 dark:text-slate-400 space-y-1">
            <li>• ISO 2533:1975 - International Standard Atmosphere</li>
            <li>• ISO 7933:2023 - Predicted Heat Strain</li>
            <li>• ACGIH TLV®/BEI® Guidelines 2024</li>
            <li>• FAA Part 117 / EASA ORO.FTL</li>
          </ul>
        </div>
        
        <div className="warning-box">
          <h3 className="font-semibold text-slate-800 dark:text-white mb-3 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-warning-500" />
            Important Disclaimer
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
            These calculators are intended for educational and research purposes only. 
            Results should not be used for operational decision-making without proper 
            professional validation.
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            For citation and academic use, please reference the GitHub repository 
            and the original scientific sources provided with each calculator.
          </p>
        </div>
      </section>

      {/* Author Info */}
      <section className="glass-card p-6 text-center">
        <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-primary-500 to-accent-500 
          flex items-center justify-center text-white text-2xl font-bold mb-4">
          DM
        </div>
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white">
          Dr. Diego Malpica
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">
          Aerospace Medicine Specialist
        </p>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Universidad Nacional de Colombia 🇨🇴
        </p>
        <div className="mt-4 flex justify-center gap-3">
          <a href="https://github.com/strikerdlm/HumanPerformanceCalcs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn-secondary text-sm py-2">
            GitHub Repository
          </a>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
