"""
Electromagnetism Dimension Module.

This module handles electrical engineering units crucial for IoT, battery sensors, 
and power grid analytics. It defines distinct physical dimensions for Current, 
Charge, Potential (Voltage), Resistance, and Capacitance.
"""
from .. base import BaseUnit
from .. import axioms as _axiom
import numpy as _np

from .length import Meter, Centimeter
from .area import SquareMeter
from .time import Second, Hour
from .power import Watt

# =========================================================================
# 1. ELECTRIC CURRENT (Base: Ampere)
# =========================================================================
@_axiom.bound(min_val=0, msg="Absolute electric current magnitude cannot be negative.")
class ElectricCurrentUnit(BaseUnit):
    dimension = "electric_current"

class Ampere(ElectricCurrentUnit):
    __base_unit__ = True
    symbol = "A"
    aliases = ["a", "amp", "amps", "ampere", "amperes"]
    base_multiplier = 1.0

@_axiom.derive(1e-3 * Ampere)
class Milliampere(ElectricCurrentUnit):
    symbol = "mA"
    aliases = ["ma", "milliamp", "milliamps", "milliampere"]

# =========================================================================
# 2. ELECTRIC CHARGE (Base: Coulomb)
# =========================================================================
class ElectricChargeUnit(BaseUnit):
    dimension = "electric_charge"

# Coulomb: 1 Ampere * 1 Second
@_axiom.derive(Ampere * Second)
class Coulomb(ElectricChargeUnit):
    __base_unit__ = True
    symbol = "C"
    aliases = ["c", "coulomb", "coulombs"]

# Ampere-hour: Battery capacity standard
@_axiom.derive(Ampere * Hour)
class AmpereHour(ElectricChargeUnit):
    symbol = "Ah"
    aliases = ["ah", "amp-hour", "ampere-hour", "ampere hour", "amp hours"]

@_axiom.derive(1e-3 * Ampere * Hour)
class MilliampereHour(ElectricChargeUnit):
    symbol = "mAh"
    aliases = ["mah", "milliamp-hour", "milliampere-hour"]

# =========================================================================
# 3. ELECTRIC POTENTIAL / VOLTAGE (Base: Volt)
# =========================================================================
class ElectricPotentialUnit(BaseUnit):
    dimension = "electric_potential"

    def rms(self) -> 'ElectricPotentialUnit':
        """Returns the Root Mean Square (RMS) value for a sinusoidal wave."""
        merged_context = {**self.context, "__is_math_op__": True}
        return self.__class__(self._value / _np.sqrt(2), context=merged_context)

    def peak(self) -> 'ElectricPotentialUnit':
        """Returns the peak value from an RMS reading."""
        merged_context = {**self.context, "__is_math_op__": True}
        return self.__class__(self._value * _np.sqrt(2), context=merged_context)

# Volt: 1 Watt / 1 Ampere
@_axiom.derive(Watt / Ampere)
class Volt(ElectricPotentialUnit):
    __base_unit__ = True
    symbol = "V"
    aliases = ["v", "volt", "volts", "voltage"]

@_axiom.derive(1e-3 * Volt)
class Millivolt(ElectricPotentialUnit):
    symbol = "mV"
    aliases = ["mv", "millivolt", "millivolts"]

@_axiom.derive(1e3 * Volt)
class Kilovolt(ElectricPotentialUnit):
    symbol = "kV"
    aliases = ["kv", "kilovolt", "kilovolts"]

@_axiom.logarithmic(reference=Volt(1), multiplier=20.0)
class DecibelVolt(ElectricPotentialUnit):
    symbol = "dBV"
    aliases = ["dbv"]

# =========================================================================
# 4. ELECTRICAL RESISTANCE (Base: Ohm)
# =========================================================================
@_axiom.bound(min_val=0, msg="Electrical resistance cannot be negative.")
class ElectricalResistanceUnit(BaseUnit):
    dimension = "electrical_resistance"

# Ohm: 1 Volt / 1 Ampere
@_axiom.derive(Volt / Ampere)
class Ohm(ElectricalResistanceUnit):
    __base_unit__ = True
    symbol = "Ω"
    aliases = ["ohm", "ohms", "Ohm"]

@_axiom.derive(1e3 * Ohm)
class Kiloohm(ElectricalResistanceUnit):
    symbol = "kΩ"
    aliases = ["kohm", "kiloohm", "kiloohms"]

# =========================================================================
# 5. ELECTRICAL CAPACITANCE (Base: Farad)
# =========================================================================
@_axiom.bound(min_val=0, msg="Capacitance cannot be negative.")
class ElectricalCapacitanceUnit(BaseUnit):
    dimension = "electrical_capacitance"

# Farad: 1 Coulomb / 1 Volt
@_axiom.derive(Coulomb / Volt)
class Farad(ElectricalCapacitanceUnit):
    __base_unit__ = True
    symbol = "F"
    aliases = ["f", "farad", "farads"]

@_axiom.derive(1e-6 * Farad)
class Microfarad(ElectricalCapacitanceUnit):
    symbol = "µF"
    aliases = ["uf", "microfarad", "microfarads", "mfd"]

# =========================================================================
# 6. MAGNETIC FLUX (Base: Weber)
# =========================================================================
class MagneticFluxUnit(BaseUnit):
    dimension = "magnetic_flux"

@_axiom.derive(Volt * Second)
class Weber(MagneticFluxUnit):
    __base_unit__ = True
    symbol = "Wb"
    aliases = ["weber", "webers", "wb"]

@_axiom.derive(1e-8 * Weber)
class Maxwell(MagneticFluxUnit):
    symbol = "Mx"
    aliases = ["maxwell"]

# =========================================================================
# 7. MAGNETIC FLUX DENSITY (Base: Tesla)
# =========================================================================
class MagneticFluxDensityUnit(BaseUnit):
    dimension = "magnetic_flux_density"

@_axiom.derive(Weber / SquareMeter)
class Tesla(MagneticFluxDensityUnit):
    __base_unit__ = True
    symbol = "T"
    aliases = ["tesla", "teslas", "t"]

@_axiom.derive(1e-3 * Tesla)
class Millitesla(MagneticFluxDensityUnit):
    symbol = "mT"
    aliases = ["mt", "millitesla", "milliteslas"]

# =========================================================================
# 8. ELECTRICAL INDUCTANCE (Base: Henry)
# =========================================================================
@_axiom.bound(min_val=0, msg="Inductance cannot be negative.")
class ElectricalInductanceUnit(BaseUnit):
    dimension = "electrical_inductance"

# Henry: 1 Weber / 1 Ampere
@_axiom.derive(Weber / Ampere)
class Henry(ElectricalInductanceUnit):
    __base_unit__ = True
    symbol = "H"
    aliases = ["henry", "henries", "h"]

@_axiom.derive(1e-3 * Henry)
class Millihenry(ElectricalInductanceUnit):
    symbol = "mH"
    aliases = ["mh", "millihenry", "millihenries"]

# =========================================================================
# 9. ELECTRIC FIELD (Base: Volt / Meter)
# =========================================================================
class ElectricFieldUnit(BaseUnit):
    dimension = "electric_field"

@_axiom.derive(Volt / Meter)
class VoltPerMeter(ElectricFieldUnit):
    __base_unit__ = True
    symbol = "V/m"

@_axiom.derive(Volt / Centimeter)
class VoltPerCentimeter(ElectricFieldUnit):
    symbol = "V/cm"
    aliases = ["volt_per_centimeter"]

# =========================================================================
# 10. CURRENT DENSITY (Base: Ampere / SquareMeter)
# =========================================================================
class CurrentDensityUnit(BaseUnit):
    dimension = "current_density"

@_axiom.derive(Ampere / SquareMeter)
class AmperePerSquareMeter(CurrentDensityUnit):
    __base_unit__ = True
    symbol = "A/m²"

@_axiom.derive(Ampere / Centimeter**2)
class AmperePerSquareCentimeter(CurrentDensityUnit):
    symbol = "A/cm²"
    aliases = ["ampere_per_square_centimeter"]

# =========================================================================
# 11. MAGNETIC FIELD STRENGTH (Base: Ampere / Meter) -> H-Field
# =========================================================================
class MagneticFieldStrengthUnit(BaseUnit):
    dimension = "magnetic_field_strength"

@_axiom.derive(Ampere / Meter)
class AmperePerMeter(MagneticFieldStrengthUnit):
    __base_unit__ = True
    symbol = "A/m"

@_axiom.derive((1000 / (4 * _np.pi)) * AmperePerMeter)
class Oersted(MagneticFieldStrengthUnit):
    symbol = "Oe"
    aliases = ["oersted"]

# =========================================================================
# 12. ELECTRICAL PERMITTIVITY (Base: Farad / Meter)
# =========================================================================
class ElectricalPermittivityUnit(BaseUnit):
    dimension = "electrical_permittivity"

@_axiom.derive(Farad / Meter)
class FaradPerMeter(ElectricalPermittivityUnit):
    __base_unit__ = True
    symbol = "F/m"

class ElectricDipoleMomentUnit(BaseUnit):
    """Dimension for Electric Dipole Moment."""
    dimension = "electric_dipole_moment"

@_axiom.derive(Coulomb * Meter)
class CoulombMeter(ElectricDipoleMomentUnit):
    """The SI Base Unit for Electric Dipole Moment."""
    __base_unit__ = True
    symbol = "C·m"
    aliases = ["coulomb-meter"]