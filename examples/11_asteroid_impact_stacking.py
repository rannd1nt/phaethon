"""
Chisa Example 11: Axiom Stacking & Lazy Context (Asteroid Impact)
-----------------------------------------------------------------
Chisa's internal engine strictly follows this equation: y = (x + c) * m
This allows for extreme physical synthesis when stacking Axioms.

Scenario: Calculating the Kinetic Energy of an asteroid impact.
Energy = Mass * (0.5 * Velocity^2)

We will create a new unit where the input (x) is Mass, the shift (c) is an 
added payload mass, and the scale multiplier (m) calculates the velocity physics.
"""

from chisa import axiom, const, vmath, C
from chisa.units.energy import EnergyUnit, Joule
from chisa.units.speed import MeterPerSecond
from chisa.units.mass import Kilogram

# FIXED: We use the explicit Class 'MeterPerSecond', not an operation like Meter/Second.
@axiom.prepare(velocity=MeterPerSecond)
def calc_kinetic_multiplier(velocity=0.0):
    """Returns the kinetic multiplier: 0.5 * v^2"""
    return 0.5 * vmath.power(velocity, 2)

# AXIOM STACKING:
# 1. @derive: We inherit the base properties of 1 Joule.
# 2. @shift : We lazily inject any attached payload mass using CtxProxy (C).
# 3. @scale : We multiply the total mass by the kinetic formula above.
@axiom.derive(mul=[Joule])
@axiom.shift(formula=C("attached_payload_kg", default=0.0))
@axiom.scale(formula=calc_kinetic_multiplier)
class AsteroidImpact(EnergyUnit):
    symbol = "J_impact"


print("=== Simulating Asteroid Impact Energy ===")

# We instantiate the impact using the Asteroid's Mass (e.g., Ceres)
# We inject the velocity and any attached payload via the context dictionary.
impact_event = AsteroidImpact(
    const.CERES_MASS_KG,  # x: Base mass of Ceres
    context={
        "attached_payload_kg": const.EARTH_MASS_KG,  # c: Shift (added mass)
        "velocity": const.SPEED_OF_SOUND_0C * 50.0,  # m: Mach 50 velocity
    }
)

# Because of our @derive stacking, Chisa inherently knows this object 
# is pure Energy and normalizes it to Joules automatically!
total_joules = impact_event.to(Joule)

print(f"Asteroid Mass (Ceres) : {const.CERES_MASS_KG:.2E} kg")
print(f"Payload Mass (Earth)  : {const.EARTH_MASS_KG:.2E} kg")
print(f"Impact Velocity       : Mach 50")
print("-" * 40)
print(f"Total Impact Energy   : {total_joules.format(scinote=True)}")

# Optional: Defining a custom unit on-the-fly!
# 1 Megaton of TNT is exactly 4.184e15 Joules (4.184 Petajoules)
@axiom.derive(mul=[4.184e15, Joule])
class MegatonTNT(EnergyUnit):
    symbol = "Mt"

megatons = impact_event.to(MegatonTNT)
print(f"Energy in Megatons    : {megatons.format(prec=2, delim=True, tag=True)}")