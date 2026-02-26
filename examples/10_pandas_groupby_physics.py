"""
Chisa Example 10: Pandas GroupBy Physics
----------------------------------------
Integrating Chisa arrays directly with Pandas `GroupBy` to aggregate 
daily IoT power production into monthly energy summaries.
"""

import pandas as pd
from chisa import u

print("--- SMART GRID IoT AGGREGATION ---")

# Raw IoT readings from different zones
df_daily = pd.DataFrame({
    'Zone': ['North', 'North', 'South', 'South'],
    'Month': ['Jan', 'Jan', 'Feb', 'Feb'],
    'Avg_Power_MW': [2.5, 2.7, 3.0, 2.8],
    'Runtime_Hours': [24.0, 12.0, 24.0, 8.0]
})

print("1. Raw Daily Logs:")
print(df_daily)

# Physics Vectorization inside Pandas!
# Power (MW) * Time (Hours) = Energy (MWh)
power = u.Megawatt(df_daily['Avg_Power_MW'].values)
time = u.Hour(df_daily['Runtime_Hours'].values)

energy_synthesized = power * time

# Extract the magnitudes safely back into the DataFrame
df_daily['Energy_MWh'] = energy_synthesized.to(u.MegawattHour).mag

# Standard Pandas Aggregation
monthly_summary = df_daily.groupby(['Zone', 'Month'])['Energy_MWh'].sum().reset_index()

print("\n2. Monthly Energy Production (MWh):")
print(monthly_summary)