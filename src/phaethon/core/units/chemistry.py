"""
Chemistry and Material Science Module.
Defines units representing amount of substance, molarity, and chemical kinetics.
The absolute base dimension is the Mole (mol).
"""
from ..base import BaseUnit
from .. import axioms as _axiom
from .mass import Kilogram, Gram, Pound
from .volume import CubicMeter, Liter
from .energy import Joule
from .temperature import Kelvin
from .time import Second, Minute

# =========================================================================
# 1. AMOUNT OF SUBSTANCE
# =========================================================================
@_axiom.bound(min_val=0, msg="Amount of substance cannot be negative.", abstract=True)
class AmountOfSubstanceUnit(BaseUnit):
    """The primary class for chemical amounts. Base unit is Mole (mol)."""
    dimension = "amount_of_substance"

class Mole(AmountOfSubstanceUnit):
    __base_unit__ = True
    symbol = "mol"
    aliases = ["mole", "moles"]

@_axiom.derive(1e-3 * Mole)
class Millimole(AmountOfSubstanceUnit):
    symbol = "mmol"
    aliases = ["millimole", "millimoles"]

@_axiom.derive(1000.0 * Mole)
class Kilomole(AmountOfSubstanceUnit):
    symbol = "kmol"
    aliases = ["kilomole", "kilomoles"]

@_axiom.derive(1e6 * Mole)
class Megamole(AmountOfSubstanceUnit):
    symbol = "Mmol"
    aliases = ["megamole", "megamoles"]

@_axiom.derive(453.59237 * Mole)
class PoundMole(AmountOfSubstanceUnit):
    symbol = "lbmol"
    aliases = ["pound_mole", "lb_mol"]

@_axiom.derive(28.349523125 * Mole)
class OunceMole(AmountOfSubstanceUnit):
    symbol = "ozmol"
    aliases = ["ounce_mole", "oz_mol"]

@_axiom.derive(907184.74 * Mole)
class ShortTonMole(AmountOfSubstanceUnit):
    symbol = "tonmol"
    aliases = ["ton_mole", "short_ton_mole"]

# =========================================================================
# 2. MOLAR MASS
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Physical Property Error: Molar mass must be a positive value.")
class MolarMassUnit(BaseUnit):
    dimension = "molar_mass"

@_axiom.derive(Kilogram / Mole)
class KilogramPerMole(MolarMassUnit):
    __base_unit__ = True
    symbol = "kg/mol"

@_axiom.derive(Gram / Mole)
class GramPerMole(MolarMassUnit):
    symbol = "g/mol"

@_axiom.derive(Pound / PoundMole)
class PoundPerPoundMole(MolarMassUnit):
    symbol = "lb/lbmol"



# =========================================================================
# 3. MOLARITY (CONCENTRATION & pH)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Chemical Concentration Error: Molarity cannot be negative.")
class MolarityUnit(BaseUnit):
    dimension = "molarity"

@_axiom.derive(Mole / CubicMeter)
class MolesPerCubicMeter(MolarityUnit):
    __base_unit__ = True
    symbol = "mol/m³"

@_axiom.derive(Mole / Liter)
class Molar(MolarityUnit):
    symbol = "M"
    aliases = ["molar", "mol/L"]

@_axiom.derive(1e-3 * Molar)
class Millimolar(MolarityUnit):
    symbol = "mM"

@_axiom.derive(1e-6 * Molar)
class Micromolar(MolarityUnit):
    symbol = "µM"
    aliases = ["uM"]

@_axiom.logarithmic(reference=MolesPerCubicMeter(1000), multiplier=-1.0)
class pH(MolarityUnit):
    symbol = "pH"
    aliases = ["ph"]

@_axiom.logarithmic(reference=MolesPerCubicMeter(1000), multiplier=-1.0)
class pOH(MolarityUnit):
    symbol = "pOH"
    aliases = ["poh"]

# =========================================================================
# 4. CATALYTIC ACTIVITY (Kinetika Kimia)
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Kinetics Violation: Catalytic activity (Katal) cannot be negative.")
class CatalyticActivityUnit(BaseUnit):
    dimension = "catalytic_activity"

@_axiom.derive(Mole / Second)
class Katal(CatalyticActivityUnit):
    __base_unit__ = True
    symbol = "kat"
    aliases = ["katal"]

@_axiom.derive((1e-6 * Mole) / Minute)
class EnzymeUnit(CatalyticActivityUnit):
    symbol = "U"
    aliases = ["enzyme_unit"]

# =========================================================================
# 5. MOLAR HEAT CAPACITY
# =========================================================================
@_axiom.bound(min_val=0, abstract=True, msg="Thermodynamic Error: Molar heat capacity must be positive for stable matter.")
class MolarHeatCapacityUnit(BaseUnit):
    dimension = "molar_heat_capacity"

@_axiom.derive(Joule / (Mole * Kelvin))
class JoulePerMoleKelvin(MolarHeatCapacityUnit):
    __base_unit__ = True
    symbol = "J/(mol·K)"
    aliases = ["J/mol.K"]

class MolarVolumeUnit(BaseUnit):
    """Dimension for the volume occupied by one mole of a substance."""
    dimension = "molar_volume"

@_axiom.derive(CubicMeter / Mole)
class CubicMeterPerMole(MolarVolumeUnit):
    """The SI Base Unit for Molar Volume."""
    __base_unit__ = True
    symbol = "m³/mol"
    aliases = ["cubic meter per mole"]

@_axiom.derive(Liter / Mole)
class LiterPerMole(MolarVolumeUnit):
    symbol = "L/mol"