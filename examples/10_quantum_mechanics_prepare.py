"""
Chisa Example 10: The Magic Extractor (@axiom.prepare)
------------------------------------------------------
In Quantum Mechanics, calculating the energy of a photon requires its wavelength.
Formula: E = (h * c) / wavelength

Instead of manually converting and extracting values inside the function, 
@axiom.prepare automatically intercepts Chisa objects, normalizes them, 
and extracts their math-safe magnitudes (.mag) before execution!
"""

import numpy as np
from chisa import axiom, const
from chisa.units.length import Meter, Nanometer
from chisa.units.energy import Joule, Electronvolt

# @prepare ensures 'wavelength' is always processed as a float/array in Meters
@axiom.prepare(wavelength=Meter)
def compute_photon_energy(wavelength=0.0):
    """Calculates the absolute energy of a photon based on its wavelength."""
    # Notice the clean body! No .to().mag clutter. 
    # 'wavelength' is already guaranteed to be a math-safe magnitude in Meters.
    return (const.PLANCK_CONSTANT * const.SPEED_OF_LIGHT) / wavelength

print("=== Quantum Photonics Calculation ===")

# Scenario: Analyzing a spectrum of visible light (Red, Green, Blue) in Nanometers
light_spectrum = Nanometer(np.array([700.0, 532.0, 450.0]))
print(f"Wavelengths (Input): {light_spectrum.format(tag=True)}")

# Pass the Chisa object directly into the prepared function
raw_energy_joules = compute_photon_energy(wavelength=light_spectrum)

# Wrap the pure array result back into an Energy unit
photon_energy = Joule(raw_energy_joules)

# Convert to Electronvolts (eV) for easier quantum reading
energy_ev = photon_energy.to(Electronvolt)

print(f"Energy in Joules   : {photon_energy.format(scinote=True)}")
print(f"Energy in eV       : {energy_ev.format(prec=2, tag=True)}")