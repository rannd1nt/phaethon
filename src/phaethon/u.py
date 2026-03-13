"""
The Universal Unit Collection for the Phaethon Framework.

This module provides access to all built-in dimensional units and base classes
in Phaethon. It aggregates all physical, digital, and financial dimensions into a single,
cohesive interface for declarative modeling and scientific computing.

Available Dimensional Domains:
- `area`                   : Square measurements (e.g., `SquareMeter`, `Acre`)
- `currency`               : Financial values with dynamic exchange rates (e.g., `USDollar`, `Bitcoin`)
- `data`                   : Digital information (e.g., `Byte`, `Gigabyte`)
- `density`                : Mass per unit volume (e.g., `KilogramPerCubicMeter`)
- `electric_charge`        : Electrical charge (e.g., `Coulomb`, `AmpereHour`)
- `electric_current`       : Flow of electric charge (e.g., `Ampere`, `Milliampere`)
- `electric_potential`     : Voltage / potential difference (e.g., `Volt`, `Kilovolt`)
- `electrical_capacitance` : Ability to store charge (e.g., `Farad`, `Microfarad`)
- `electrical_resistance`  : Opposition to current flow (e.g., `Ohm`, `Kiloohm`)
- `energy`                 : Work and heat (e.g., `Joule`, `Kilocalorie`)
- `force`                  : Physical mechanics (e.g., `Newton`, `PoundForce`)
- `frequency`              : Cycles over time (e.g., `Hertz`, `RPM`)
- `illuminance`            : Luminous flux per unit area (e.g., `Lux`)
- `length`                 : Distance measurements (e.g., `Meter`, `Foot`)
- `luminous_flux`          : Perceived power of light (e.g., `Lumen`)
- `luminous_intensity`     : Wavelength-weighted power emitted by a light source (e.g., `Candela`)
- `mass`                   : Weight and matter (e.g., `Kilogram`, `Pound`)
- `power`                  : Energy transfer rate (e.g., `Watt`, `Horsepower`)
- `pressure`               : Force per area (e.g., `Pascal`, `Bar`, `PSI`)
- `speed`                  : Velocity (e.g., `MeterPerSecond`, `Mach`)
- `temperature`            : Thermal states (e.g., `Celsius`, `Kelvin`)
- `time`                   : Temporal duration (e.g., `Second`, `Hour`)
- `volume`                 : 3D space (e.g., `CubicMeter`, `Liter`, `Gallon`)

Example:
    >>> from phaethon import u
    >>> # 1. Standard physical dimensional synthesis
    >>> speed = u.Meter(10) / u.Second(2)
    >>> print(speed)
    <MeterPerSecond: 5.0 m/s>
    
    >>> # 2. Context-aware financial conversion
    >>> revenue = u.Euro(100, context={"eur_to_usd": 1.10})
    >>> print(revenue.to(u.USDollar))
    <USDollar: 110.0 USD>
"""
from .units.area import *
from .units.currency import *
from .units.data import *
from .units.density import *
from .units.electromagnetism import *
from .units.energy import *
from .units.force import *
from .units.frequency import *
from .units.length import *
from .units.mass import *
from .units.photometry import *
from .units.power import *
from .units.pressure import *
from .units.speed import *
from .units.temperature import *
from .units.time import *
from .units.volume import *