"""
Chisa Example 08: Custom Domain Creation (Density)
--------------------------------------------------
Chisa comes out-of-the-box with 12 core dimensions. But what if your domain 
requires a dimension that doesn't exist yet, like Material Density?

This script demonstrates how to build entirely new physical dimensions 
from scratch using Chisa's BaseUnit architecture and @axiom.derive.
"""

from chisa import axiom
from chisa import BaseUnit
from chisa.units.mass import Kilogram
from chisa.units.length import Meter

print("=== Building the 'Density' Dimension ===")

# 1. Define the Dimension Base with an absolute physical boundary
# We use @axiom.bound to dictate that Density cannot exist in negative space.
@axiom.bound(min_val=0, msg="Physics Violation: Density cannot be negative!")
class DensityUnit(BaseUnit):
    dimension = "density"

# 2. Synthesize the Base Unit using @axiom.derive
# Density = Mass / Volume (or Mass / Length^3).
# Chisa's Axiom Engine allows us to divide by multiple units seamlessly!
@axiom.derive(mul=[Kilogram], div=[Meter, Meter, Meter])
class KilogramPerCubicMeter(DensityUnit):
    symbol = "kg/m³"
    aliases = ["kg/m3", "kilogram per cubic meter"]

# 3. Create a derived unit manually using a base_multiplier
class GramPerCubicCentimeter(DensityUnit):
    symbol = "g/cm³"
    aliases = ["g/cm3", "gram per cubic centimeter"]
    # 1 g/cm³ is exactly 1,000 kg/m³
    base_multiplier = 1000.0  


print("\n=== 1. Testing the New Dimension ===")
# Let's instantiate our new units! Pure water has a density of ~1.0 g/cm³
water_density = GramPerCubicCentimeter(1.0)

# Convert to the SI base unit (kg/m³)
print(f"Water Density (g/cm³) : {water_density.format(tag=True)}")
print(f"Water Density (kg/m³): {water_density.to(KilogramPerCubicMeter).format(delim=True, tag=True)}")


print("\n=== 2. Testing the @axiom.bound Guardrail ===")
try:
    impossible_matter = GramPerCubicCentimeter(-5.0)
    
except Exception as error:
    print(f"[BLOCKED SUCCESSFULLY] Reason: {error}")