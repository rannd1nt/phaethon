"""
Chisa Example 03: Explicit OOP Math & The Dimension Guardrails
--------------------------------------------------------------
In Chisa, units are first-class physical entities. 
This script demonstrates cross-unit mathematical operations and how Chisa 
proactively blocks impossible physics logic (e.g., adding Mass to Length).
"""

from chisa.units.length import Meter, Centimeter, Kilometer
from chisa.units.mass import Kilogram
from chisa import DimensionMismatchError

print("=== 1. Seamless Cross-Unit Mathematics ===")
# Chisa automatically normalizes everything to the underlying base unit (Meter)
# under the hood before performing the calculation.
track_1 = Kilometer(2.5)
track_2 = Meter(500.0)
track_3 = Centimeter(10_000.0)

total_length = track_1 + track_2 + track_3

# The output natively takes the shape of the LEFT-MOST operand (Kilometer)
# but you can dynamically format it!
print(f"Track 1: {track_1.format(tag=True)}")
print(f"Track 2: {track_2.format(tag=True)}")
print(f"Track 3: {track_3.format(tag=True)}")
print("-" * 30)
print(f"Total  : {total_length.format(tag=True)} (Inherited from left operand)")
print(f"Total  : {total_length.to(Meter).format(tag=True)} (Converted to Meters)")


print("\n=== 2. The Dimensional Guardrails (Type Safety) ===")
# In standard Python, if you use a dictionary or plain floats:
# distance = 10.0
# weight = 5.0
# total = distance + weight  <-- Python allows this logic error!

# In Chisa, physics rules are absolute.
distance = Meter(10.0)
weight = Kilogram(5.0)

try:
    print("Attempting to add Length and Mass...")
    impossible_math = distance + weight
    
except DimensionMismatchError as error:
    print(f"[BLOCKED] Chisa prevented a logic error in your code!")
    print(f"Error Details: {error}")