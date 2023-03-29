# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 18:59:57 2023

@author: Diego Malpica
"""

def sweat_rate(pre_exercise_weight, post_exercise_weight, fluid_intake, urine_volume, exercise_time_hours):
    return (pre_exercise_weight - post_exercise_weight + fluid_intake - urine_volume) / exercise_time_hours

if __name__ == "__main__":
    pre_exercise_weight = float(input("Enter pre-exercise body weight (kg): "))
    post_exercise_weight = float(input("Enter post-exercise body weight (kg): "))
    fluid_intake = float(input("Enter fluid intake during exercise (L): "))
    urine_volume = float(input("Enter urine volume during exercise (L): "))
    exercise_time_hours = float(input("Enter exercise duration (hours): "))

    sweat_rate_result = sweat_rate(pre_exercise_weight, post_exercise_weight, fluid_intake, urine_volume, exercise_time_hours)

    print("\nSweat Rate: {:.2f} L/h".format(sweat_rate_result))

    if pre_exercise_weight > post_exercise_weight:
        print("You lost weight during the exercise, consider hydrating more.")
    elif pre_exercise_weight < post_exercise_weight:
        print("You gained weight during the exercise, consider hydrating less.")
    else:
        print("Your weight remained stable during the exercise. Maintain your current hydration habits.")