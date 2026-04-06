"""
Scalar and Dimensionless Quantities Module.
Defines pure numbers, ratios, and counts that have no physical dimension.
Essential for ML features, Buckingham Pi variables (Reynolds, Mach), and percentages.
"""
from .. base import BaseUnit
import math
from .. import axioms as _axiom

@_axiom.bound(abstract=True)
class ScalarUnit(BaseUnit):
    """The base class for all dimensionless/scalar properties."""
    dimension = "dimensionless"

class Dimensionless(ScalarUnit):
    __base_unit__ = True
    symbol = ""
    aliases = ["dimensionless", "scalar", "unitless", "dimless", "count"]
    
class Percent(ScalarUnit):
    symbol = "%"
    aliases = ["percent", "percentage"]
    base_multiplier = 0.01

class Cycle(ScalarUnit):
    """Represents a single repeating event (used for Frequency)."""
    dimension = "cycle"
    __base_unit__ = True
    symbol = "cycle"

class Decay(ScalarUnit):
    """Represents a single atomic disintegration (used for Radioactivity)."""
    dimension = "decay"
    __base_unit__ = True
    symbol = "decay"

class Radiation(ScalarUnit):
    """Represents ionizing radiation presence (used for Absorbed Dose)."""
    dimension = "radiation"
    __base_unit__ = True
    symbol = "rad_particle"

class BiologicalEffect(ScalarUnit):
    """Represents biological weighting factor (used for Equivalent Dose)."""
    dimension = "biological_effect"
    __base_unit__ = True
    symbol = "bio_factor"

class Photon(ScalarUnit):
    """Represents a discrete quantum of light (Used in Quantum Optics)."""
    dimension = "photon"
    __base_unit__ = True
    symbol = "γ"
    aliases = ["photon", "photons"]

class SymbolData(ScalarUnit):
    """Represents a discrete communication symbol (Used to branch Baud Rate from Bit Rate)."""
    dimension = "symbol"
    __base_unit__ = True
    symbol = "sym"

class Count(ScalarUnit):
    """Represents a generic discrete item or particle (Used for Number Density)."""
    dimension = "count"
    __base_unit__ = True
    symbol = "count"
    aliases = ["item", "particles"]

class EnergyContent(ScalarUnit):
    """Phantom unit to separate Energy Density from Mechanical Pressure."""
    dimension = "energy_content"
    __base_unit__ = True
    symbol = "E_c"

class Expansion(ScalarUnit):
    """Phantom unit to separate cosmic expansion from generic frequency/rate."""
    dimension = "expansion"
    __base_unit__ = True
    symbol = "exp"

@_axiom.logarithmic(reference=Dimensionless(1), multiplier=10.0)
class Decibel(ScalarUnit):
    symbol = "dB"
    aliases = ["db", "decibel"]

@_axiom.logarithmic(reference=Dimensionless(1), multiplier=1.0, base=math.e)
class Neper(ScalarUnit):
    symbol = "Np"
    aliases = ["np", "neper", "nepers"]

@_axiom.logarithmic(reference=Dimensionless(1), multiplier=-1.0)
class Absorbance(ScalarUnit):
    symbol = "A"
    aliases = ["OD", "optical_density", "absorbance"]