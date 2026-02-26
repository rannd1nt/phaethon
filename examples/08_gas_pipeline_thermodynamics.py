"""
Chisa Example 08: Gas Pipeline Thermodynamics
---------------------------------------------
Gases compress under pressure (Boyle's Law).
This script creates a dynamic 'Compressed Cubic Meter' unit that 
autonomously shrinks its base multiplier using the `C` (CtxProxy) object.
"""

from chisa import axiom, C, u

# Look at this beautiful declarative syntax!
# CtxProxy allows us to divide 1.0 by a dynamic runtime variable seamlessly.
@axiom.scale(formula=1.0 / C("pressure_atm", default=1.0))
class CompressedCubicMeter(u.CubicMeter):
    symbol = "m³_comp"

print("--- INDUSTRIAL GAS PIPELINE ---")

# Standard volume at 1.0 ATM (Normal Pressure)
normal_gas = CompressedCubicMeter(100.0, context={"pressure_atm": 1.0})
print(f"Normal Volume (1 ATM) : {normal_gas.to(u.CubicMeter).mag:.1f} m³")

# The gas enters a highly pressurized underground pipeline (5.0 ATM)
# Chisa autonomously recalculates the physical volume!
compressed_gas = CompressedCubicMeter(100.0, context={"pressure_atm": 5.0})
print(f"Compressed    (5 ATM) : {compressed_gas.to(u.CubicMeter).mag:.1f} m³")