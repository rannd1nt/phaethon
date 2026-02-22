"""
A global registry for absolute physical constants and standard conversion factors.
Designed to prevent magic numbers in physics modeling and unit definitions.
"""
from typing import Final

# =========================================================================
# 1. ABSOLUTE PHYSICAL CONSTANTS
# =========================================================================
# Thermodynamics
ABSOLUTE_ZERO_K: Final = 0.0
"""Value: 0.0 K"""

INF: Final = float('inf')
"""Value: infite (∞)"""

ZERO_CELSIUS_K: Final = 273.15
"""Value: 273.15 K"""

STANDARD_ATMOSPHERE_TEMP_K: Final = 288.15
"""Value: 288.15 K (15 °C)"""

STEFAN_BOLTZMANN: Final = 5.670374419e-8
"""Value: 5.670374419e-8 W/(m²·K⁴)"""

# Mechanics & Astrophysics
STANDARD_GRAVITY: Final = 9.80665
"""Value: 9.80665 m/s² (Exact)"""

SPEED_OF_LIGHT: Final = 299792458.0
"""Value: 299792458.0 m/s (Exact)"""

SPEED_OF_SOUND_0C: Final = 331.3
"""Value: 331.3 m/s"""

GRAVITATIONAL_CONSTANT: Final = 6.67430e-11
"""Value: 6.67430e-11 G (m³/(kg·s²))"""

PLANCK_CONSTANT: Final = 6.62607015e-34
"""Value: 6.62607015e-34 J·s (Exact)"""

# Pressure
STANDARD_ATMOSPHERE_PA: Final = 101325.0
"""Value: 101325.0 Pa (Exact)"""

# Astronomical Masses (Base: Kilogram)
SOLAR_MASS_KG: Final = 1.988409870698051e30
"""Value: 1.988409870698051e30 kg"""

EARTH_MASS_KG: Final = 5.972168e24
"""Value: 5.972168e24 kg"""

LUNAR_MASS_KG: Final = 7.342e22
"""Value: 7.342e22 kg"""

JUPITER_MASS_KG: Final = 1.89813e27
"""Value: 1.89813e27 kg"""

SATURN_MASS_KG: Final = 5.6834e26
"""Value: 5.6834e26 kg"""

URANUS_MASS_KG: Final = 8.6810e25
"""Value: 8.6810e25 kg"""

NEPTUNE_MASS_KG: Final = 1.02413e26
"""Value: 1.02413e26 kg"""

VENUS_MASS_KG: Final = 4.8675e24
"""Value: 4.8675e24 kg"""

MARS_MASS_KG: Final = 6.4171e23
"""Value: 6.4171e23 kg"""

MERCURY_MASS_KG: Final = 3.3011e23
"""Value: 3.3011e23 kg"""

PLUTO_MASS_KG: Final = 1.303e22
"""Value: 1.303e22 kg"""

CERES_MASS_KG: Final = 9.393e20
"""Value: 9.393e20 kg"""

# Atomic / Quantum Masses (Base: Kilogram)
ATOMIC_MASS_UNIT_KG: Final = 1.66053906660e-27
"""Value: 1.66053906660e-27 kg (1 Da)"""

PLANCK_MASS_KG: Final = 2.176434e-8
"""Value: 2.176434e-8 kg"""

ELECTRON_VOLT_C2_KG: Final = 1.78266192e-36
"""Value: 1.78266192e-36 kg"""

AVOGADRO_CONSTANT: Final = 6.02214076e23
"""Value: 6.02214076e23 mol⁻¹ (Exact)"""

BOLTZMANN_CONSTANT: Final = 1.380649e-23
"""Value: 1.380649e-23 J/K (Exact)"""

IDEAL_GAS_CONSTANT: Final = 8.314462618
"""Value: 8.314462618 J/(mol·K) (Exact)"""

FARADAY_CONSTANT: Final = 96485.33212
"""Value: 96485.33212 C/mol (Exact)"""

VACUUM_PERMITTIVITY: Final = 8.8541878128e-12
"""Value: ~8.8541878128e-12 F/m (Electric constant)"""

VACUUM_PERMEABILITY: Final = 1.25663706212e-6
"""Value: ~1.25663706212e-6 N/A² (Magnetic constant)"""

ELECTRON_MASS_KG: Final = 9.1093837015e-31
"""Value: 9.1093837015e-31 kg"""

PROTON_MASS_KG: Final = 1.67262192369e-27
"""Value: 1.67262192369e-27 kg"""

WIEN_DISPLACEMENT_CONSTANT: Final = 2.897771955e-3
"""Value: 2.897771955e-3 m·K (Wien's displacement law constant 'b')"""

RYDBERG_CONSTANT: Final = 10973731.568160
"""Value: 10973731.568160 m⁻¹ (Rydberg constant 'R∞')"""

BOHR_RADIUS: Final = 5.29177210903e-11
"""Value: 5.29177210903e-11 m (Bohr radius 'a0')"""

FINE_STRUCTURE_CONSTANT: Final = 0.0072973525693
"""Value: ~1/137.036 (Dimensionless fine-structure constant 'α')"""

MAGNETIC_FLUX_QUANTUM: Final = 2.067833848e-15
"""Value: 2.067833848e-15 Wb (Magnetic flux quantum 'Φ0')"""

CONDUCTANCE_QUANTUM: Final = 7.748091729e-5
"""Value: 7.748091729e-5 S (Conductance quantum 'G0')"""

CLASSICAL_ELECTRON_RADIUS: Final = 2.8179403227e-15
"""Value: 2.8179403227e-15 m (Classical electron radius 're')"""

# =========================================================================
# 2. EXACT CONVERSION FACTORS (International Agreements)
# =========================================================================
# Length (Base: Meter)
INCH_TO_METER: Final = 0.0254
"""Value: 0.0254 m"""

FOOT_TO_METER: Final = 0.3048
"""Value: 0.3048 m"""

MILE_TO_METER: Final = 1609.344
"""Value: 1609.344 m"""

NAUTICAL_MILE_TO_METER: Final = 1852.0
"""Value: 1852.0 m"""

LIGHT_YEAR_METER: Final = 9460730472580800.0
"""Value: 9460730472580800.0 m"""

ASTRONOMICAL_UNIT_METER: Final = 149597870700.0
"""Value: 149597870700.0 m"""

PARSEC_METER: Final = 3.085677581491367e16
"""Value: 3.085677581491367e16 m"""

# Mass (Base: Kilogram)
POUND_TO_KG: Final = 0.45359237
"""Value: 0.45359237 kg"""

OUNCE_TO_KG: Final = POUND_TO_KG / 16.0
"""Value: 0.028349523125 kg"""

TROY_OUNCE_TO_KG: Final = 0.0311034768
"""Value: 0.0311034768 kg"""

STONE_TO_KG: Final = POUND_TO_KG * 14.0
"""Value: 6.35029318 kg"""

SLUG_TO_KG: Final = 14.5939029372
"""Value: ~14.593 kg"""

SHORT_TON_TO_KG: Final = POUND_TO_KG * 2000.0
"""Value: 907.18474 kg"""

LONG_TON_TO_KG: Final = POUND_TO_KG * 2240.0
"""Value: 1016.0469088 kg"""

CARAT_TO_KG: Final = 0.0002
"""Value: 0.0002 kg (200 mg)"""

GRAIN_TO_KG: Final = 0.00006479891
"""Value: 0.00006479891 kg"""

# Derived Pressure Factors
PSI_TO_PA: Final = (POUND_TO_KG * STANDARD_GRAVITY) / (INCH_TO_METER ** 2)
"""Value: ~6894.757 Pa (Derived from lbf/in²)"""

TORR_TO_PA: Final = STANDARD_ATMOSPHERE_PA / 760.0
"""Value: ~133.322 Pa (1 atm / 760)"""

INHG_TO_PA: Final = 3386.389
"""Value: 3386.389 Pa (Inch of Mercury at 0 °C)"""

# Volume (Base: Cubic Meter)
LITER_TO_CUBIC_METER: Final = 0.001
"""Value: 0.001 m³ (Exactly 1 dm³)"""

US_GALLON_TO_CUBIC_METER: Final = 0.003785411784
"""Value: 0.003785411784 m³ (Exactly 231 in³)"""

UK_GALLON_TO_CUBIC_METER: Final = 0.00454609
"""Value: 0.00454609 m³ (Exactly 4.54609 Liters)"""

# Area (Base: Square Meter)
HECTARE_TO_SQ_METER: Final = 10000.0
"""Value: 10000.0 m² (100 Ares)"""

ARE_TO_SQ_METER: Final = 100.0
"""Value: 100.0 m²"""

ACRE_TO_SQ_METER: Final = 43560.0 * (FOOT_TO_METER ** 2)
"""Value: ~4046.8564224 m² (Exactly 43,560 sq ft)"""

# Time (Base: Second)
MINUTE_TO_SECOND: Final = 60.0
"""Value: 60.0 s"""

HOUR_TO_SECOND: Final = MINUTE_TO_SECOND * 60.0
"""Value: 3600.0 s"""

DAY_TO_SECOND: Final = HOUR_TO_SECOND * 24.0
"""Value: 86400.0 s"""

WEEK_TO_SECOND: Final = DAY_TO_SECOND * 7.0
"""Value: 604800.0 s"""

# Julian Year is strictly defined as exactly 365.25 days
JULIAN_YEAR_TO_SECOND: Final = DAY_TO_SECOND * 365.25
"""Value: 31557600.0 s"""

JULIAN_MONTH_TO_SECOND: Final = JULIAN_YEAR_TO_SECOND / 12.0
"""Value: 2629800.0 s"""

# Temperature (Base Reference: Celsius)
ABSOLUTE_ZERO_C: Final = -ZERO_CELSIUS_K
"""Value: -273.15 °C"""

FAHRENHEIT_OFFSET: Final = 32.0
"""Value: 32.0 °F (Freezing point of water)"""

RANKINE_OFFSET: Final = ZERO_CELSIUS_K * 1.8
"""Value: 491.67 °R (Exactly 273.15 * 1.8)"""

ABSOLUTE_ZERO_F: Final = (ABSOLUTE_ZERO_C * 1.8) + FAHRENHEIT_OFFSET
"""Value: -459.67 °F"""

ABSOLUTE_ZERO_RE: Final = ABSOLUTE_ZERO_C * 0.8
"""Value: -218.52 °Re"""

# Data (Base: Byte)
BYTES_PER_BIT: Final = 1.0 / 8.0
"""Value: 0.125 B (Exactly 1/8 Byte)"""

BYTES_PER_NIBBLE: Final = 1.0 / 2.0
"""Value: 0.5 B (Exactly 4 Bits or 1/2 Byte)"""

IEC_BASE: Final = 1024.0
"""Value: 1024.0 (2¹⁰ - The standard binary multiplier)"""

# Energy (Base: Joule)
CALORIE_TO_JOULE: Final = 4.184
"""Value: 4.184 J (Thermochemical calorie)"""

BTU_TO_JOULE: Final = 1055.05585262
"""Value: 1055.05585262 J (British Thermal Unit - IT)"""

ELECTRON_VOLT_TO_JOULE: Final = 1.602176634e-19
"""Value: 1.602176634e-19 J (Elementary charge 'e')"""