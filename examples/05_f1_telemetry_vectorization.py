"""
Phaethon Example 05: F1 Telemetry Vectorization
--------------------------------------------
Phaethon completely bypasses scalar iteration. You can drop massive NumPy
arrays directly into Phaethon Units to perform conversions on millions 
of rows in fractions of a second.
"""

import numpy as np
from phaethon import u

# Simulating 1 million telemetry readings from an F1 car
sample_size = 1_000_000
raw_speed_mph = np.random.uniform(50.0, 220.0, sample_size)
raw_tire_pressure_psi = np.random.uniform(18.0, 24.0, sample_size)

print(f"Ingesting {sample_size:,} telemetry rows...")

# 1. Instantiate units directly with NumPy arrays (Zero memory leak)
speed_mph = u.MilePerHour(raw_speed_mph)
pressure_psi = u.PSI(raw_tire_pressure_psi)

# 2. Vectorized conversion to FIA Metric Standards
speed_kph = speed_mph.to(u.KilometerPerHour).mag
pressure_bar = pressure_psi.to(u.Bar).mag

print("\n--- VECTORIZED METRIC RESULTS (Top 3 Rows) ---")
print(f"Speed (km/h) : {speed_kph[:3]}")
print(f"Tire (Bar)   : {pressure_bar[:3]}")