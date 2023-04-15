# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 19:16:54 2023

@author: Diego Malpica
"""
import numpy as np
import pymc3 as pm
import multiprocessing as mp

def run_sampling(years, incidence_rates):
    with pm.Model() as model:
        # Priors
        alpha = pm.Normal("alpha", mu=0, sigma=10)
        beta = pm.Normal("beta", mu=0, sigma=10)

        # Likelihood
        mu = alpha + beta * years
        likelihood = pm.Normal("incidence_rates", mu=mu, sigma=10, observed=incidence_rates)

        # MCMC sampling
        trace = pm.sample(2000, tune=1000, target_accept=0.95, compute_convergence_checks=False, cores=1, return_inferencedata=False)
    return trace

if __name__ == '__main__':
    # Years and incidence rates
    years = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020])
    incidence_rates = np.array([83.68, 12.70, 20.29, 32.61, 27.67, 35.43, 48.93, 42.30, 45.86, 64.14, 33.33])

    # Set a timeout for the sampling process (in seconds)
    timeout = 60

    # Run the sampling process with a timeout
    with mp.Pool(1) as pool:
        result = pool.apply_async(run_sampling, args=(years, incidence_rates))
        try:
            trace = result.get(timeout)
        except mp.TimeoutError:
            pool.terminate()
            print("Sampling process took too long and was terminated.")

    # If the sampling process completed successfully, continue with the analysis
    if trace is not None:
        # Predict the incidence rates for the next 5 years
        future_years = np.array([2021, 2022, 2023, 2024, 2025])

        # Calculate the posterior predictive samples for the future years
        post_pred_samples = np.outer(trace["alpha"], np.ones(len(future_years))) + np.outer(trace["beta"], future_years)

        # Calculate the 25th, 75th and 95% CI percentiles for each year's incidence rate and probability
        post_pred_percentiles = np.percentile(post_pred_samples, [2.5, 25, 75, 97.5], axis=0)
        post_pred_prob_percentiles = post_pred_percentiles / 1000

        # Print the results in a table for incidence rates
        print("Incidence Rates")
        print("Year | Mean | 25th Percentile | 75th Percentile | 95% CI")
        print("-----|------|-----------------|-----------------|---------------------")
        for year, (rate_2_5, rate_25, rate_75, rate_97_5) in zip(future_years, post_pred_percentiles.T):
            print(f"{year} | {np.mean((rate_25 + rate_75) / 2):.2f} | {rate_25:.2f}         | {rate_75:.2f}         | ({rate_2_5:.2f}, {rate_97_5:.2f})")

        # Print the results in a table for probabilities
        print("\nProbabilities")
        print("Year | Mean | 25th Percentile | 75th Percentile | 95% CI")
        print("-----|------|-----------------|-----------------|---------------------")
        for year, (prob_2_5, prob_25, prob_75, prob_97_5) in zip(future_years, post_pred_prob_percentiles.T):
            print(f"{year} | {np.mean((prob_25 + prob_75) / 2):.4f} | {prob_25:.4f} | {prob_75:.4f} | ({prob_2_5:.4f}, {prob_97_5:.4f})")
