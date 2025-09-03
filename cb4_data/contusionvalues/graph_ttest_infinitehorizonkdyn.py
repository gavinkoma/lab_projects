import seaborn as sns
import scipy.stats as ss
import numpy as np 
import pandas as pd 
from scipy.stats import ttest_ind

file_path = 'infinite_horizon_kdyn.csv.xlsx'
df = pd.read_excel(file_path)

import matplotlib.pyplot as plt

# Use original df — no filtering
plt.figure(figsize=(8, 6))
sns.boxplot(
    data=df,
    x='Group',
    y='Contusion Value (kDyn)',
    showfliers=False) # hide outlier dots, bu

exp = df[df['group'] == 'experimental']['actual_value']
ctrl = df[df['group'] == 'control']['actual_value']

t_stat, p_val = ttest_ind(exp, ctrl, equal_var=False)

print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_val:.4f}")

#ttest pvalue = 0.2118


# Filter the DataFrame to exclude actual_value > 220
df_filtered = df[df['actual_value'] <= 220]

# Create the Seaborn boxplot
plt.figure(figsize=(8, 6))
sns.boxplot(
    data=df_filtered,
    x='Group',
    y='Contusion Value (kDyn)',
    showfliers=False,  # hide outlier dots
    width=0.6
)

# Labels and title
plt.title('Actual Value by Group (Filtered to ≤220, Outliers Hidden)')
plt.xlabel('Group')
plt.ylabel('Actual Value')

plt.tight_layout()
plt.show()

from scipy.stats import ttest_ind

# Filter dataset
df_filtered = df[df['actual_value'] <= 220]

# Split into groups
exp = df_filtered[df_filtered['group'] == 'experimental']['actual_value']
ctrl = df_filtered[df_filtered['group'] == 'control']['actual_value']

# Perform Welch's t-test (unequal variance)
t_stat, p_val = ttest_ind(exp, ctrl, equal_var=False)

print(f"T-statistic: {t_stat:.3f}")
print(f"P-value: {p_val:.4f}")


#pval on filtered dataset
#0.2960



# Make a copy and capitalize the group labels
df_plot = df.copy()
df_plot['group'] = df_plot['group'].str.capitalize()

# Create the boxplot
plt.figure(figsize=(8, 6))
sns.boxplot(
    data=df_plot,
    x='group',
    y='actual_value',
    showfliers=False,
    width=0.6
)

# Labels and title
plt.title('Actual Value by Group (Outliers Hidden, Full Data Used)')
plt.xlabel('Group')
plt.ylabel('Impact Force (kDyn)')

plt.tight_layout()
plt.show()