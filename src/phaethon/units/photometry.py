"""
Photometry Dimension Module.

This module handles the measurement of light in terms of its perceived brightness 
to the human eye. Crucial for smart lighting, agricultural IoT, and optical sensors.
Defines Luminous Intensity (Candela), Luminous Flux (Lumen), and Illuminance (Lux).
"""
from ..core.base import BaseUnit
from ..core import axioms as _axiom
from .area import SquareMeter

# =========================================================================
# 1. LUMINOUS INTENSITY (Base: Candela)
# =========================================================================
@_axiom.bound(min_val=0, msg="Luminous intensity cannot be negative.")
class LuminousIntensityUnit(BaseUnit):
    dimension = "luminous_intensity"

class Candela(LuminousIntensityUnit):
    symbol = "cd"
    aliases = ["cd", "candela", "candelas", "candlepower"]
    base_multiplier = 1.0

# =========================================================================
# 2. LUMINOUS FLUX (Base: Lumen)
# =========================================================================
@_axiom.bound(min_val=0, msg="Luminous flux cannot be negative.")
class LuminousFluxUnit(BaseUnit):
    dimension = "luminous_flux"

class Lumen(LuminousFluxUnit):
    symbol = "lm"
    aliases = ["lm", "lumen", "lumens"]
    base_multiplier = 1.0

# =========================================================================
# 3. ILLUMINANCE (Base: Lux)
# =========================================================================
@_axiom.bound(min_val=0, msg="Illuminance cannot be negative.")
class IlluminanceUnit(BaseUnit):
    dimension = "illuminance"

# Lux: 1 Lumen per Square Meter
@_axiom.derive(mul=[Lumen], div=[SquareMeter])
class Lux(IlluminanceUnit):
    symbol = "lx"
    aliases = ["lx", "lux"]