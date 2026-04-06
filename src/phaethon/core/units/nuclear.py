"""
Nuclear and Radiation Physics Module.

This module provides units for measuring ionizing radiation.
Crucial for medical physics (PINNs for oncology), nuclear reactor simulations, 
and environmental radiation monitoring.
Defines Radioactivity, Absorbed Dose, Equivalent Dose, and Radiation Exposure.
"""

from ..base import BaseUnit
from .. import axioms as _axiom

from .time import Second, Minute
from .scalar import Decay, Radiation, BiologicalEffect
from .energy import Joule
from .mass import Kilogram
from .electromagnetism import Coulomb

# =========================================================================
# 1. RADIOACTIVITY (Decays per second)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Nuclear Violation: Radioactive decay rate cannot be negative.")
class RadioactivityUnit(BaseUnit):
    dimension = "radioactivity"

@_axiom.derive(Decay / Second)
class Becquerel(RadioactivityUnit):
    __base_unit__ = True
    symbol = "Bq"
    aliases = ["bq", "becquerel", "becquerels"]

@_axiom.derive(3.7e10 * Becquerel)
class Curie(RadioactivityUnit):
    symbol = "Ci"
    aliases = ["ci", "curie", "curies"]

@_axiom.derive(1e6 * Becquerel)
class Rutherford(RadioactivityUnit):
    symbol = "Rd"
    aliases = ["rd", "rutherford", "rutherfords"]

# =========================================================================
# 2. ABSORBED DOSE (Energy deposited per unit mass)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Radiology Error: Absorbed radiation dose (Gray) cannot be negative.")
class AbsorbedDoseUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "absorbed_dose"

@_axiom.derive((Joule * Radiation) / Kilogram)
class Gray(AbsorbedDoseUnit):
    __base_unit__ = True
    symbol = "Gy"
    aliases = ["gy", "gray", "grays"]

@_axiom.derive(0.01 * Gray)
class Rad(AbsorbedDoseUnit):
    symbol = "rad"
    aliases = ["rads"]

# =========================================================================
# 3. EQUIVALENT DOSE (Biological effect of radiation)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Biophysical Violation: Equivalent biological dose (Sievert) cannot be negative.")
class EquivalentDoseUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "equivalent_dose"

@_axiom.derive((Joule * BiologicalEffect) / Kilogram)
class Sievert(EquivalentDoseUnit):
    __base_unit__ = True
    symbol = "Sv"
    aliases = ["sv", "sievert", "sieverts"]

@_axiom.derive(0.01 * Sievert)
class RoentgenEquivalentMan(EquivalentDoseUnit):
    symbol = "rem"
    aliases = ["rems", "roentgen_equivalent_man"]

# =========================================================================
# 4. RADIATION EXPOSURE (Ionization of air)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Safety Violation: Radiation exposure level cannot be negative.")
class RadiationExposureUnit(BaseUnit):
    dimension = "radiation_exposure"

@_axiom.derive(Coulomb / Kilogram)
class CoulombPerKilogram(RadiationExposureUnit):
    __base_unit__ = True
    symbol = "C/kg"
    aliases = ["c/kg"]

@_axiom.derive(2.58e-4 * CoulombPerKilogram)
class Roentgen(RadiationExposureUnit):
    symbol = "R"
    aliases = ["roentgen", "roentgens"]

@_axiom.derive(0.001 * Roentgen)
class Milliroentgen(RadiationExposureUnit):
    symbol = "mR"
    aliases = ["milliroentgen"]


@_axiom.bound(min_val=0, abstract=True)
class AbsorbedDoseRateUnit(BaseUnit):
    dimension = "absorbed_dose_rate"

@_axiom.derive(Gray / Second)
class GrayPerSecond(AbsorbedDoseRateUnit):
    __base_unit__ = True
    symbol = "Gy/s"

@_axiom.derive(Rad / Second)
class RadPerSecond(AbsorbedDoseRateUnit):
    symbol = "rad/s"

@_axiom.derive(Gray / Minute)
class GrayPerMinute(AbsorbedDoseRateUnit):
    symbol = "Gy/min"