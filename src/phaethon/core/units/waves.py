"""
Wave Physics and Spatial Gradients Module.
"""
from ..base import BaseUnit
from .. import axioms as _axiom
from .length import Meter, Centimeter, Millimeter, Kilometer, Inch
from .scalar import Cycle
from .geometry import Radian

# --- PURE SPATIAL GRADIENT ---
class LinearAttenuationUnit(BaseUnit):
    dimension = "linear_attenuation"

@_axiom.derive(1 / Meter)
class ReciprocalMeter(LinearAttenuationUnit):
    __base_unit__ = True
    symbol = "m⁻¹"

@_axiom.derive(1 / Meter)
class ReciprocalMeter(LinearAttenuationUnit):
    __base_unit__ = True
    symbol = "m⁻¹"
    aliases = ["1/m", "reciprocal_meter", "per_meter"]

@_axiom.derive(1 / Centimeter)
class ReciprocalCentimeter(LinearAttenuationUnit):
    symbol = "cm⁻¹"
    aliases = ["1/cm", "reciprocal_centimeter", "per_centimeter"]

@_axiom.derive(1 / Millimeter)
class ReciprocalMillimeter(LinearAttenuationUnit):
    symbol = "mm⁻¹"
    aliases = ["1/mm", "reciprocal_millimeter", "per_millimeter"]

@_axiom.derive(1 / Kilometer)
class ReciprocalKilometer(LinearAttenuationUnit):
    symbol = "km⁻¹"
    aliases = ["1/km", "reciprocal_kilometer", "per_kilometer"]

# --- SPATIAL FREQUENCY ---
@_axiom.bound(min_val=0, abstract=True)
class SpatialFrequencyUnit(BaseUnit):
    dimension = "spatial_frequency"

@_axiom.derive(Cycle / Meter)
class CyclesPerMeter(SpatialFrequencyUnit):
    __base_unit__ = True
    symbol = "cycle/m"
    aliases = ["cycles_per_meter"]

@_axiom.derive(Cycle / Centimeter)
class CyclesPerCentimeter(SpatialFrequencyUnit):
    symbol = "cycle/cm"
    aliases = ["cycles_per_centimeter", "cpcm"]

@_axiom.derive(Cycle / Millimeter)
class CyclesPerMillimeter(SpatialFrequencyUnit):
    symbol = "cycle/mm"
    aliases = ["cycles_per_millimeter", "cpmm", "lpmm", "lines_per_millimeter"]

@_axiom.derive(Cycle / Inch)
class CyclesPerInch(SpatialFrequencyUnit):
    symbol = "cycle/in"
    aliases = ["cycles_per_inch", "cpi", "lpi", "lines_per_inch"]


# --- WAVENUMBER (SPECTROSCOPY) ---
class WavenumberUnit(BaseUnit):
    dimension = "wavenumber"

@_axiom.derive(Radian / Meter)
class RadianPerMeter(WavenumberUnit):
    __base_unit__ = True
    symbol = "rad/m"
    aliases = ["radian_per_meter"]

@_axiom.derive(Radian / Centimeter)
class Kayser(WavenumberUnit):
    symbol = "cm⁻¹"
    aliases = ["kayser", "reciprocal_centimeter"]