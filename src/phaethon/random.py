"""
Random Physics Module.
Generates stochastic tensors strictly bounded by physical dimensions.
"""
from .core.random import uniform, normal, poisson, exponential

__all__ = ["uniform", "normal", "poisson", "exponential"]