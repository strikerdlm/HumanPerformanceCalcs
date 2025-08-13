#!/usr/bin/env python3
"""
Modern Visualizations for Human Performance Formulas
Creates eye-catching charts and infographics for sports science formulas
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# Set modern styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def create_vo2_max_visualization():
    """Create VO2 Max visualization with Cooper Test correlation"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # VO2 Max by fitness level
    fitness_levels = ['Sedentary', 'Recreational', 'Trained', 'Elite']
    vo2_values = [35, 45, 55, 70]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    bars = ax1.bar(fitness_levels, vo2_values, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax1.set_ylabel('VO₂ Max (ml·kg⁻¹·min⁻¹)', fontsize=14, fontweight='bold')
    ax1.set_title('VO₂ Max by Fitness Level', fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylim(0, 80)
    
    # Add value labels on bars
    for bar, value in zip(bars, vo2_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Cooper Test correlation
    distances = np.linspace(1.5, 3.5, 100)
    vo2_cooper = 22.351 * distances - 3.45
    
    ax2.plot(distances, vo2_cooper, linewidth=4, color='#FF6B6B', alpha=0.8)
    ax2.fill_between(distances, vo2_cooper, alpha=0.3, color='#FF6B6B')
    ax2.set_xlabel('12-min Run Distance (km)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Estimated VO₂ Max', fontsize=14, fontweight='bold')
    ax2.set_title('Cooper Test Formula', fontsize=16, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)
    
    # Add formula text
    ax2.text(0.05, 0.95, 'VO₂ₘₐₓ = 22.351 × D - 3.45', 
             transform=ax2.transAxes, fontsize=12, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('/workspace/vo2_max_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_power_performance_dashboard():
    """Create comprehensive power performance dashboard"""
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Power-Duration Curve
    ax1 = fig.add_subplot(gs[0, :2])
    durations = np.array([5, 15, 30, 60, 300, 1200, 3600])  # seconds
    power_values = np.array([1200, 800, 600, 400, 300, 250, 200])  # watts
    
    ax1.loglog(durations, power_values, 'o-', linewidth=4, markersize=8, 
               color='#FF6B6B', alpha=0.8)
    ax1.fill_between(durations, power_values, alpha=0.3, color='#FF6B6B')
    ax1.set_xlabel('Duration (seconds)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Power Output (watts)', fontsize=14, fontweight='bold')
    ax1.set_title('Power-Duration Relationship', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Power-to-Weight Ratios by Sport
    ax2 = fig.add_subplot(gs[0, 2])
    sports = ['Cycling\n(Sprinter)', 'Cycling\n(Climber)', 'Running\n(800m)', 'Rowing']
    pwr_ratios = [18, 6.5, 25, 5.8]
    colors = ['#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    
    bars = ax2.bar(sports, pwr_ratios, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax2.set_ylabel('Power-to-Weight\n(W/kg)', fontsize=12, fontweight='bold')
    ax2.set_title('Power-to-Weight by Sport', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    # Wingate Test Profile
    ax3 = fig.add_subplot(gs[1, :])
    time_wingate = np.linspace(0, 30, 100)
    peak_power = 1000
    fatigue_rate = 0.03
    power_profile = peak_power * np.exp(-fatigue_rate * time_wingate)
    
    ax3.plot(time_wingate, power_profile, linewidth=4, color='#FF6B6B', alpha=0.8)
    ax3.fill_between(time_wingate, power_profile, alpha=0.3, color='#FF6B6B')
    ax3.axhline(y=np.mean(power_profile), color='#4ECDC4', linestyle='--', 
                linewidth=3, label='Mean Power')
    ax3.set_xlabel('Time (seconds)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Power Output (watts)', fontsize=14, fontweight='bold')
    ax3.set_title('Wingate Test Power Profile', fontsize=16, fontweight='bold')
    ax3.legend(fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # Fatigue Index Visualization
    ax4 = fig.add_subplot(gs[2, 0])
    fatigue_types = ['FATI1\n(10s)', 'FATI2\n(30s)', 'FATI3\n(Full)']
    fatigue_values = [15, 35, 45]
    colors = ['#96CEB4', '#FECA57', '#FF6B6B']
    
    bars = ax4.bar(fatigue_types, fatigue_values, color=colors, alpha=0.8, 
                   edgecolor='white', linewidth=2)
    ax4.set_ylabel('Fatigue Index (%)', fontsize=12, fontweight='bold')
    ax4.set_title('Fatigue Indices', fontsize=14, fontweight='bold')
    
    # Critical Power Model
    ax5 = fig.add_subplot(gs[2, 1:])
    work_capacity = np.array([20000, 15000, 12000, 10000, 8000])
    time_to_exhaustion = np.array([60, 120, 180, 300, 600])
    
    # Linear regression for Critical Power
    coeffs = np.polyfit(time_to_exhaustion, work_capacity, 1)
    cp_line = np.poly1d(coeffs)
    
    ax5.scatter(time_to_exhaustion, work_capacity, s=100, color='#FF6B6B', 
                alpha=0.8, edgecolor='white', linewidth=2)
    ax5.plot(time_to_exhaustion, cp_line(time_to_exhaustion), '--', 
             linewidth=3, color='#4ECDC4', alpha=0.8)
    ax5.set_xlabel('Time to Exhaustion (seconds)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Total Work Capacity (J)', fontsize=12, fontweight='bold')
    ax5.set_title('Critical Power Model', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    plt.suptitle('Power Performance Dashboard', fontsize=20, fontweight='bold', y=0.98)
    plt.savefig('/workspace/power_performance_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_metabolic_infographic():
    """Create metabolic formulas infographic"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # RER vs Substrate Utilization
    rer_values = np.linspace(0.7, 1.0, 100)
    fat_oxidation = (1.0 - rer_values) / 0.3 * 100
    carb_oxidation = 100 - fat_oxidation
    
    ax1.fill_between(rer_values, 0, fat_oxidation, alpha=0.7, color='#4ECDC4', label='Fat')
    ax1.fill_between(rer_values, fat_oxidation, 100, alpha=0.7, color='#FF6B6B', label='Carbs')
    ax1.set_xlabel('RER (VCO₂/VO₂)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Substrate Utilization (%)', fontsize=14, fontweight='bold')
    ax1.set_title('Respiratory Exchange Ratio', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # METs by Activity
    activities = ['Rest', 'Walking', 'Jogging', 'Running', 'Cycling\n(Fast)']
    mets = [1, 3.5, 7, 12, 16]
    colors = ['#96CEB4', '#4ECDC4', '#45B7D1', '#FF6B6B', '#FECA57']
    
    bars = ax2.barh(activities, mets, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    ax2.set_xlabel('METs', fontsize=14, fontweight='bold')
    ax2.set_title('Metabolic Equivalents by Activity', fontsize=16, fontweight='bold')
    
    # Energy Expenditure over Time
    time_hours = np.linspace(0, 2, 100)
    power_watts = [200, 300, 400, 500]
    colors = ['#96CEB4', '#4ECDC4', '#FF6B6B', '#FECA57']
    
    for i, power in enumerate(power_watts):
        energy = power * time_hours * 3.6  # kcal
        ax3.plot(time_hours, energy, linewidth=3, color=colors[i], 
                label=f'{power}W', alpha=0.8)
    
    ax3.set_xlabel('Time (hours)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Energy Expenditure (kcal)', fontsize=14, fontweight='bold')
    ax3.set_title('Energy Expenditure vs Power', fontsize=16, fontweight='bold')
    ax3.legend(fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # Efficiency Comparison
    activities = ['Cycling', 'Running', 'Swimming', 'Rowing']
    efficiency = [23, 20, 15, 18]
    colors = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4']
    
    bars = ax4.bar(activities, efficiency, color=colors, alpha=0.8, 
                   edgecolor='white', linewidth=2)
    ax4.set_ylabel('Gross Efficiency (%)', fontsize=14, fontweight='bold')
    ax4.set_title('Mechanical Efficiency by Activity', fontsize=16, fontweight='bold')
    ax4.set_ylim(0, 30)
    
    # Add value labels
    for bar, value in zip(bars, efficiency):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('/workspace/metabolic_infographic.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_training_zones_visualization():
    """Create training zones and heart rate visualization"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Training Zones
    zones = ['Recovery\n(50-60%)', 'Aerobic\n(60-70%)', 'Tempo\n(70-80%)', 
             'Threshold\n(80-90%)', 'VO₂ Max\n(90-95%)', 'Anaerobic\n(95-100%)']
    percentages = [55, 65, 75, 85, 92.5, 97.5]
    colors = ['#96CEB4', '#4ECDC4', '#45B7D1', '#FECA57', '#FF6B6B', '#8B5CF6']
    
    bars = ax1.barh(zones, percentages, color=colors, alpha=0.8, 
                    edgecolor='white', linewidth=2)
    ax1.set_xlabel('% of VO₂ Max', fontsize=14, fontweight='bold')
    ax1.set_title('Training Zones', fontsize=16, fontweight='bold')
    ax1.set_xlim(0, 100)
    
    # Heart Rate Zones (Karvonen Method)
    hr_rest = 60
    hr_max = 190
    zone_percentages = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    hr_zones = [(hr_max - hr_rest) * pct + hr_rest for pct in zone_percentages]
    
    # Create heart rate visualization
    theta = np.linspace(0, 2*np.pi, 100)
    for i, (hr, color) in enumerate(zip(hr_zones, colors)):
        radius = hr / 200  # Scale for visualization
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        ax2.fill(x, y, color=color, alpha=0.3, label=f'Zone {i+1}: {int(hr)} bpm')
    
    ax2.set_xlim(-1, 1)
    ax2.set_ylim(-1, 1)
    ax2.set_aspect('equal')
    ax2.set_title('Heart Rate Zones (Karvonen)', fontsize=16, fontweight='bold')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig('/workspace/training_zones_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_interactive_formula_explorer():
    """Create interactive Plotly dashboard for formula exploration"""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('VO₂ Max vs Performance', 'Power-Duration Curve', 
                       'Training Stress Score', 'Lactate Threshold'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # VO2 Max scatter
    vo2_data = pd.DataFrame({
        'VO2_Max': [35, 42, 48, 55, 62, 68, 75],
        'Performance_Score': [60, 70, 75, 82, 88, 92, 98],
        'Athlete_Type': ['Recreational', 'Recreational', 'Trained', 'Trained', 
                        'Elite', 'Elite', 'Elite']
    })
    
    for athlete_type in vo2_data['Athlete_Type'].unique():
        data = vo2_data[vo2_data['Athlete_Type'] == athlete_type]
        fig.add_trace(
            go.Scatter(x=data['VO2_Max'], y=data['Performance_Score'],
                      mode='markers', name=athlete_type,
                      marker=dict(size=12, opacity=0.8)),
            row=1, col=1
        )
    
    # Power-Duration curve
    durations = [5, 15, 30, 60, 300, 1200, 3600]
    powers = [1200, 800, 600, 400, 300, 250, 200]
    
    fig.add_trace(
        go.Scatter(x=durations, y=powers, mode='lines+markers',
                  name='Power Curve', line=dict(width=4, color='red')),
        row=1, col=2
    )
    
    # TSS over time
    days = list(range(1, 8))
    tss_values = [85, 120, 95, 150, 75, 200, 60]
    
    fig.add_trace(
        go.Bar(x=days, y=tss_values, name='Daily TSS',
               marker_color='lightblue'),
        row=2, col=1
    )
    
    # Lactate curve
    intensities = np.linspace(40, 100, 20)
    lactate = 1 + np.exp((intensities - 75) / 10)
    
    fig.add_trace(
        go.Scatter(x=intensities, y=lactate, mode='lines',
                  name='Lactate Response', line=dict(width=4, color='green')),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Interactive Human Performance Dashboard",
        title_x=0.5,
        height=800,
        showlegend=True,
        template="plotly_white"
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="VO₂ Max (ml/kg/min)", row=1, col=1)
    fig.update_yaxes(title_text="Performance Score", row=1, col=1)
    
    fig.update_xaxes(title_text="Duration (seconds)", type="log", row=1, col=2)
    fig.update_yaxes(title_text="Power (watts)", row=1, col=2)
    
    fig.update_xaxes(title_text="Day", row=2, col=1)
    fig.update_yaxes(title_text="TSS", row=2, col=1)
    
    fig.update_xaxes(title_text="Exercise Intensity (%)", row=2, col=2)
    fig.update_yaxes(title_text="Blood Lactate (mmol/L)", row=2, col=2)
    
    fig.write_html('/workspace/interactive_formula_dashboard.html')

def create_formula_reference_cards():
    """Create reference cards for key formulas"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    formulas = [
        {
            'title': 'VO₂ Max',
            'formula': 'VO₂ₘₐₓ = Q × (CaO₂ - CvO₂) / BW',
            'description': 'Maximal oxygen uptake\nGold standard of aerobic fitness',
            'color': '#FF6B6B'
        },
        {
            'title': 'Cardiac Output',
            'formula': 'CO = HR × SV',
            'description': 'Heart rate × Stroke volume\nDetermines oxygen delivery',
            'color': '#4ECDC4'
        },
        {
            'title': 'Power-to-Weight',
            'formula': 'PWR = P / m',
            'description': 'Power output per kg body weight\nKey for climbing performance',
            'color': '#45B7D1'
        },
        {
            'title': 'Training Stress Score',
            'formula': 'TSS = (sec × NP × IF) / (FTP × 3600) × 100',
            'description': 'Quantifies training load\nBalances intensity and duration',
            'color': '#96CEB4'
        },
        {
            'title': 'Critical Power',
            'formula': 'CP = (W₂ - W₁) / (t₁ - t₂)',
            'description': 'Sustainable power output\nThreshold for fatigue',
            'color': '#FECA57'
        },
        {
            'title': 'Running Economy',
            'formula': 'RE = VO₂ / Velocity',
            'description': 'Oxygen cost of running\nEfficiency indicator',
            'color': '#8B5CF6'
        }
    ]
    
    for i, (ax, formula_info) in enumerate(zip(axes, formulas)):
        # Create fancy box
        fancy_box = FancyBboxPatch((0.05, 0.1), 0.9, 0.8,
                                  boxstyle="round,pad=0.02",
                                  facecolor=formula_info['color'],
                                  alpha=0.2,
                                  edgecolor=formula_info['color'],
                                  linewidth=3)
        ax.add_patch(fancy_box)
        
        # Add title
        ax.text(0.5, 0.85, formula_info['title'], 
                ha='center', va='center', fontsize=16, fontweight='bold',
                transform=ax.transAxes)
        
        # Add formula
        ax.text(0.5, 0.6, formula_info['formula'], 
                ha='center', va='center', fontsize=12, fontweight='bold',
                transform=ax.transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Add description
        ax.text(0.5, 0.3, formula_info['description'], 
                ha='center', va='center', fontsize=10,
                transform=ax.transAxes)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    plt.suptitle('Human Performance Formula Reference Cards', 
                 fontsize=20, fontweight='bold', y=0.95)
    plt.tight_layout()
    plt.savefig('/workspace/formula_reference_cards.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all visualizations"""
    print("🎨 Creating modern visualizations for human performance formulas...")
    
    print("📊 Generating VO₂ Max visualization...")
    create_vo2_max_visualization()
    
    print("⚡ Creating power performance dashboard...")
    create_power_performance_dashboard()
    
    print("🔋 Generating metabolic infographic...")
    create_metabolic_infographic()
    
    print("📈 Creating training zones visualization...")
    create_training_zones_visualization()
    
    print("🌐 Generating interactive dashboard...")
    create_interactive_formula_explorer()
    
    print("📋 Creating formula reference cards...")
    create_formula_reference_cards()
    
    print("✅ All visualizations created successfully!")
    print("\nGenerated files:")
    print("- vo2_max_visualization.png")
    print("- power_performance_dashboard.png") 
    print("- metabolic_infographic.png")
    print("- training_zones_visualization.png")
    print("- interactive_formula_dashboard.html")
    print("- formula_reference_cards.png")

if __name__ == "__main__":
    main()