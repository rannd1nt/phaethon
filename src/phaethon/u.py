"""
The Universal Unit Collection for the Phaethon Framework.

This module provides access to all built-in dimensional units and base classes
in Phaethon. It aggregates all physical and digital dimensions into a single,
cohesive interface for declarative modeling and scientific computing.

Available Dimensional Domains:
    - `area`       : Square measurements (e.g., `SquareMeter`, `Acre`)
    - `data`       : Digital information (e.g., `Byte`, `Gigabyte`)
    - `density`    : Mass per unit volume (e.g., `KilogramPerCubicMeter`)
    - `energy`     : Work and heat (e.g., `Joule`, `Kilocalorie`)
    - `force`      : Physical mechanics (e.g., `Newton`, `PoundForce`)
    - `frequency`  : Cycles over time (e.g., `Hertz`, `RPM`)
    - `length`     : Distance measurements (e.g., `Meter`, `Foot`)
    - `mass`       : Weight and matter (e.g., `Kilogram`, `Pound`)
    - `power`      : Energy transfer rate (e.g., `Watt`, `Horsepower`)
    - `pressure`   : Force per area (e.g., `Pascal`, `Bar`, `PSI`)
    - `speed`      : Velocity (e.g., `MeterPerSecond`, `Mach`)
    - `temperature`: Thermal states (e.g., `Celsius`, `Kelvin`)
    - `time`       : Temporal duration (e.g., `Second`, `Hour`)
    - `volume`     : 3D space (e.g., `CubicMeter`, `Liter`, `Gallon`)

Example:
    >>> from phaethon import u
    >>> speed = u.Meter(10) / u.Second(2)
    >>> print(speed)
    <MeterPerSecond: 5.0 m/s>
"""
from .units.area import *
from .units.data import *
from .units.energy import *
from .units.force import *
from .units.length import *
from .units.mass import *
from .units.power import *
from .units.pressure import *
from .units.speed import *
from .units.temperature import *
from .units.time import *
from .units.volume import *
from .units.density import *
from .units.frequency import *