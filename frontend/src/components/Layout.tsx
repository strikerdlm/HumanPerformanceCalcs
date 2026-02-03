import React, { useState } from 'react';
import { 
  Home, Activity, Heart, Shield, Thermometer, 
  Brain, FlaskConical, BarChart3, AlertTriangle,
  Menu, X, Sun, Moon, ChevronRight, Beaker
} from 'lucide-react';
import type { CalculatorCategory, NavigationItem } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  currentCategory: CalculatorCategory;
  onCategoryChange: (category: CalculatorCategory) => void;
}

const navigationItems: NavigationItem[] = [
  { id: 'home', label: 'Home', icon: 'home', description: 'Dashboard Overview' },
  { id: 'atmospheric', label: 'Atmospheric & Physiological', icon: 'activity', description: 'Altitude, hypoxia, G-force' },
  { id: 'clinical', label: 'Clinical Calculators', icon: 'heart', description: 'BMR, BSA, eGFR, Wells scores' },
  { id: 'environmental', label: 'Environmental Monitoring', icon: 'thermometer', description: 'Heat stress, WBGT, UTCI' },
  { id: 'fatigue', label: 'Fatigue & Circadian', icon: 'brain', description: 'Performance, jet lag, duty limits' },
  { id: 'simulation', label: 'Simulation Studio', icon: 'flask', description: 'Trajectory forecasting' },
  { id: 'visualization', label: 'Visualization Studio', icon: 'chart', description: 'Custom plots and exports' },
  { id: 'risk', label: 'Risk Assessment', icon: 'alert', description: 'SD, NVG, chemical risk' },
];

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  home: Home,
  activity: Activity,
  heart: Heart,
  shield: Shield,
  thermometer: Thermometer,
  brain: Brain,
  flask: FlaskConical,
  chart: BarChart3,
  alert: AlertTriangle,
};

export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  currentCategory, 
  onCategoryChange 
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen flex ${darkMode ? 'dark' : ''}`}>
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-72' : 'w-20'} 
          glass-card flex-shrink-0 transition-all duration-300
          fixed left-0 top-0 bottom-0 z-40
          flex flex-col`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-200/50 dark:border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 
              flex items-center justify-center text-white shadow-lg shadow-primary-500/30">
              <Beaker className="w-5 h-5" />
            </div>
            {sidebarOpen && (
              <div className="animate-fade-in">
                <h1 className="font-bold text-slate-800 dark:text-white text-sm">
                  Aerospace Medicine
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Safety Dashboard v2.0
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 overflow-y-auto">
          <div className="space-y-1">
            {navigationItems.map((item) => {
              const Icon = iconMap[item.icon] || Activity;
              const isActive = currentCategory === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => onCategoryChange(item.id)}
                  className={`w-full nav-item ${isActive ? 'active' : ''}`}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {sidebarOpen && (
                    <div className="flex-1 text-left animate-fade-in">
                      <span className="block text-sm">{item.label}</span>
                      {isActive && (
                        <span className="text-xs text-slate-500 dark:text-slate-400">
                          {item.description}
                        </span>
                      )}
                    </div>
                  )}
                  {sidebarOpen && isActive && (
                    <ChevronRight className="w-4 h-4 text-primary-500" />
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* Footer controls */}
        <div className="p-3 border-t border-slate-200/50 dark:border-slate-700/50">
          <div className="flex items-center gap-2">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 
                transition-colors"
              title={darkMode ? 'Light mode' : 'Dark mode'}
            >
              {darkMode ? (
                <Sun className="w-5 h-5 text-amber-500" />
              ) : (
                <Moon className="w-5 h-5 text-slate-600" />
              )}
            </button>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 
                transition-colors ml-auto"
            >
              {sidebarOpen ? (
                <X className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              ) : (
                <Menu className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              )}
            </button>
          </div>
        </div>

        {/* Disclaimer */}
        {sidebarOpen && (
          <div className="p-3 mx-3 mb-3 warning-box text-xs animate-fade-in">
            <strong>Research Use Only</strong>
            <p className="mt-1 text-slate-600 dark:text-slate-400">
              Not for clinical decision-making without professional validation.
            </p>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-72' : 'ml-20'}`}>
        <div className="p-6 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
