"""
Phaethon Linear Algebra Module.
Physics-aware wrappers around numpy.linalg operations.
"""
from .core.linalg import inv, det, solve, norm

__all__ = ["inv", "det", "solve", "norm"]