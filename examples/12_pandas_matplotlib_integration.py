"""
Chisa Example 12: Data Science Ecosystem (Pandas & Matplotlib)
--------------------------------------------------------------
Chisa is designed to natively integrate with the Python data science stack.
Because Chisa returns pure NumPy arrays and standard floats, you can seamlessly 
plug it into Pandas DataFrames and plot it using Matplotlib.

Scenario: Normalizing legacy wind tunnel telemetry data.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from chisa import convert

print("=== 1. Loading Legacy Telemetry Data (Pandas) ===")
# Simulating a dataset (e.g., from a CSV file)
telemetry_df = pd.DataFrame({
    'timestamp_sec': np.arange(0, 60, 5),
    'temp_f': [68.0, 75.2, 82.4, 95.0, 104.0, 113.0, 122.0, 131.0, 135.5, 140.0, 142.0, 145.0],
    'speed_mph': [10.0, 25.0, 45.0, 70.0, 100.0, 130.0, 160.0, 180.0, 195.0, 210.0, 215.0, 220.0]
})

print("Raw DataFrame:")
print(telemetry_df.head())

print("\n=== 2. Normalizing Data with Chisa ===")
# By extracting the underlying NumPy array (.values), Chisa processes 
# the entire column instantly without slow Python loops.

telemetry_df['temp_c'] = (
    convert(telemetry_df['temp_f'].values, 'F')
        .to('C')
        .use(format='raw')
        .resolve()
)

telemetry_df['speed_kmh'] = (
    convert(telemetry_df['speed_mph'].values, 'mph')
        .to('km/h')
        .use(format='raw')
        .resolve()
)

print("\nNormalized DataFrame (Ready for ML/Analysis):")
print(telemetry_df[['timestamp_sec', 'temp_c', 'speed_kmh']].head())

print("\n=== 3. Plotting with Matplotlib ===")
print("Generating visualization... (Check the popup window)")

# Setup the plot
fig, ax1 = plt.subplots(figsize=(8, 5))

color1 = 'tab:red'
ax1.set_xlabel('Time (Seconds)')
ax1.set_ylabel('Temperature (°C)', color=color1)
# Plotting the normalized Chisa data
ax1.plot(telemetry_df['timestamp_sec'], telemetry_df['temp_c'], color=color1, marker='o', label='Engine Temp')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, linestyle='--', alpha=0.6)

# Create a twin axis for speed
ax2 = ax1.twinx()  
color2 = 'tab:blue'
ax2.set_ylabel('Speed (km/h)', color=color2)
# Plotting the normalized Chisa data
ax2.plot(telemetry_df['timestamp_sec'], telemetry_df['speed_kmh'], color=color2, marker='s', label='Wind Speed')
ax2.tick_params(axis='y', labelcolor=color2)

plt.title('Wind Tunnel Telemetry (Normalized by Chisa)')
fig.tight_layout()

# Show the plot
plt.show()