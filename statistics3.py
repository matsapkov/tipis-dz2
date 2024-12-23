import scipy.stats as stats
import numpy as np


data = [12496, 12496, 12496, 12496, 12504, 12504, 12504, 12504]

unique_values, counts = np.unique(data, return_counts=True)

expected_frequency = [len(data) / len(unique_values)] * len(unique_values)

chi2_stat, p_val = stats.chisquare(counts, expected_frequency)

print(f"Chi-squared Statistic: {chi2_stat}")
print(f"P-value: {p_val}")

if p_val < 0.05:
    print("Распределение не является равномерным (отклоняем гипотезу).")
else:
    print("Распределение является равномерным (не отклоняем гипотезу).")
