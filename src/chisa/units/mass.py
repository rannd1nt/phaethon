"""
Mass Dimension Module.

This module provides units for quantifying the amount of matter in an object.
It supports everyday metric and imperial weights, jewelry standards (Carats), 
microscopic scales (Daltons, Planck mass), and cosmic scales (Solar Mass, Earth Mass).
The absolute base unit for this dimension is the Kilogram (kg).
"""

from ..core.base import BaseUnit
from ..core import axioms as axiom
from ..core import constants as const # <-- The SSOT

@axiom.bound(min_val=0, msg="Mass cannot be a negative value.")
class MassUnit(BaseUnit):
    """
    The primary parent class for the Mass dimension.
    The base unit is Kilogram (kg).
    """
    dimension = "mass"

# =========================================================================
# 1. METRIC UNITS (SI) 
# (Metric is intrinsically base-10, so magic numbers are acceptable here)
# =========================================================================
class Kilogram(MassUnit):
    symbol = "kg"
    aliases = ["kilogram", "kilograms"]
    base_multiplier = 1.0

class Gram(MassUnit):
    symbol = "g"
    aliases = ["gram", "grams"]
    base_multiplier = 1e-3

class Milligram(MassUnit):
    symbol = "mg"
    aliases = ["milligram", "milligrams"]
    base_multiplier = 1e-6

class MetricTon(MassUnit):
    symbol = "t"
    aliases = ["ton", "tons", "metricton"]
    base_multiplier = 1000.0

class Quintal(MassUnit):
    symbol = "quintal"
    base_multiplier = 100.0

class Ons(MassUnit):
    symbol = "ons"
    aliases = ["ons-nl"]
    base_multiplier = 0.1


# =========================================================================
# 2. IMPERIAL & US CUSTOMARY UNITS
# =========================================================================
class Pound(MassUnit):
    symbol = "lb"
    aliases = ["pound", "pounds"]
    base_multiplier = const.POUND_TO_KG

class Ounce(MassUnit):
    symbol = "oz"
    aliases = ["ounce", "ounces"]
    base_multiplier = const.OUNCE_TO_KG

class TroyOunce(MassUnit):
    symbol = "oz_t"
    aliases = ["ozt", "troy ounce", "troy ounces"]
    base_multiplier = const.TROY_OUNCE_TO_KG

class Stone(MassUnit):
    symbol = "st"
    aliases = ["stone", "stones"]
    base_multiplier = const.STONE_TO_KG

class Slug(MassUnit):
    symbol = "slug"
    base_multiplier = const.SLUG_TO_KG

class Dram(MassUnit):
    symbol = "dr"
    aliases = ["dram", "drams"]
    base_multiplier = const.POUND_TO_KG / 256.0

class ShortTon(MassUnit):
    symbol = "shortton"
    aliases = ["short ton"]
    base_multiplier = const.SHORT_TON_TO_KG

class LongTon(MassUnit):
    symbol = "longton"
    aliases = ["long ton"]
    base_multiplier = const.LONG_TON_TO_KG


# =========================================================================
# 3. SMALLER / JEWELRY UNITS
# =========================================================================
class Carat(MassUnit):
    symbol = "carat"
    aliases = ["carats"]
    base_multiplier = const.CARAT_TO_KG

class Grain(MassUnit):
    symbol = "grain"
    aliases = ["grains"]
    base_multiplier = const.GRAIN_TO_KG


# =========================================================================
# 4. ASTRONOMICAL MASS UNITS
# =========================================================================
class SolarMass(MassUnit):
    symbol = "M☉"
    aliases = ["solarmass", "solar-mass"]
    base_multiplier = const.SOLAR_MASS_KG

class EarthMass(MassUnit):
    symbol = "M⊕"
    aliases = ["earthmass", "earth-mass"]
    base_multiplier = const.EARTH_MASS_KG

class LunarMass(MassUnit):
    symbol = "M☾"
    aliases = ["lunarmass", "lunar-mass"]
    base_multiplier = const.LUNAR_MASS_KG

class JupiterMass(MassUnit):
    symbol = "Mj"
    aliases = ["jupitermass", "jupiter-mass", "M♃"]
    base_multiplier = const.JUPITER_MASS_KG

class SaturnMass(MassUnit):
    symbol = "Msat"
    aliases = ["saturnmass", "saturn-mass", "M♄"]
    base_multiplier = const.SATURN_MASS_KG

class UranusMass(MassUnit):
    symbol = "Mura"
    aliases = ["uranusmass", "uranus-mass"]
    base_multiplier = const.URANUS_MASS_KG

class NeptuneMass(MassUnit):
    symbol = "Mnep"
    aliases = ["neptunemass", "neptune-mass"]
    base_multiplier = const.NEPTUNE_MASS_KG

class VenusMass(MassUnit):
    symbol = "Mven"
    aliases = ["venusmass", "venus-mass"]
    base_multiplier = const.VENUS_MASS_KG

class MarsMass(MassUnit):
    symbol = "Mmars"
    aliases = ["marsmass", "mars-mass"]
    base_multiplier = const.MARS_MASS_KG

class MercuryMass(MassUnit):
    symbol = "Mmer"
    aliases = ["mercurymass", "mercury-mass"]
    base_multiplier = const.MERCURY_MASS_KG

class PlutoMass(MassUnit):
    symbol = "Mplu"
    aliases = ["plutomass", "pluto-mass"]
    base_multiplier = const.PLUTO_MASS_KG

class CeresMass(MassUnit):
    symbol = "Mcer"
    aliases = ["ceresmass", "ceres-mass"]
    base_multiplier = const.CERES_MASS_KG


# =========================================================================
# 5. ATOMIC / QUANTUM UNITS
# =========================================================================
class AtomicMassUnit(MassUnit):
    symbol = "amu"
    aliases = ["u", "Da", "dalton", "atomicmassunit", "atomic mass unit", "atomic-mass-unit"]
    base_multiplier = const.ATOMIC_MASS_UNIT_KG

class PlanckMass(MassUnit):
    symbol = "m_p"
    aliases = ["planckmass", "planck-mass", "planck mass"]
    base_multiplier = const.PLANCK_MASS_KG

class ElectronVoltPerCSquared(MassUnit):
    symbol = "eV/c^2"
    aliases = [
        "ev/c^2", "ev/c2", "ev/c²", "eV/c2",
        "electronvoltpercsquared", "electron-volt-per-c-squared",
        "electron volt per c squared", "electron volt/c^2", "electron volt/c2"
    ]
    base_multiplier = const.ELECTRON_VOLT_C2_KG


# =========================================================================
# 6. OBSOLETE / REGIONAL UNITS
# =========================================================================
class BaleCotton(MassUnit):
    symbol = "bale-cotton"
    aliases = ["bale", "bale_cotton"]
    base_multiplier = 217.72

class BaleWool(MassUnit):
    symbol = "bale-wool"
    aliases = ["bale_wool"]
    base_multiplier = 204.0

class BaleUK(MassUnit):
    symbol = "bale-uk"
    aliases = ["bale_uk"]
    base_multiplier = 226.8

class BaleAus(MassUnit):
    symbol = "bale-aus"
    aliases = ["bale_aus"]
    base_multiplier = 204.0

class MarkDE(MassUnit):
    symbol = "mark-de"
    aliases = ["mark", "mark_de"]
    base_multiplier = 0.25

class MarkNO(MassUnit):
    symbol = "mark-no"
    aliases = ["mark_no"]
    base_multiplier = 0.213

class ArrobaES(MassUnit):
    symbol = "arroba-es"
    aliases = ["arroba", "arroba_es"]
    base_multiplier = 11.5

class ArrobaPT(MassUnit):
    symbol = "arroba-pt"
    aliases = ["arrobas", "arroba_pt"]
    base_multiplier = 15.0