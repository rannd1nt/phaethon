import time
import pandas as pd
import numpy as np

# Pydantic Imports
from typing import Annotated
from pydantic import BaseModel, ValidationError
from pydantic_pint import PydanticPintQuantity
from pint import UnitRegistry

# Phaethon Imports
import phaethon as ptn

# ==========================================
# CONFIGURATION & DATA GENERATION
# ==========================================
SAMPLE_SIZE = 100_000
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Generate 100,000 rows of mixed length data
# e.g., "150.5 cm", "1.2 km", "500 mm"
units = ["cm", "m", "mm", "km"]
values = np.random.uniform(1, 1000, SAMPLE_SIZE)
unit_labels = np.random.choice(units, SAMPLE_SIZE)

# Raw data formatted as strings just like incoming raw CSV/JSON data
raw_strings = [f"{v:.2f} {u}" for v, u in zip(values, unit_labels)]

df_messy = pd.DataFrame({'length_raw': raw_strings})

print(f"{'='*50}")
print(f"BENCHMARK: PYDANTIC+PINT vs Phaethon")
print(f"Dataset Size: {SAMPLE_SIZE:,} rows of mixed strings")
print(f"{'='*50}\n")

# ==========================================
# 1. PYDANTIC + PYDANTIC_PINT
# ==========================================
ureg = UnitRegistry()

class PydanticSchema(BaseModel):
    # Strictly target meters
    length: Annotated[ureg.Quantity, PydanticPintQuantity('m')]

print("Running Pydantic + Pint...")
start_time_pydantic = time.perf_counter()

# Step A: Convert DataFrame to list of dicts (fastest way to feed Pydantic)
records = df_messy.rename(columns={'length_raw': 'length'}).to_dict(orient='records')

# Step B: Instantiate Pydantic models row-by-row
parsed_records = []
for record in records:
    try:
        model = PydanticSchema(**record)
        # Extract the pure float magnitude for fair comparison
        parsed_records.append(model.length.magnitude)
    except ValidationError:
        parsed_records.append(np.nan)

# Step C: Reconstruct column
df_messy['pydantic_result'] = parsed_records

duration_pydantic = time.perf_counter() - start_time_pydantic
print(f"Pydantic Duration : {duration_pydantic:.4f} seconds\n")

# ==========================================
# 2. Phaethon (VECTORIZED SCHEMA)
# ==========================================
class PhaethonSchema(ptn.Schema):
    # Target Meters natively
    length_result: ptn.u.Meter = ptn.Field(
        source="length_raw",
        parse_string=True,
        on_error='coerce'
    )

print("Running Phaethon Vectorized Schema...")
start_time_Phaethon = time.perf_counter()

# Pass the dataframe directly. Phaethon handles string extraction and math via C-arrays.
clean_df_Phaethon = PhaethonSchema.normalize(df_messy)

duration_Phaethon = time.perf_counter() - start_time_Phaethon
print(f"Phaethon Duration    : {duration_Phaethon:.4f} seconds\n")

# ==========================================
# FINAL REPORT
# ==========================================
speedup = duration_pydantic / duration_Phaethon

print(f"{'-'*50}")
print(f"ANALYSIS SUMMARY")
print(f"{'-'*50}")
print(f"Phaethon performance gain: {speedup:.2f}x faster")
print(f"Efficiency increase:    {((duration_pydantic - duration_Phaethon) / duration_pydantic) * 100:.2f}% reduction in latency")
print(f"{'-'*50}")

# RESULT 
# ==================================================
# BENCHMARK: PYDANTIC+PINT vs Phaethon
# Dataset Size: 100,000 rows of mixed strings
# ==================================================

# Running Pydantic + Pint...
# Pydantic Duration : 28.1406 seconds

# Running Phaethon Vectorized Schema...
# Phaethon Duration    : 0.4319 seconds

# --------------------------------------------------
# ANALYSIS SUMMARY
# --------------------------------------------------
# Phaethon performance gain: 65.16x faster
# Efficiency increase:    98.47% reduction in latency
# --------------------------------------------------