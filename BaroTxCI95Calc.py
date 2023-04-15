# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 11:45:26 2023

@author: Diego Malpica
"""



total_cases = 257
total_trained = 6745
proportion = total_cases / total_trained

import numpy as np

z_score = 1.96
ci_margin = z_score * np.sqrt(proportion * (1 - proportion) / total_trained)
ci_lower = proportion - ci_margin
ci_upper = proportion + ci_margin

ci_lower_incidence_rate = ci_lower * 1000
ci_upper_incidence_rate = ci_upper * 1000

#Input data to calculate Error Factor with the 95% CI
lower_limit = 33.53
upper_limit = 42.67

print(f"The 95% confidence interval for the total incidence rate is ({ci_lower_incidence_rate:.2f}, {ci_upper_incidence_rate:.2f}) per 1000 person-year")

ef = np.sqrt(upper_limit / lower_limit)
print(f"The error factor for the given confidence interval is approximately {ef:.2f}")


