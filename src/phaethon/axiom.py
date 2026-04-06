"""
Defines a set of physical laws, constraints, and mathematical modifiers 
that dynamically govern the instantiation and conversion of Phaethon units.
It acts as a physics rule engine utilizing Python decorators.
"""

from phaethon.core.axioms import bound, derive, logarithmic, scale, shift, require, prepare, C

__all__ = ["bound", "derive", "logarithmic", "scale", "shift", "require", "prepare", "C"]