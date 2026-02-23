"""
Chisa Example 02: Real-World IoT Sensor Normalization
-----------------------------------------------------
Scenario: You receive a massive legacy dataset (1 million rows) of weather 
sensors. The temperature is in Fahrenheit and pressure in PSI.
Your Machine Learning pipeline strictly requires standard SI units (Kelvin and Pascals).

This script demonstrates Chisa's high-performance native vectorization.
"""

import time
import numpy as np
from chisa import convert

print("=== 1. Generating 1,000,000 Mock IoT Sensor Readings ===")
# Generate 1 million random rows of legacy data
raw_temp_f = np.random.uniform(-40.0, 120.0, 1_000_000)
raw_pressure_psi = np.random.uniform(10.0, 50.0, 1_000_000)

print(f"Data generated. Array size: {raw_temp_f.nbytes / 1024 / 1024:.2f} MB each.")

print("\n=== 2. Chisa NumPy Vectorization in Action ===")
start_time = time.time()

# 1. Normalize Temperature (Fahrenheit to Kelvin)
# .resolve() bypasses scalar formatting and returns the fast, ML-ready numpy.ndarray
clean_temp_k = convert(raw_temp_f, 'F').to('Kelvin').use(format='raw').resolve()

# 2. Normalize Pressure (PSI to Pascals)
clean_pressure_pa = convert(raw_pressure_psi, 'psi').to('Pa').use(format='raw').resolve()

execution_time = time.time() - start_time

print(f"\n[SUCCESS] Processed 2,000,000 data points in {execution_time:.4f} seconds!")

print("\n--- Pipeline Verification (Index 0) ---")
print(f"Sensor 1 (Temp) : {raw_temp_f[0]:.2f} °F  -> {clean_temp_k[0]:.2f} K")
print(f"Sensor 1 (Press): {raw_pressure_psi[0]:.2f} PSI -> {clean_pressure_pa[0]:.2f} Pa")