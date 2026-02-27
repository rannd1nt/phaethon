"""
Phaethon Example 06: Structural Stress Algebra
-------------------------------------------
Demonstrates safe cross-dimensional OOP algebra. Phaethon automatically 
recognizes that Force divided by Area equates to Pressure (Pascals).
"""

import phaethon as cs
from phaethon import u

# Civil engineering load test on a concrete pillar
# Force: 50 Kips (Kilo-pounds)
applied_force = u.Kip(50.0)

# Area: 200 Square Inches
surface_area = u.SquareInch(200.0)

print(f"Applied Force : {applied_force}")
print(f"Surface Area  : {surface_area}")

# Dimensional Algebra: Force / Area = Pressure
# Phaethon synthesizes the class automatically
stress_pressure = applied_force / surface_area

print(f"\nRaw Synthesized Stress: {stress_pressure} (Dimension: {cs.dimof(stress_pressure)})")

# Normalize to standard Megapascals for the final report
stress_mpa = stress_pressure.to(u.Megapascal).mag
print(f"Standardized Stress   : {stress_mpa:.2f} MPa")