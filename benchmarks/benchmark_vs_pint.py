import pandas as pd
import numpy as np
import time
import chisa as cs
from pint import UnitRegistry

# Configuration
SAMPLE_SIZE = 100_000
RANDOM_SEED = 42
SOURCE_UNITS = ["lbs", "oz"]
TARGET_UNIT = "kg"

np.random.seed(RANDOM_SEED)

# Generate Mock Dataset
raw_data = pd.DataFrame({
    'value': np.random.uniform(10, 100, SAMPLE_SIZE),
    'unit_label': np.random.choice(SOURCE_UNITS, SAMPLE_SIZE)
})

print(f"{'='*50}")
print(f"COMMENCING PERFORMANCE BENCHCHMARK")
print(f"Dataset Size: {SAMPLE_SIZE:,} records")
print(f"{'='*50}\n")

# ==========================================
# 1. PINT + PANDAS (Row-wise Iteration)
# ==========================================
unit_registry = UnitRegistry()

def pint_row_handler(row):
    try:
        quantity = unit_registry.Quantity(row['value'], row['unit_label'])
        return quantity.to(TARGET_UNIT).magnitude
    except Exception:
        return np.nan

start_time_pint = time.perf_counter()
raw_data['pint_result'] = raw_data.apply(pint_row_handler, axis=1)
duration_pint = time.perf_counter() - start_time_pint

print(f"Method: Pint + Pandas (.apply)  | Time: {duration_pint:.4f}s")


# ==========================================
# 2. CHISA (Vectorized Schema Processing)
# ==========================================
class ConversionSchema(cs.Schema):
    mass_kg: cs.u.Kilogram = cs.Field(
        source="value", 
        unit_col="unit_label",
        on_error='coerce'
    )

start_time_chisa = time.perf_counter()
normalized_df = ConversionSchema.normalize(raw_data)
duration_chisa = time.perf_counter() - start_time_chisa

print(f"Method: Chisa (Vectorized)      | Time: {duration_chisa:.4f}s")

# ==========================================
# FINAL REPORT
# ==========================================
speedup_magnitude = duration_pint / duration_chisa

print(f"\n{'-'*50}")
print(f"ANALYSIS SUMMARY")
print(f"{'-'*50}")
print(f"Chisa performance gain: {speedup_magnitude:.2f}x faster")
print(f"Efficiency increase:    {((duration_pint - duration_chisa) / duration_pint) * 100:.2f}% reduction in latency")
print(f"{'-'*50}")