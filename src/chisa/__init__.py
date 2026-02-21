"""
Chisa is A Dimensional Algebra and Unit Conversion Engine for Python.

Chisa provides a robust, developer-friendly ecosystem for handling physical and 
digital unit conversions, mathematical operations across different units, and 
strict dimensional validation. It is designed to prevent dimensional mismatch 
errors in scientific computing, engineering applications, and everyday scripting.

Scope and Capabilities:
    Chisa covers a wide array of physical and digital dimensions, including:
    Area, Data, Energy, Force, Length, Mass, Power, Pressure, Speed, 
    Temperature, Time, and Volume.

Core Paradigms:

    1. The Fluent API (Quick Conversions)
       A chainable, readable interface for straightforward conversions and string formatting.
       >>> from chisa import convert
       >>> result = convert(1.5, 'kg').to('g').use(format='verbose').resolve()
       >>> print(result) # "1.5 kg = 1500 g"

    2. Explicit OOP (Dimensional Math & State)
       Treat units as first-class objects. Chisa automatically handles base-value 
       normalization, allowing seamless math and comparisons between different units 
       of the same dimension.
       >>> from chisa.units.length import Meter, Centimeter
       >>> total = Meter(1) + Centimeter(50)
       >>> print(total) # <Meter: 1.5 m>

    3. The Axiom Engine (Advanced Extensibility & Synthesis)
       Developers can extend Chisa by defining custom units or entirely new dimensions 
       by inheriting from `BaseUnit`. The `@axiom` decorators act as a physics rule engine:
       - `@axiom.derive`: Synthesizes base multipliers automatically (e.g., Joule = Newton * Meter).
       - `@axiom.bound`: Enforces physical limits (e.g., Absolute Zero for Kelvin).
       - `@axiom.scale` / `.shift`: Handles complex, context-dependent unit scaling (e.g., Mach speed).
       - `@axiom.require`: Acts as a guardrail for custom physics functions, enforcing 
         dimensional integrity on arguments before execution.

Example Advanced Usage:
    >>> from chisa import axiom
    >>> from chisa.units.force import Newton
    >>> from chisa.units.mass import MassUnit
    >>> from chisa.units.length import LengthUnit
    >>> from chisa.units.time import TimeUnit
    >>> 
    >>> @axiom.require(mass="mass", distance="length", time="time")
    >>> def calculate_impact_force(mass: MassUnit, distance: LengthUnit, time: TimeUnit) -> Newton:
    ...     # Internal physics logic safely assuming correct dimensions...
    ...     pass
"""

from typing import Union, List
from decimal import Decimal

from .core.registry import default_ureg
from .core.axioms import Axiom
from .core.engine import ChisaEngine
from .core.base import BaseUnit

# Import modules to trigger auto-registration via __init_subclass__
from .units import (
    length, mass, pressure, time, speed, temperature, 
    data, volume, force, energy, power, area
)

axiom = Axiom()
_default_engine = ChisaEngine(registry=default_ureg)


def convert(value: Union[int, float, Decimal, str], from_unit: str):
    """
    Initializes a fluent conversion pipeline for physical and digital units.

    This method serves as the primary entry point for the Chisa library. 
    It provides a chainable, intuitive, and highly precise conversion interface 
    driven by an underlying Dimensional Algebra Engine. 

    Args:
        value (Union[int, float, Decimal, str]): The scalar magnitude to be converted.
        from_unit (str): The symbol or alias of the source unit (e.g., 'km', 'kg').

    Returns:
        _ConversionBuilder: A builder object allowing chained execution methods 
        like `.to()`, `.use()`, `.context()`, and finally `.resolve()`.
    """
    return _default_engine.convert(value, from_unit)


def get_base_unit(dimension: str) -> type:
    """
    Retrieves the base unit class (the absolute reference point) for a specified 
    physical dimension.

    Args:
        dimension (str): The dimension name (e.g., 'length', 'mass').

    Returns:
        type: The BaseUnit subclass serving as the standard for that dimension.
    """
    return default_ureg.get_base_unit(dimension)


def get_dimensions() -> List[str]:
    """
    Retrieves a list of all unique physical dimensions currently supported 
    and registered within the Chisa ecosystem.

    Returns:
        List[str]: A sorted list of dimension string identifiers.
    """
    return default_ureg.get_dimensions()


def get_units_by_dimension(dimension: str) -> List[str]:
    """
    Retrieves a list of primary unit symbols associated with a specific dimension.

    Args:
        dimension (str): The dimension name (e.g., 'volume', 'speed').

    Returns:
        List[str]: A sorted list of unit symbols.
    """
    return default_ureg.get_units_by_dimension(dimension)


def dimension_of(unit_name: str) -> str:
    """
    Resolves the physical dimension of a given unit symbol or alias.

    Args:
        unit_name (str): The unit symbol/alias to inspect (e.g., 'kg', 'mph').

    Returns:
        str: The physical dimension of the unit (e.g., 'mass', 'speed').
    """
    return default_ureg.dimension_of(unit_name)


__version__ = "0.1.0"
__all__ = [
    "convert",
    "axiom",
    "ChisaEngine",
    "BaseUnit",
    "default_ureg",
    "get_base_unit",
    "get_dimensions",
    "get_units_by_dimension",
    "dimension_of",
    "length",
    "mass",
    "pressure",
    "time",
    "speed",
    "temperature",
    "data",
    "volume",
    "force",
    "energy",
    "power",
    "area"
]