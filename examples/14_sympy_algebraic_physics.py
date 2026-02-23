"""
Chisa Example 14: SymPy Symbolic Derivation & Chisa Constants
-------------------------------------------------------------
SymPy is brilliant at isolating variables and solving formulas abstractly.
Chisa acts as the perfect companion by feeding those derived formulas with 
absolute, high-precision physical constants, and wrapping the output into 
usable physical units.

Scenario: Deriving the Escape Velocity formula symbolically, then 
calculating it specifically for the Planet Jupiter.
"""

import sympy as sp
from chisa import const
from chisa.units.speed import MeterPerSecond, KilometerPerHour

print("=== 1. Symbolic Derivation with SymPy ===")
# We want to find velocity (v) from the kinetic/potential energy balance:
# 0.5 * m * v^2 = (G * M * m) / r

# Define our symbols
v, G, M, r = sp.symbols('v G M r', positive=True)

# Define the isolated equation for v^2
escape_velocity_eq = sp.Eq(v**2, (2 * G * M) / r)

# Solve for v
derived_formula = sp.solve(escape_velocity_eq, v)[0]
print(f"Derived Formula for v : {derived_formula}")
# Output should be: sqrt(2)*sqrt(G)*sqrt(M)/sqrt(r)

print("\n=== 2. Physical Execution with Chisa ===")
# Now we use Chisa's built-in high-precision constants to actually calculate 
# the escape velocity of Jupiter!

jupiter_radius_meters = 71492000.0  # ~71,492 km

# Substitute the SymPy symbols with Chisa constants
execution_ready = derived_formula.subs({
    G: const.GRAVITATIONAL_CONSTANT,
    M: const.JUPITER_MASS_KG,
    r: jupiter_radius_meters
})

# Evaluate the final numerical float
raw_velocity_ms = float(execution_ready.evalf())

# Wrap the naked float back into a Chisa unit for safe conversion & formatting!
escape_velocity = MeterPerSecond(raw_velocity_ms)

print(f"Jupiter Escape Velocity (m/s)  : {escape_velocity.format(delim=True, prec=2, tag=True)}")
print(f"Jupiter Escape Velocity (km/h) : {escape_velocity.to(KilometerPerHour).format(delim=True, prec=2, tag=True)}")