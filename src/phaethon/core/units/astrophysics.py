"""
Advanced Astrophysics and Particle Physics Module.

Provides units for deep space observation, cosmology (Hubble constants), 
and subatomic particle collisions (Cross-section areas).
Bridges the gap between classical metrics and astronomical phenomena.
"""

from ..base import BaseUnit
from .. import axioms as _axiom

from .area import SquareMeter
from .power import Watt
from .frequency import Hertz
from .length import Meter, Parsec, Kilometer
from .mass import Kilogram
from .time import Second
from .scalar import Expansion

# =========================================================================
# 1. CROSS-SECTION AREA (Particle Physics Collision Probabilities)
# Hooks directly into the existing "area" dimension.
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Quantum Violation: Particle cross-section area (Barn) cannot be negative.")
class CrossSectionAreaUnit(BaseUnit):
    dimension = "area"

@_axiom.derive(1e-28 * SquareMeter)
class Barn(CrossSectionAreaUnit):
    symbol = "b"
    aliases = ["barn", "barns"]

@_axiom.derive(1e-3 * Barn)
class Millibarn(CrossSectionAreaUnit):
    symbol = "mb"
    aliases = ["millibarn"]

@_axiom.derive(1e-6 * Barn)
class Microbarn(CrossSectionAreaUnit):
    symbol = "µb"
    aliases = ["ub", "microbarn"]

@_axiom.derive(1e-12 * Barn)
class Picobarn(CrossSectionAreaUnit):
    symbol = "pb"
    aliases = ["picobarn"]

@_axiom.derive(1e-15 * Barn)
class Femtobarn(CrossSectionAreaUnit):
    symbol = "fb"
    aliases = ["femtobarn"]

# =========================================================================
# 2. SPECTRAL FLUX DENSITY (Radio Astronomy)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Observation Error: Spectral flux density cannot be negative. Check for sensor noise/interference.")
class SpectralFluxDensityUnit(BaseUnit):
    dimension = "spectral_flux_density"

@_axiom.derive(Watt / (SquareMeter * Hertz))
class WattPerSquareMeterHertz(SpectralFluxDensityUnit):
    __base_unit__ = True
    symbol = "W/(m²·Hz)"

@_axiom.derive(1e-26 * WattPerSquareMeterHertz)
class Jansky(SpectralFluxDensityUnit):
    symbol = "Jy"
    aliases = ["jy", "jansky", "janskys"]

@_axiom.derive(1e-3 * Jansky)
class Millijansky(SpectralFluxDensityUnit):
    symbol = "mJy"
    aliases = ["mjy", "millijansky"]

@_axiom.logarithmic(reference=Jansky(3000), multiplier=-2.5)
class ApparentMagnitude(SpectralFluxDensityUnit):
    symbol = "mag"

# =========================================================================
# 3. COSMIC LENGTHS (Planetary & Stellar Radii)
# Hooks directly into the existing "length" dimension.
# Nominal IAU 2015 Constants.
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Stellar Geometry Error: Astronomical radius (Solar/Earth/Jupiter) cannot be negative.")
class CosmicLengthUnit(BaseUnit):
    dimension = "length"

@_axiom.derive(695700000.0 * Meter)
class SolarRadius(CosmicLengthUnit):
    symbol = "R_sun"
    aliases = ["R☉", "solar_radius", "solar radius"]

@_axiom.derive(6371000.0 * Meter)
class EarthRadius(CosmicLengthUnit):
    symbol = "R_earth"
    aliases = ["R⊕", "earth_radius", "earth radius"]

@_axiom.derive(71492000.0 * Meter)
class JupiterRadius(CosmicLengthUnit):
    symbol = "R_jup"
    aliases = ["R♃", "jupiter_radius", "jupiter radius"]

@_axiom.derive(1e6 * Parsec)
class Megaparsec(CosmicLengthUnit):
    symbol = "Mpc"
    aliases = ["megaparsec"]

# =========================================================================
# 4. COSMIC LUMINOSITY
# Hooks directly into the existing "power" dimension.
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Thermodynamic Violation: Stellar luminosity (energy output) cannot be negative.")
class CosmicLuminosityUnit(BaseUnit):
    dimension = "power"

@_axiom.derive(3.828e26 * Watt)
class SolarLuminosity(CosmicLuminosityUnit):
    symbol = "L_sun"
    aliases = ["L☉", "solar_luminosity", "solar luminosity"]

# =========================================================================
# 5. COSMOLOGY (Expansion of the Universe)
# =========================================================================


class GravitationalParameterUnit(BaseUnit):
    """Dimension for the Universal Gravitational Constant (G) and orbital parameters."""
    dimension = "gravitational_parameter"

@_axiom.derive((Meter ** 3) / (Kilogram * (Second ** 2)))
class CubicMeterPerKilogramSecondSquared(GravitationalParameterUnit):
    """The SI Base Unit for the Universal Gravitational Constant."""
    __base_unit__ = True
    symbol = "m³/(kg·s²)"
    aliases = ["g_constant_unit"]


@_axiom.bound(abstract=True, min_val=0, msg="Cosmology Error: Universe cannot have negative expansion rate!")
class ExpansionRateUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "expansion_rate"

@_axiom.derive(Expansion / Second)
class ExpansionPerSecond(ExpansionRateUnit):
    __base_unit__ = True
    symbol = "exp/s"
    aliases = ["expansion_per_second"]

@_axiom.derive((Kilometer / Second) * Expansion / Megaparsec)
class KilometerPerSecondPerMegaparsec(ExpansionRateUnit):
    symbol = "km/s/Mpc"
    aliases = ["hubble_unit"]

@_axiom.derive(70.0 * KilometerPerSecondPerMegaparsec)
class HubbleConstant(ExpansionRateUnit):
    symbol = "H₀"
    aliases = ["hubble_parameter"]
