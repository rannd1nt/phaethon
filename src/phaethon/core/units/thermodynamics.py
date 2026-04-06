"""
Thermodynamics and Heat Transfer Module.
Essential for thermal PINNs, HVAC simulations, and material science.
"""
from .. base import BaseUnit
from .. import axioms as _axiom
from .mass import Kilogram, Gram, Pound
from .length import Meter, Foot
from .energy import Joule, BTU, Calorie
from .power import Watt
from .temperature import Kelvin, Celsius, Fahrenheit
from .time import Hour

@_axiom.bound(min_val=0, abstract=True, msg="Entropy Violation: Statistical disorder (Entropy) cannot be negative.")
class EntropyUnit(BaseUnit):
    dimension = "entropy"

@_axiom.derive(Joule / Kelvin)
class JoulePerKelvin(EntropyUnit):
    __base_unit__ = True
    symbol = "J/K"
    aliases = ["joule_per_kelvin"]

@_axiom.derive(1.380649e-23 * JoulePerKelvin)
class BoltzmannConstantUnit(EntropyUnit):
    symbol = "k_B"

@_axiom.bound(min_val=0, abstract=True, msg="Material Science Error: Specific heat capacity must be positive for stable matter.")
class SpecificHeatCapacityUnit(BaseUnit):
    dimension = "specific_heat_capacity"

@_axiom.derive(Joule / (Kilogram * Kelvin))
class JoulePerKilogramKelvin(SpecificHeatCapacityUnit):
    __base_unit__ = True
    symbol = "J/(kg·K)"
    aliases = ["J/kg.K", "specific_heat"]

@_axiom.derive(Calorie / (Gram * Celsius))
class CaloriePerGramCelsius(SpecificHeatCapacityUnit):
    symbol = "cal/(g·°C)"

@_axiom.derive(BTU / (Pound * Fahrenheit))
class BTUPerPoundFahrenheit(SpecificHeatCapacityUnit):
    symbol = "BTU/(lb·°F)"

@_axiom.bound(min_val=0, abstract=True, msg="Heat Transfer Violation: Thermal conductivity must be positive (Heat flows from hot to cold).")
class ThermalConductivityUnit(BaseUnit):
    dimension = "thermal_conductivity"

@_axiom.derive(Watt / (Meter * Kelvin))
class WattPerMeterKelvin(ThermalConductivityUnit):
    __base_unit__ = True
    symbol = "W/(m·K)"
    aliases = ["W/m.K", "thermal_conductivity"]

@_axiom.bound(min_val=0, abstract=True, msg="Engineering Error: Heat transfer coefficient (U-value) cannot be negative.")
class HeatTransferCoefficientUnit(BaseUnit):
    dimension = "heat_transfer_coefficient"

@_axiom.derive(Watt / (Meter**2 * Kelvin))
class WattPerSquareMeterKelvin(HeatTransferCoefficientUnit):
    __base_unit__ = True
    symbol = "W/(m²·K)"
    aliases = ["W/m2.K"]

@_axiom.derive(BTU / (Hour * Foot * Fahrenheit))
class BTUPerHourFootFahrenheit(ThermalConductivityUnit):
    symbol = "BTU/(h·ft·°F)"


class HeatFluxDensityUnit(BaseUnit):
    dimension = "heat_flux_density"

@_axiom.derive(Watt / Meter**2)
class WattPerSquareMeter(HeatFluxDensityUnit):
    __base_unit__ = True
    symbol = "W/m²"
    aliases = ["W/m2", "heat_flux"]

@_axiom.derive(BTU / (Hour * Foot**2))
class BTUPerHourSquareFoot(HeatFluxDensityUnit):
    symbol = "BTU/(h·ft²)"


@_axiom.bound(min_val=0, abstract=True, msg="Thermodynamic Error: Specific energy/enthalpy magnitude cannot be negative.")
class SpecificEnergyUnit(BaseUnit):
    dimension = "specific_energy"

@_axiom.derive(Joule / Kilogram)
class JoulePerKilogram(SpecificEnergyUnit):
    __base_unit__ = True
    symbol = "J/kg"
    aliases = ["joule_per_kilogram"]

@_axiom.derive(BTU / Pound)
class BTUPerPound(SpecificEnergyUnit):
    symbol = "BTU/lb"

@_axiom.derive(1e-3 * JoulePerKilogram)
class MillijoulePerKilogram(SpecificEnergyUnit):
    symbol = "mJ/kg"

@_axiom.bound(abstract=True)
class StefanBoltzmannUnit(BaseUnit):
    dimension = "stefan_boltzmann_constant"

@_axiom.derive(Watt / (Meter**2 * Kelvin**4))
class WattPerSquareMeterKelvinFourth(StefanBoltzmannUnit):
    __base_unit__ = True
    symbol = "W/(m²·K⁴)"