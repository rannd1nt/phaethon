"""
Photometry Dimension Module.

This module handles the measurement of light in terms of its perceived brightness 
to the human eye. Crucial for smart lighting, agricultural IoT, and optical sensors.
Defines Luminous Intensity (Candela), Luminous Flux (Lumen), and Illuminance (Lux).
"""
from .. base import BaseUnit
from .. import axioms as _axiom
from .area import SquareMeter

# =========================================================================
# 1. LUMINOUS INTENSITY (Base: Candela)
# =========================================================================
@_axiom.bound(min_val=0, msg="Luminous intensity cannot be negative.")
class LuminousIntensityUnit(BaseUnit):
    dimension = "luminous_intensity"

class Candela(LuminousIntensityUnit):
    __base_unit__ = True
    symbol = "cd"
    aliases = ["cd", "candela", "candelas", "candlepower"]
    base_multiplier = 1.0

@_axiom.derive(0.001 * Candela)
class Millicandela(LuminousIntensityUnit):
    symbol = "mcd"
    aliases = ["millicandela"]

@_axiom.derive(0.981 * Candela)
class Candlepower(LuminousIntensityUnit):
    symbol = "cp"
    aliases = ["candlepower"]

# =========================================================================
# 2. LUMINOUS FLUX (Base: Lumen)
# =========================================================================
@_axiom.bound(min_val=0, msg="Luminous flux cannot be negative.")
class LuminousFluxUnit(BaseUnit):
    dimension = "luminous_flux"

class Lumen(LuminousFluxUnit):
    __base_unit__ = True
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
@_axiom.derive(Lumen / SquareMeter)
class Lux(IlluminanceUnit):
    __base_unit__ = True
    symbol = "lx"
    aliases = ["lx", "lux"]

@_axiom.derive(10.7639 * Lux)
class FootCandle(IlluminanceUnit):
    symbol = "fc"
    aliases = ["footcandle", "foot-candle", "lm/ft²"]