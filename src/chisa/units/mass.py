"""
Mass Dimension Module.

This module provides units for quantifying the amount of matter in an object.
It supports everyday metric and imperial weights, jewelry standards (Carats), 
microscopic scales (Daltons, Planck mass), and cosmic scales (Solar Mass, Earth Mass).
The absolute base unit for this dimension is the Kilogram (kg).
"""

from ..core.base import BaseUnit
from ..core import axioms as _axiom
from ..core import constants as _const

@_axiom.bound(min_val=0, msg="Mass cannot be a negative value.")
class MassUnit(BaseUnit):
    """
    The primary parent class for the Mass dimension.
    The base unit is Kilogram (kg).
    """
    dimension = "mass"

# =========================================================================
# 1. METRIC UNITS (SI) 
# =========================================================================
class Kilogram(MassUnit):
    symbol = "kg"
    aliases = ["kilogram", "kilograms", "kilo", "kilos", "KG", "Kg"]
    base_multiplier = 1.0

class Gram(MassUnit):
    symbol = "g"
    aliases = ["gram", "grams", "gm", "gms", "G", "gr"]
    base_multiplier = 1e-3

class Milligram(MassUnit):
    symbol = "mg"
    aliases = ["milligram", "milligrams", "mgs"]
    base_multiplier = 1e-6

class MetricTon(MassUnit):
    symbol = "t"
    aliases = ["ton", "tons", "metricton", "metric ton", "metric tons", "tonne", "tonnes", "MT", "mt"]
    base_multiplier = 1000.0

class Quintal(MassUnit):
    symbol = "q"
    aliases = ["quintal", "quintals"]
    base_multiplier = 100.0

class Ons(MassUnit):
    symbol = "ons"
    aliases = ["ons-nl", "ounce (metric)", "metric ounce"]
    base_multiplier = 0.1


# =========================================================================
# 2. IMPERIAL & US CUSTOMARY UNITS
# =========================================================================
class Pound(MassUnit):
    symbol = "lb"
    aliases = ["pound", "pounds", "lbs", "lb.", "lbs.", "lbm"]
    base_multiplier = _const.POUND_TO_KG

class Ounce(MassUnit):
    symbol = "oz"
    aliases = ["ounce", "ounces", "oz.", "ozs"]
    base_multiplier = _const.OUNCE_TO_KG

class TroyOunce(MassUnit):
    symbol = "oz_t"
    aliases = ["ozt", "troy ounce", "troy ounces", "troy_ounce", "oz t", "troy-oz"]
    base_multiplier = _const.TROY_OUNCE_TO_KG

class Stone(MassUnit):
    symbol = "st"
    aliases = ["stone", "stones", "st."]
    base_multiplier = _const.STONE_TO_KG

class Slug(MassUnit):
    symbol = "slug"
    aliases = ["slugs"]
    base_multiplier = _const.SLUG_TO_KG

class Dram(MassUnit):
    symbol = "dr"
    aliases = ["dram", "drams", "dr.", "drachm"]
    base_multiplier = _const.POUND_TO_KG / 256.0

class ShortTon(MassUnit):
    symbol = "shortton"
    aliases = ["short ton", "short tons", "us ton", "us tons", "ton (US)"]
    base_multiplier = _const.SHORT_TON_TO_KG

class LongTon(MassUnit):
    symbol = "longton"
    aliases = ["long ton", "long tons", "uk ton", "uk tons", "ton (UK)", "imperial ton"]
    base_multiplier = _const.LONG_TON_TO_KG


# =========================================================================
# 3. SMALLER / JEWELRY UNITS
# =========================================================================
class Carat(MassUnit):
    symbol = "ct"
    aliases = ["carat", "carats", "ct."]
    base_multiplier = _const.CARAT_TO_KG

class Grain(MassUnit):
    symbol = "gr"
    aliases = ["grain", "grains", "gr."]
    base_multiplier = _const.GRAIN_TO_KG


# =========================================================================
# 4. ASTRONOMICAL MASS UNITS
# =========================================================================
class SolarMass(MassUnit):
    symbol = "M_sun"
    aliases = ["solarmass", "solar-mass", "solar mass", "M☉", "M_sol"]
    base_multiplier = _const.SOLAR_MASS_KG

class EarthMass(MassUnit):
    symbol = "M_earth"
    aliases = ["earthmass", "earth-mass", "earth mass", "M⊕"]
    base_multiplier = _const.EARTH_MASS_KG

class LunarMass(MassUnit):
    symbol = "M_moon"
    aliases = ["lunarmass", "lunar-mass", "lunar mass", "M☾"]
    base_multiplier = _const.LUNAR_MASS_KG

class JupiterMass(MassUnit):
    symbol = "M_jup"
    aliases = ["jupitermass", "jupiter-mass", "jupiter mass", "Mj", "M♃"]
    base_multiplier = _const.JUPITER_MASS_KG

class SaturnMass(MassUnit):
    symbol = "M_sat"
    aliases = ["saturnmass", "saturn-mass", "saturn mass", "Msat", "M♄"]
    base_multiplier = _const.SATURN_MASS_KG

class UranusMass(MassUnit):
    symbol = "M_ura"
    aliases = ["uranusmass", "uranus-mass", "uranus mass", "Mura"]
    base_multiplier = _const.URANUS_MASS_KG

class NeptuneMass(MassUnit):
    symbol = "M_nep"
    aliases = ["neptunemass", "neptune-mass", "neptune mass", "Mnep"]
    base_multiplier = _const.NEPTUNE_MASS_KG

class VenusMass(MassUnit):
    symbol = "M_ven"
    aliases = ["venusmass", "venus-mass", "venus mass", "Mven"]
    base_multiplier = _const.VENUS_MASS_KG

class MarsMass(MassUnit):
    symbol = "M_mars"
    aliases = ["marsmass", "mars-mass", "mars mass", "Mmars"]
    base_multiplier = _const.MARS_MASS_KG

class MercuryMass(MassUnit):
    symbol = "M_mer"
    aliases = ["mercurymass", "mercury-mass", "mercury mass", "Mmer"]
    base_multiplier = _const.MERCURY_MASS_KG

class PlutoMass(MassUnit):
    symbol = "M_plu"
    aliases = ["plutomass", "pluto-mass", "pluto mass", "Mplu"]
    base_multiplier = _const.PLUTO_MASS_KG

class CeresMass(MassUnit):
    symbol = "M_cer"
    aliases = ["ceresmass", "ceres-mass", "ceres mass", "Mcer"]
    base_multiplier = _const.CERES_MASS_KG


# =========================================================================
# 5. ATOMIC / QUANTUM UNITS
# =========================================================================
class AtomicMassUnit(MassUnit):
    symbol = "amu"
    aliases = ["u", "Da", "dalton", "daltons", "atomicmassunit", "atomic mass unit", "atomic-mass-unit"]
    base_multiplier = _const.ATOMIC_MASS_UNIT_KG

class PlanckMass(MassUnit):
    symbol = "m_p"
    aliases = ["planckmass", "planck-mass", "planck mass"]
    base_multiplier = _const.PLANCK_MASS_KG

class ElectronVoltPerCSquared(MassUnit):
    symbol = "eV/c^2"
    aliases = [
        "ev/c^2", "ev/c2", "ev/c²", "eV/c2", "eV/c²",
        "electronvoltpercsquared", "electron-volt-per-c-squared",
        "electron volt per c squared", "electron volt/c^2", "electron volt/c2",
        "eV/c**2"
    ]
    base_multiplier = _const.ELECTRON_VOLT_C2_KG


# =========================================================================
# 6. OBSOLETE / REGIONAL UNITS
# =========================================================================
class BaleCotton(MassUnit):
    symbol = "bale-cotton"
    aliases = ["bale", "bale_cotton", "cotton bale"]
    base_multiplier = 217.72

class BaleWool(MassUnit):
    symbol = "bale-wool"
    aliases = ["bale_wool", "wool bale"]
    base_multiplier = 204.0

class BaleUK(MassUnit):
    symbol = "bale-uk"
    aliases = ["bale_uk", "uk bale"]
    base_multiplier = 226.8

class BaleAus(MassUnit):
    symbol = "bale-aus"
    aliases = ["bale_aus", "aus bale", "australian bale"]
    base_multiplier = 204.0

class MarkDE(MassUnit):
    symbol = "mark-de"
    aliases = ["mark", "mark_de", "german mark (mass)"]
    base_multiplier = 0.25

class MarkNO(MassUnit):
    symbol = "mark-no"
    aliases = ["mark_no", "norwegian mark"]
    base_multiplier = 0.213

class ArrobaES(MassUnit):
    symbol = "arroba-es"
    aliases = ["arroba", "arroba_es", "spanish arroba"]
    base_multiplier = 11.5

class ArrobaPT(MassUnit):
    symbol = "arroba-pt"
    aliases = ["arrobas", "arroba_pt", "portuguese arroba"]
    base_multiplier = 15.0