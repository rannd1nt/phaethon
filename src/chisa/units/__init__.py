"""
Physical and Digital Dimension Modules.

This package contains all concrete unit class definitions derived from Chisa's 
BaseUnit. It covers 12 core dimensions (Length, Mass, Time, Speed, Temperature, 
Pressure, Volume, Area, Force, Energy, Power, and Data). 

Importing these modules automatically triggers the `__init_subclass__` hook, 
registering every defined unit into the global UnitRegistry.
"""