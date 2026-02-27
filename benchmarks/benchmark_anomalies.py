"""
Phaethon Stress Test: The 1 Million Row Anomaly Benchmark
------------------------------------------------------
Testing the performance of Phaethon's Vectorized Pre-Filtering on massive
datasets with high anomaly rates (values violating Absolute Zero).
"""

import pandas as pd
import numpy as np
import phaethon as ptn
from phaethon import u
import time

# =========================================================================
# 1. SETUP MASSIVE DIRTY DATASET
# =========================================================================
SAMPLE_SIZE = 1_000_000

print(f"[{time.strftime('%H:%M:%S')}] Generating {SAMPLE_SIZE:,} rows of dirty physics data...")

# Generate a mix of Valid and INVALID temperatures (violating Absolute Zero)
# Valid: 0 to 100. Invalid: -300 to -1000
raw_values = np.random.uniform(-1000, 100, SAMPLE_SIZE)

# Randomize the units (Mix of Celsius, Fahrenheit, and Kelvin)
raw_units = np.random.choice(["C", "F", "K"], SAMPLE_SIZE)

# Combine them into a single dirty string column: e.g., "-500.5 C"
df_dirty = pd.DataFrame({
    'Sensor_Data': [f"{val:.2f} {unit}" for val, unit in zip(raw_values, raw_units)]
})

print(f"[{time.strftime('%H:%M:%S')}] Dataset ready in memory. Sample:")
print(df_dirty.head())

# =========================================================================
# 2. DEFINE THE STRICT SCHEMA
# =========================================================================
class ExtremeThermalSchema(ptn.Schema):
    # Target: Kelvin (Absolute Thermodynamic Baseline)
    # We set on_error='coerce' so extreme anomalies quietly become NaN
    standardized_temp: u.Kelvin = ptn.Field(
        source="Sensor_Data", 
        parse_string=True, 
        on_error='coerce',
        round=2
    )

# =========================================================================
# 3. EXECUTE & MEASURE
# =========================================================================
print(f"\n[{time.strftime('%H:%M:%S')}] COMMENCING PHAETHON VECTORIZED NORMALIZATION...")

start_time = time.perf_counter()

# Run the 1-Million row pipeline
clean_df = ExtremeThermalSchema.normalize(df_dirty)

end_time = time.perf_counter()
duration = end_time - start_time

# =========================================================================
# 4. REPORTING
# =========================================================================
total_nans = clean_df['standardized_temp'].isna().sum()

print("\n" + "="*50)
print("BENCHMARK RESULTS")
print("="*50)
print(f"Total Rows Processed : {SAMPLE_SIZE:,}")
print(f"Physics Violations   : {total_nans:,} anomalies safely neutralized to NaN")
print(f"Valid Data Surviving : {SAMPLE_SIZE - total_nans:,} records")
print(f"Execution Time       : {duration:.4f} seconds")
print("="*50)

print("\nSample Output:")
# Combine to show before and after
print(pd.concat([df_dirty.head(), clean_df.head()], axis=1))