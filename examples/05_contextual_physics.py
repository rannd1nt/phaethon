"""
Chisa Example 05: Contextual Physics (Environment Injection)
------------------------------------------------------------
Some physical units do not have absolute static bases. Their true value 
changes depending on the environment. 

For example, Gauge Pressure (psig) measures pressure *relative* to the local 
atmospheric pressure. This script shows how to inject environmental context 
into the OOP API to dynamically alter physical boundaries.
"""

from chisa.units.pressure import PSIG, PSI
from chisa import const

print("=== 1. Default Context (Sea Level) ===")
# By default, Chisa assumes standard atmospheric pressure (~14.696 psi or 101325 Pa).
# If your tire gauge reads 30 psi at sea level, the absolute pressure inside is higher.

tire_sea_level = PSIG(30.0)
absolute_sea = tire_sea_level.to(PSI)

print(f"Tire Gauge Reading          : {tire_sea_level.format(prec=1)}")
print(f"Absolute Pressure (Sea Level): {absolute_sea.format(prec=2)}")


print("\n=== 2. Injected Context (High Altitude - Denver, Colorado) ===")
# At high altitude, atmospheric pressure drops significantly (~12.1 psi).
# A tire inflated to 30 psig in Denver actually has less absolute pressure 
# inside compared to a tire inflated to 30 psig in Miami.

# We inject the local atmospheric pressure (normalized to Pascals) into the context!
tire_denver = PSIG(
    30.0, 
    context={"atmospheric_pressure": 12.1 * const.PSI_TO_PA} 
)
absolute_denver = tire_denver.to(PSI)

print(f"Tire Gauge Reading          : {tire_denver.format(prec=1)}")
print(f"Absolute Pressure (Denver)  : {absolute_denver.format(prec=2)}")

# The absolute pressure difference is automatically handled by Chisa's Axiom Engine!
difference = absolute_sea.mag - absolute_denver.mag
print(f"\nDifference in absolute force: {difference:.2f} psi")