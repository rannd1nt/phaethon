"""
Chisa Example 04: Strict Physics Guardrails (@axiom.require)
------------------------------------------------------------
When building complex scientific applications, passing the wrong type of data 
(e.g., Temperature instead of Speed) into a formula can cause catastrophic bugs.

This script demonstrates how to protect your functions using Chisa's 
metaprogramming decorators and the Explicit OOP API.
"""

import numpy as np
from chisa import axiom, vmath
from chisa.units.mass import MassUnit, Kilogram
from chisa.units.speed import SpeedUnit, MeterPerSecond, KilometerPerHour
from chisa.units.energy import Joule
from chisa.units.temperature import Celsius

# @axiom.require enforces strict dimensional validation on the arguments.
# It guarantees `mass` is a MassUnit and `velocity` is a SpeedUnit.
@axiom.require(mass=MassUnit, velocity=SpeedUnit)
def calculate_kinetic_energy(mass: MassUnit, velocity: SpeedUnit) -> Joule:
    """Calculates Kinetic Energy: E_k = 0.5 * m * v^2"""
    
    # .mag safely extracts the standard float or NumPy array for pure math execution.
    # We use vmath to safely power the array without triggering NumPy type warnings.
    v_squared = vmath.power(velocity.to(MeterPerSecond).mag, 2)
    
    energy_raw = 0.5 * mass.to(Kilogram).mag * v_squared
    
    # Safely wrap the result back into a Chisa Energy unit (Joule)
    return Joule(energy_raw)


print("=== 1. Valid Execution (Scalar & Array) ===")

# Scenario A: Scalar Execution (A sedan moving at 100 km/h)
sedan_mass = Kilogram(1500.0)
sedan_speed = KilometerPerHour(100.0)
sedan_energy = calculate_kinetic_energy(mass=sedan_mass, velocity=sedan_speed)

print(f"Sedan Energy   : {sedan_energy.format(scinote=True)}")

# Scenario B: Vectorized Execution (A fleet of drones)
drone_masses = Kilogram(np.array([2.0, 2.5, 3.0]))
drone_speeds = MeterPerSecond(np.array([15.0, 20.0, 25.0]))
fleet_energy = calculate_kinetic_energy(mass=drone_masses, velocity=drone_speeds)

print(f"Fleet Energies : {fleet_energy.format(tag=True)}")


print("\n=== 2. The Guardrail Demonstration ===")
try:
    wrong_input = Celsius(30.0)
    
    print("Attempting to pass Temperature (Celsius) into the velocity argument...")
    # Accidentally passing Temperature instead of Speed!
    calculate_kinetic_energy(mass=sedan_mass, velocity=wrong_input)

except Exception as error:
    # Chisa catches the error before any corrupt data enters the formula!
    print(f"\n[BLOCKED SUCCESSFULLY] Reason:\n{error}")