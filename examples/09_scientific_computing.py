"""
Chisa Example 09: Scientific Computing (vmath, const & CtxProxy)
----------------------------------------------------------------
Chisa provides built-in utilities optimized for cross-type mathematics.
- `chisa.const`: High-precision physical constants without magic numbers.
- `chisa.vmath`: Universal math wrapper that safely handles scalars and arrays.
- `CtxProxy` (C): A lazy-evaluating proxy for context variables.
"""

import numpy as np
from chisa import const, vmath, C

print("=== 1. High-Precision Constants ===")
# No more magic numbers in your formulas!
print(f"Planck Constant (h) : {const.PLANCK_CONSTANT} J·s")
print(f"Avogadro Constant   : {const.AVOGADRO_CONSTANT} mol⁻¹")
print(f"Jupiter Mass        : {const.JUPITER_MASS_KG} kg")

print("\n=== 2. Universal Math (vmath) ===")
# Python's `math.sqrt` crashes on NumPy arrays. NumPy's `np.sqrt` adds overhead 
# for pure scalars. `vmath` automatically routes to the fastest engine!
scalar_val = 144.0
array_val = np.array([4.0, 9.0, 16.0])

print(f"Scalar SQRT : {vmath.sqrt(scalar_val)} (Type: {type(vmath.sqrt(scalar_val)).__name__})")
print(f"Array SQRT  : {vmath.sqrt(array_val)} (Type: {type(vmath.sqrt(array_val)).__name__})")

print("\n=== 3. Introduction to CtxProxy (C) ===")
# CtxProxy allows you to declare variables that don't exist yet. 
# They will be extracted from a dictionary at runtime. This is the secret 
# weapon for Chisa's @axiom decorators.

# We declare a proxy variable named 'payload_mass' with a default of 0.0
lazy_mass = C('payload_mass', default=0.0)

# We can perform math on it even before the value exists!
lazy_force = lazy_mass * const.STANDARD_GRAVITY

print(f"Proxy Object: {lazy_force}")
print(f"Notice how it stores the execution tree. We will use this in Example 11!")