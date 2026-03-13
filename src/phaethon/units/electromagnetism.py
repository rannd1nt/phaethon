"""
Electromagnetism Dimension Module.

This module handles electrical engineering units crucial for IoT, battery sensors, 
and power grid analytics. It defines distinct physical dimensions for Current, 
Charge, Potential (Voltage), Resistance, and Capacitance.
"""
from ..core.base import BaseUnit
from ..core import axioms as _axiom

from .time import Second, Hour
from .power import Watt

# =========================================================================
# 1. ELECTRIC CURRENT (Base: Ampere)
# =========================================================================
@_axiom.bound(min_val=0, msg="Absolute electric current magnitude cannot be negative.")
class ElectricCurrentUnit(BaseUnit):
    dimension = "electric_current"

class Ampere(ElectricCurrentUnit):
    symbol = "A"
    aliases = ["a", "amp", "amps", "ampere", "amperes"]
    base_multiplier = 1.0

@_axiom.derive(mul=[1e-3, Ampere])
class Milliampere(ElectricCurrentUnit):
    symbol = "mA"
    aliases = ["ma", "milliamp", "milliamps", "milliampere"]

# =========================================================================
# 2. ELECTRIC CHARGE (Base: Coulomb)
# =========================================================================
class ElectricChargeUnit(BaseUnit):
    dimension = "electric_charge"

# Coulomb: 1 Ampere * 1 Second
@_axiom.derive(mul=[Ampere, Second])
class Coulomb(ElectricChargeUnit):
    symbol = "C"
    aliases = ["c", "coulomb", "coulombs"]

# Ampere-hour: Battery capacity standard
@_axiom.derive(mul=[Ampere, Hour])
class AmpereHour(ElectricChargeUnit):
    symbol = "Ah"
    aliases = ["ah", "amp-hour", "ampere-hour", "ampere hour", "amp hours"]

@_axiom.derive(mul=[1e-3, Ampere, Hour])
class MilliampereHour(ElectricChargeUnit):
    symbol = "mAh"
    aliases = ["mah", "milliamp-hour", "milliampere-hour"]

# =========================================================================
# 3. ELECTRIC POTENTIAL / VOLTAGE (Base: Volt)
# =========================================================================
class ElectricPotentialUnit(BaseUnit):
    dimension = "electric_potential"

# Volt: 1 Watt / 1 Ampere
@_axiom.derive(mul=[Watt], div=[Ampere])
class Volt(ElectricPotentialUnit):
    symbol = "V"
    aliases = ["v", "volt", "volts", "voltage"]

@_axiom.derive(mul=[1e-3, Volt])
class Millivolt(ElectricPotentialUnit):
    symbol = "mV"
    aliases = ["mv", "millivolt", "millivolts"]

@_axiom.derive(mul=[1e3, Volt])
class Kilovolt(ElectricPotentialUnit):
    symbol = "kV"
    aliases = ["kv", "kilovolt", "kilovolts"]

# =========================================================================
# 4. ELECTRICAL RESISTANCE (Base: Ohm)
# =========================================================================
@_axiom.bound(min_val=0, msg="Electrical resistance cannot be negative.")
class ElectricalResistanceUnit(BaseUnit):
    dimension = "electrical_resistance"

# Ohm: 1 Volt / 1 Ampere
@_axiom.derive(mul=[Volt], div=[Ampere])
class Ohm(ElectricalResistanceUnit):
    symbol = "Ω"
    aliases = ["ohm", "ohms", "Ohm"]

@_axiom.derive(mul=[1e3, Ohm])
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
@_axiom.derive(mul=[Coulomb], div=[Volt])
class Farad(ElectricalCapacitanceUnit):
    symbol = "F"
    aliases = ["f", "farad", "farads"]

@_axiom.derive(mul=[1e-6, Farad])
class Microfarad(ElectricalCapacitanceUnit):
    symbol = "µF"
    aliases = ["uf", "microfarad", "microfarads", "mfd"]