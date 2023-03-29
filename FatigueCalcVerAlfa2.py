# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 14:02:27 2023

@author: DiegoMalpica - Ver Alpha
"""
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

def homeostatic_process(t, prev_reservoir_level, asleep, ai, sleep_quality, sleep_quantity, rem_sleep_time, non_rem_sleep_time, sleep_debt):
    K = 0.5
    K_adjusted = K * (1 + (8 - sleep_quantity) * 0.1)
    as_factor = 0.235
    tau1 = 1
    tau2 = 1
    delta_t = 1
    rem_factor = 0.6  # Adjust this factor based on how much REM sleep affects the recovery
    non_rem_factor = 0.4  # Adjust this factor based on how much non-REM sleep affects the recovery

    if asleep:
        recovery_factor = sleep_quality * (1 - math.exp(-delta_t / tau1))
        sleep_recovery = (rem_sleep_time * rem_factor + non_rem_sleep_time * non_rem_factor) / sleep_quantity
        return as_factor + recovery_factor * prev_reservoir_level * sleep_recovery + (1 - math.exp(-delta_t / tau2)) * (ai - as_factor)
    else:
        sleep_debt_factor = max(0, sleep_debt - 2) / 6
        return prev_reservoir_level - (K_adjusted + sleep_debt_factor) * t


def circadian_process(t, chronotype_offset):
    p = 18 + chronotype_offset
    p_prime = 3 + chronotype_offset
    beta = 0.5

    return math.cos(2 * math.pi * (t - p) / 24) + beta * math.cos(4 * math.pi * (t - p_prime) / 24)


def sleep_inertia(t):
    Imax = 5
    i = 0.04

    if t < 2:
        return Imax * math.exp(-t / i)
    else:
        return 0

def cognitive_performance(t, Rt, Ct, It):
    a1 = 7
    a2 = 5
    Rc = 2880

    return 100 * (Rt / Rc) + (a1 + a2 * (Rc - Rt) / Rc) * Ct + It

def workload(t, Wt_prev, load_rating, asleep):
    Wc = 75
    Wd = 1.14
    Wr = 11

    if asleep:
        return Wt_prev + Wr
    else:
        return Wt_prev - Wd * (1 + load_rating)

def cognitive_performance_with_workload(t, Rt, Ct, It, Wt, Wc):
    Et_base = cognitive_performance(t, Rt, Ct, It)
    return Et_base * (Wc - Wt) / Wc

def simulate_cognitive_performance(prediction_hours, sleep_history, work_history, load_rating_history, chronotype_offset):
    Wt_prev = 0
    Wc = 75
    sleep_debt = 0
    ideal_sleep_time = 8
    start_datetime = datetime.datetime(2000, 1, 1)
    time_points = [start_datetime + datetime.timedelta(hours=i) for i in range(prediction_hours)]
    circadian_rhythms = []
    cognitive_performances = []
    
    for sleep_session in sleep_history:
        sleep_start, sleep_end, sleep_quality, sleep_quantity, rem_sleep_time, non_rem_sleep_time, sleep_debt = sleep_session
        sleep_debt += max(0, ideal_sleep_time - sleep_quantity)

    for t in range(prediction_hours):
        sleep_session = sleep_history[t % 2]
        sleep_start, sleep_end, sleep_quality, sleep_quantity, rem_sleep_time, non_rem_sleep_time, sleep_debt = sleep_session

        work_session = work_history[t % 2]
        work_start, work_end = work_session
        load_rating = load_rating_history[t % 2]

        asleep = sleep_start <= t % 24 < sleep_end
        at_work = work_start <= t % 24 < work_end

        if t == 0:
            prev_reservoir_level = 2400
            ai = 1
        else:
            ai = 1

        Rt = homeostatic_process(t, prev_reservoir_level, asleep, ai, sleep_quality, sleep_quantity, rem_sleep_time, non_rem_sleep_time, sleep_debt)
        Ct = circadian_process(t, chronotype_offset)
        It = sleep_inertia(t)

        if at_work:
            Wt = workload(t, Wt_prev, load_rating, asleep)
            E_t = cognitive_performance_with_workload(t, Rt, Ct, It, Wt, Wc)
        else:
            E_t = cognitive_performance(t, Rt, Ct, It)

        # Remove the following line to avoid generating time_points again
        # time_points.append(t)
        
        circadian_rhythms.append(Ct)
        cognitive_performances.append(E_t)

    return time_points, circadian_rhythms, cognitive_performances

def main():
    # Gather user input
    prediction_hours = int(input("Enter the number of hours you want the prediction for: "))
    
    print("Enter your chronotype:")
    print("1: Early bird (morning type)")
    print("2: Intermediate type")
    print("3: Night owl (evening type)")
    chronotype = int(input("Your choice (1-3): "))

    if chronotype == 1:
        chronotype_offset = -1.5
    elif chronotype == 2:
        chronotype_offset = 0
    elif chronotype == 3:
        chronotype_offset = 1.5
    else:
        print("Invalid choice. Assuming intermediate type.")
        chronotype_offset = 0
        
    sleep_history = []
    for i in range(2): # Changed to 2 prior sleep days
        print(f"Enter sleep data for the {i+1}-th sleep session:")
        start_time = int(input("Start time (0-23): "))
        end_time = int(input("End time (0-23): "))
        quality = float(input("Sleep quality (0-1): "))
        quantity = float(input("Sleep quantity (0-12): "))
        rem_sleep_time = float(input("REM sleep time (hours): "))
        non_rem_sleep_time = float(input("Non-REM sleep time (hours): "))
        sleep_debt = float(input("sleep debt (hours): "))
        sleep_history.append((start_time, end_time, quality, quantity, rem_sleep_time, non_rem_sleep_time, sleep_debt))

    work_history = []
    for i in range(2): # Changed to 2 prior work days
        print(f"Enter work data for the {i+1}-th work session:")
        start_time = int(input("Work start time (0-23): "))
        end_time = int(input("Work end time (0-23): "))
        work_history.append((start_time, end_time))

    load_rating_history = []
    for i in range(2): # Changed to 2 prior workload 
        load_rating = int(input(f"Enter workload rating for the {i+1}-th work session (0-1): "))
        load_rating_history.append(load_rating)
    
    
    # Calculate cognitive performance for the desired number of hours
    time_points, circadian_rhythms, cognitive_performances = simulate_cognitive_performance(prediction_hours, sleep_history, work_history, load_rating_history, chronotype_offset)


    # Save cognitive performance data to an Excel file
    data = {
        "Time of Day": [(t.hour % 24) for t in time_points],
        "Predicted Cognitive Performance": cognitive_performances
    }
    df = pd.DataFrame(data)
    df.to_excel("cognitive_performance_data.xlsx", index=False)
    print("Cognitive performance data saved to 'cognitive_performance_data.xlsx'")
    # Plotting the results
    fig, ax = plt.subplots()
    
    # Add a fixed dotted line at 77.5
    ax.axhline(y=77.5, linestyle='--', color='black', alpha=0.6)
    
    # Set up the x-axis to display time in 24-hour format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Plot cognitive performance
    ax.plot(time_points, cognitive_performances, label='Cognitive Performance')
    
    # Create the colored boxes
    ax.fill_between(time_points, 0, 60, facecolor='red', alpha=0.4)
    ax.fill_between(time_points, 60, 80, facecolor='yellow', alpha=0.4)
    ax.fill_between(time_points, 80, 100, facecolor='green', alpha=0.4)
    
    ax.set_ylim(0, 100)
    ax.set_xlabel("Time")
    ax.set_ylabel("Cognitive Performance")
    ax.set_title("Cognitive Performance Prediction")
    
    # Remove the legend entry for the fixed line at 77.5
    handles, labels = ax.get_legend_handles_labels()  
    plt.show()

if __name__ == "__main__":
    main()
