"""
Chisa Example 01: Core Types, Basics, and Type Safety
-----------------------------------------------------
This script demonstrates the foundational data types Chisa uses:
Native Floats, high-precision Decimals, and NumPy Array dtype preservation.
It also covers basic Fluent API formatting.
"""

import numpy as np
from decimal import Decimal
from chisa import convert
from chisa.units.length import Kilometer

print("=== 1. Basic Formatting (Fluent API) ===")
# Use .use() for aesthetic UI/Console string formatting
res_verbose = convert(15.5, 'km').to('m').use(format='verbose', delim=True).resolve()
print(f"Verbose Format : {res_verbose}")  # 15.5 km = 15,500.0 m

res_tag = convert(36.5, 'celsius').to('fahrenheit').use(format='tag', prec=1).resolve()
print(f"Tag Format     : {res_tag}")      # 97.7 °F


print("\n=== 2. The Native Float Standard ===")
# By default, Chisa strictly uses Python's native `float` (float64) for all scalars.
# This prevents random TypeErrors when mixing Chisa outputs with external ML/Math libraries.
val_float = convert(10, 'km').to('m').use(format='raw').resolve()
print(f"Default Scalar : {val_float} (Type: {type(val_float).__name__})")


print("\n=== 3. Opting into Extreme Precision (Decimal) ===")
# If you need financial/audit-level precision, explicitly force Decimal mode.
# In the Fluent API, Chisa automatically safely casts your input into a Decimal.
val_dec = convert(10, 'km').to('m').use(mode='decimal', format='raw').resolve()
print(f"Decimal Mode   : {val_dec} (Type: {type(val_dec).__name__})")

# In the Explicit OOP API, you must explicitly pass a Decimal object to preserve it:
audit_distance = Kilometer(Decimal('10.5'))
print(f"OOP Exact Val  : {audit_distance.exact} (Type: {type(audit_distance.exact).__name__})")
# You can always safely extract it back to a float for external math using .mag
print(f"OOP Math Safe  : {audit_distance.mag} (Type: {type(audit_distance.mag).__name__})")


print("\n=== 4. NumPy Vectorization & Dtype Preservation ===")
# Chisa respects your NumPy array memory sizes natively!
# If you pass a memory-efficient float16 array, Chisa processes it as float16.

# Create an array of 1 million distances using ultra-light float16
tiny_memory_array = np.array([1.5, 2.0, 5.5], dtype=np.float16)
print(f"Input Array  : {tiny_memory_array} (Dtype: {tiny_memory_array.dtype})")

# Convert the array to meters
result_array = convert(tiny_memory_array, 'km').to('m').use(format='raw').resolve()
print(f"Result Array : {result_array} (Dtype: {result_array.dtype})")