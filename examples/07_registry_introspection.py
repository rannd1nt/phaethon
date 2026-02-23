"""
Chisa Example 07: Registry Introspection
----------------------------------------
When building dynamic applications or parsing CSV files, you often need 
to validate if a string (like 'kg' or 'm/s') is a valid physical unit.

Chisa provides snappy, NumPy-style root helper methods to interrogate 
the internal Unit Registry natively.
"""

import chisa
from chisa.units.temperature import Celsius
from chisa.units.speed import MeterPerSecond

print("=== 1. Identify Dimensions (dimof) ===")
# Resolves the physical dimension of string aliases, Classes, or Instances.
print(f"Alias 'kg' belongs to        : '{chisa.dimof('kg')}'")
print(f"Alias 'm/s' belongs to       : '{chisa.dimof(Celsius)}'")
print(f"Class Celsius belongs to     : '{chisa.dimof(MeterPerSecond(10))}'")


print("\n=== 2. List All Active Dimensions (dims) ===")
all_dims = chisa.dims()
print(f"Total dimensions loaded : {len(all_dims)}")
print(f"Active Dimensions       : {', '.join(all_dims[:6])} ...")


print("\n=== 3. Discover Available Units (unitsin) ===")
# Find all string symbols registered under a specific dimension
pressure_units = chisa.unitsin('pressure')
print(f"Pressure symbols available   : {', '.join(pressure_units[:8])}...")

# Pass `ascls=True` to retrieve the actual OOP Class objects for dynamic instantiation
mass_classes = chisa.unitsin('mass', ascls=True)
print(f"Mass Class Objects           : {mass_classes[0].__name__}, {mass_classes[1].__name__} ...")


print("\n=== 4. Find the Computational Baseline (baseof) ===")
# Identify the absolute mathematical root class for a dimension
temp_root = chisa.baseof('temperature')
print(f"Temperature mathematical root: {temp_root.__name__}")