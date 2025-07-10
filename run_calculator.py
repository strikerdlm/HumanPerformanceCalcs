#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human Performance Calculations - Unified Entry Point
@author: Diego Malpica

Single entry point for all aerospace medicine calculators.
For research and educational use only.
"""

import sys
import importlib
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def display_main_menu():
    """Display the main calculator menu."""
    print("\n" + "="*70)
    print("   HUMAN PERFORMANCE CALCULATIONS FOR AEROSPACE MEDICINE")
    print("="*70)
    print("For research and educational use only.")
    print("Not for operational decision-making without professional validation.")
    print("\nSelect a calculator domain:")
    print("="*40)
    
    print("\n1. DECOMPRESSION SICKNESS (DCS)")
    print("   - DCS risk prediction")
    print("   - Barotrauma analysis")
    
    print("\n2. HEAT STRESS ASSESSMENT")
    print("   - Physiological Strain Index (PSI)")
    print("   - Sweat rate calculations")
    print("   - Heat strain modeling")
    
    print("\n3. COLD STRESS EXPOSURE")
    print("   - Wind chill temperature")
    print("   - Cold survival prediction")
    
    print("\n4. ALTITUDE EFFECTS")
    print("   - Altitude from pressure")
    print("   - Time of Useful Consciousness (TUC)")
    
    print("\n5. FATIGUE & COGNITIVE PERFORMANCE")
    print("   - Fatigue modeling")
    
    print("\n6. MOTION SICKNESS")
    print("   - MSSQ questionnaire processing")
    
    print("\n0. EXIT")
    print("="*40)

def display_domain_menu(domain: str, options: dict):
    """Display calculators for a specific domain."""
    print(f"\n{domain.upper()} CALCULATORS")
    print("="*40)
    
    for key, (name, description) in options.items():
        print(f"{key}. {name}")
        print(f"   {description}")
    
    print("\n0. Back to main menu")
    print("="*40)

def run_calculator(module_path: str, function_name: str = "main"):
    """Import and run a calculator module."""
    try:
        module = importlib.import_module(module_path)
        calculator_func = getattr(module, function_name)
        
        print("\n" + "-"*50)
        calculator_func()
        print("-"*50)
        
        input("\nPress Enter to continue...")
        
    except ImportError as e:
        print(f"Error: Could not import {module_path}")
        print(f"Details: {e}")
        input("\nPress Enter to continue...")
    except AttributeError:
        print(f"Error: Function '{function_name}' not found in {module_path}")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"Error running calculator: {e}")
        input("\nPress Enter to continue...")

def handle_decompression_menu():
    """Handle the decompression sickness calculator menu."""
    options = {
        "1": ("DCS Risk Calculator", "Machine learning-based DCS risk prediction"),
        "2": ("DCS Ensemble Model", "Enhanced ensemble model for DCS risk"),
        "3": ("Barotrauma MCMC", "Barometric treatment modeling"),
        "4": ("Barotrauma CI", "Confidence interval calculations")
    }
    
    while True:
        display_domain_menu("Decompression Sickness", options)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            run_calculator("aerospace_medicine.decompression.dcs_risk")
        elif choice == "2":
            print("DCS Ensemble Model - Module needs to be implemented")
            input("Press Enter to continue...")
        elif choice == "3":
            print("Barotrauma MCMC - Module needs to be implemented")
            input("Press Enter to continue...")
        elif choice == "4":
            print("Barotrauma CI - Module needs to be implemented")
            input("Press Enter to continue...")
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def handle_heat_stress_menu():
    """Handle the heat stress calculator menu."""
    options = {
        "1": ("Physiological Strain Index", "PSI calculation with age adjustment"),
        "2": ("Sweat Rate Calculator", "ACSM-based sweat rate and dehydration"),
        "3": ("PHS-HR Heat Strain", "Predicted Heat Strain using Heart Rate"),
        "4": ("Ontario Sweat Rate", "Regional sweat rate calculations")
    }
    
    while True:
        display_domain_menu("Heat Stress Assessment", options)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            run_calculator("aerospace_medicine.heat_stress.strain_index")
        elif choice == "2":
            print("Sweat Rate Calculator - Module needs to be implemented")
            input("Press Enter to continue...")
        elif choice == "3":
            print("PHS-HR Model - Module needs to be implemented")
            input("Press Enter to continue...")
        elif choice == "4":
            print("Ontario Sweat Rate - Module needs to be implemented")
            input("Press Enter to continue...")
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def handle_cold_stress_menu():
    """Handle the cold stress calculator menu."""
    options = {
        "1": ("Wind Chill Calculator", "NOAA wind chill index with frostbite risk"),
        "2": ("Cold Survival Prediction", "Cold stress survival assessment")
    }
    
    while True:
        display_domain_menu("Cold Stress Exposure", options)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            run_calculator("aerospace_medicine.cold_stress.wind_chill")
        elif choice == "2":
            print("Cold Survival - Module needs to be implemented")
            input("Press Enter to continue...")
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def handle_altitude_menu():
    """Handle the altitude effects calculator menu."""
    options = {
        "1": ("Altitude Calculator", "Altitude from barometric pressure"),
        "2": ("TUC Model v4", "Time of Useful Consciousness prediction"),
        "3": ("TUC Model v5", "Altitude-focused TUC modeling")
    }
    
    while True:
        display_domain_menu("Altitude Effects", options)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            run_calculator("aerospace_medicine.altitude.altitude_calc")
        elif choice == "2":
            print("TUC v4 - Module needs to be implemented")
            input("Press Enter to continue...")
        elif choice == "3":
            print("TUC v5 - Module needs to be implemented")
            input("Press Enter to continue...")
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def handle_fatigue_menu():
    """Handle the fatigue calculator menu."""
    options = {
        "1": ("Fatigue Model", "Comprehensive fatigue and cognitive performance")
    }
    
    while True:
        display_domain_menu("Fatigue & Cognitive Performance", options)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            print("Fatigue Model - Module needs to be implemented")
            input("Press Enter to continue...")
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def handle_motion_sickness_menu():
    """Handle the motion sickness calculator menu."""
    options = {
        "1": ("MSSQ Calculator", "Motion Sickness Susceptibility Questionnaire")
    }
    
    while True:
        display_domain_menu("Motion Sickness", options)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            print("MSSQ Calculator - Module needs to be implemented")
            input("Press Enter to continue...")
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def main():
    """Main entry point for the calculator suite."""
    try:
        while True:
            display_main_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "0":
                print("\nThank you for using Human Performance Calculations!")
                print("Remember: For operational use, consult qualified professionals.")
                sys.exit(0)
            elif choice == "1":
                handle_decompression_menu()
            elif choice == "2":
                handle_heat_stress_menu()
            elif choice == "3":
                handle_cold_stress_menu()
            elif choice == "4":
                handle_altitude_menu()
            elif choice == "5":
                handle_fatigue_menu()
            elif choice == "6":
                handle_motion_sickness_menu()
            else:
                print("Invalid choice. Please enter a number from 0-6.")
                input("Press Enter to continue...")
                
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 