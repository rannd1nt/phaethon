"""
Fluid Dynamics and Transport Phenomena Module (excluding viscosity).
"""
from .. base import BaseUnit
from .. import axioms as _axiom
from .mass import Kilogram, Pound, Gram
from .length import Meter, Foot
from .volume import CubicMeter, Liter, USGallon, CubicFoot
from .time import Second, Minute, Hour
from .force import Newton

# 1. SPECIFIC VOLUME (Kebalikan Density: m³/kg)
@_axiom.bound(min_val=0, abstract=True, msg="Density cannot be negative.")
class SpecificVolumeUnit(BaseUnit):
    dimension = "specific_volume"

@_axiom.derive(CubicMeter / Kilogram)
class CubicMeterPerKilogram(SpecificVolumeUnit):
    __base_unit__ = True
    symbol = "m³/kg"
    aliases = ["m3/kg"]

@_axiom.derive(Liter / Kilogram)
class LiterPerKilogram(SpecificVolumeUnit):
    symbol = "L/kg"

@_axiom.derive(Foot**3 / Pound)
class CubicFootPerPound(SpecificVolumeUnit):
    symbol = "ft³/lb"

# 2. MASS FLOW RATE (kg/s)
@_axiom.bound(min_val=0, abstract=True, msg="Mass flow in/out is typically measured as a positive value.")
class MassFlowRateUnit(BaseUnit):
    dimension = "mass_flow_rate"

@_axiom.derive(Kilogram / Second)
class KilogramPerSecond(MassFlowRateUnit):
    __base_unit__ = True
    symbol = "kg/s"

@_axiom.derive(Kilogram / Hour)
class KilogramPerHour(MassFlowRateUnit):
    symbol = "kg/h"

@_axiom.derive(Gram / Second)
class GramPerSecond(MassFlowRateUnit):
    symbol = "g/s"

@_axiom.derive(Pound / Second)
class PoundPerSecond(MassFlowRateUnit):
    symbol = "lb/s"

@_axiom.derive(Pound / Hour)
class PoundPerHour(MassFlowRateUnit):
    symbol = "lb/h"

# 3. VOLUMETRIC FLOW RATE (m³/s)
@_axiom.bound(min_val=0, abstract=True, msg="Mass flow in/out is typically measured as a positive value.")
class VolumetricFlowRateUnit(BaseUnit):
    dimension = "volumetric_flow_rate"

@_axiom.derive(CubicMeter / Second)
class CubicMeterPerSecond(VolumetricFlowRateUnit):
    __base_unit__ = True
    symbol = "m³/s"
    aliases = ["m3/s", "cumecs"]

# --- VOLUMETRIC FLOW RATE ---
@_axiom.derive(Liter / Second)
class LiterPerSecond(VolumetricFlowRateUnit):
    symbol = "L/s"

@_axiom.derive(Liter / Minute)
class LiterPerMinute(VolumetricFlowRateUnit):
    symbol = "L/min"
    aliases = ["lpm"]

@_axiom.derive(USGallon / Minute)
class GallonsPerMinute(VolumetricFlowRateUnit):
    symbol = "gpm"
    aliases = ["GPM", "gal/min", "gallons per minute"]

@_axiom.derive(CubicFoot / Minute)
class CubicFeetPerMinute(VolumetricFlowRateUnit):
    symbol = "cfm"
    aliases = ["CFM", "ft³/min", "cubic feet per minute"]


# 4. SURFACE TENSION (N/m)
@_axiom.bound(abstract=True)
class ForcePerLengthUnit(BaseUnit):
    dimension = "force_per_length"

@_axiom.derive(Newton / Meter)
class NewtonPerMeter(ForcePerLengthUnit):
    __base_unit__ = True
    symbol = "N/m"
    aliases = ["newton_per_meter", "surface_tension", "stiffness", "spring_constant"]

@_axiom.derive(0.001 * NewtonPerMeter)
class MillinewtonPerMeter(ForcePerLengthUnit):
    symbol = "mN/m"
    aliases = ["dyn/cm", "millinewton_per_meter"]