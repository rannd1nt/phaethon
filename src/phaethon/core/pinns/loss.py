"""
Physics-Informed Loss Functions.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..compat import HAS_TORCH
from .tensor import PTensor

if TYPE_CHECKING:
    import torch
    import torch.nn as nn
    _BaseModule = nn.Module
elif HAS_TORCH:
    import torch
    import torch.nn as nn
    _BaseModule = nn.Module
else:
    _BaseModule = object

class AxiomLoss(_BaseModule):
    """
    Penalizes a Neural Network for mathematically valid but physically impossible predictions.
    
    This loss function extracts the absolute bounds defined in Phaethon's unit and applies a ReLU-based 
    penalty gradient if the model's predictions violate these natural laws.
    """

    __module__ = "phaethon.pinns"

    def __init__(self, expected_dimension: str, min_val: float | None = None, max_val: float | None = None) -> None:
        """
        Penalizes a Neural Network for mathematically valid but physically impossible predictions.
        
        This loss function extracts the absolute bounds (axiom bounds) defined in Phaethon's unit registry,
        OR uses manually provided engineering bounds, and applies a ReLU-based penalty gradient if the model's predictions violate them.

        Args:
            expected_dimension: The target physical dimension.
            min_val: Manual override for the minimum allowed scalar boundary.
            max_val: Manual override for the maximum allowed scalar boundary.

        Examples:
            >>> import phaethon.pinns as pnn
            >>> tribunal = pnn.AxiomLoss(expected_dimension='mass')
            >>> # Model predicts an impossible negative mass
            >>> pred = pnn.PTensor([-5.0], unit=u.Kilogram)
            >>> penalty = tribunal(pred) # Returns a high penalty tensor to backpropagate
        """
        if not HAS_TORCH: raise ImportError("PyTorch is required for AxiomLoss.")
        super().__init__()
        self.expected_dim = expected_dimension
        self.override_min = min_val
        self.override_max = max_val

    def forward(self, pred: PTensor[Any]) -> torch.Tensor:
        """
        Computes the penalty score for axiomatic violations.

        Args:
            pred: The model's prediction wrapped as a physical tensor.

        Returns:
            A zero-dimensional scalar tensor representing the penalty magnitude.
            
        Raises:
            DimensionMismatchError: If the prediction's dimension does not match 
                the loss function's expected dimension.
        """
        if not isinstance(pred, PTensor):
            raise TypeError("AxiomLoss requires a Phaethon PINNs Tensor.")

        pred_dim = getattr(pred.unit, 'dimension', 'unknown')
        if pred_dim != self.expected_dim:
            from ...exceptions import DimensionMismatchError
            actual_dim_str = pred_dim
            if pred_dim == 'anonymous':
                sym = getattr(pred.unit, 'symbol', '???')
                actual_dim_str = f"Unregistered DNA [{sym}]"
                
            raise DimensionMismatchError(self.expected_dim, actual_dim_str, "AxiomLoss Tribunal")

        min_bound = self.override_min if self.override_min is not None else getattr(pred.unit, '__axiom_min__', None)
        max_bound = self.override_max if self.override_max is not None else getattr(pred.unit, '__axiom_max__', None)

        penalty = (pred.mag * 0.0).sum()

        if min_bound is not None:
            penalty += torch.mean(torch.relu(min_bound - pred.mag))
        if max_bound is not None:
            penalty += torch.mean(torch.relu(pred.mag - max_bound))

        return penalty
    
class ResidualLoss(_BaseModule):
    """
    Computes the Mean Squared Error (MSE) of a physics equation's residual.
    
    Before calculating the MSE, this loss function strictly verifies that the 
    residual tensor and the target tensor share the exact same physical dimension, 
    preventing users from accidentally equating Energy with Power.
    """
    __module__ = "phaethon.pinns"

    def __init__(self) -> None:
        """
        Computes the Mean Squared Error (MSE) of a physics equation's residual.
        
        Before calculating the MSE, this loss function strictly verifies that the 
        residual tensor and the target tensor share the exact same physical dimension, 
        preventing users from accidentally equating Energy with Power.

        Examples:
            >>> import phaethon.pinns as pnn
            >>> pde_loss = pnn.ResidualLoss()
            >>> # Evaluate how close a PDE is to equilibrium (0.0)
            >>> residual_energy = pnn.PTensor([0.5, -0.1], unit=u.Joule)
            >>> loss = pde_loss(residual_energy, target=0.0)
            >>> loss.backward()
        """
        if not HAS_TORCH: raise ImportError("PyTorch is required for ResidualLoss.")
        super().__init__()
        self.mse = nn.MSELoss()

    def forward(self, residual: PTensor[Any], target: PTensor[Any] | float = 0.0) -> torch.Tensor:
        """
        Evaluates the residual error against a target state.

        Args:
            residual: The computed residual of a physical equation.
            target: The desired target value, defaults to equilibrium (0.0).

        Returns:
            A scalar tensor representing the MSE of the physics residual.
        """
        if not isinstance(residual, PTensor):
            raise TypeError("ResidualLoss requires a Phaethon PINNs Tensor.")
        
        if isinstance(target, PTensor):
            if getattr(residual.unit, 'dimension', None) != getattr(target.unit, 'dimension', None):
                from ...exceptions import EquationBalanceError
                def _format_dim(u_cls: Any) -> str:
                    if u_cls is None: return "unknown"
                    dim = getattr(u_cls, 'dimension', 'unknown')
                    sym = getattr(u_cls, 'symbol', '')
                    sym_str = f" [{sym}]" if sym else ""
                    return f"Unregistered DNA{sym_str}" if dim == 'anonymous' else f"{dim}{sym_str}"
                
                raise EquationBalanceError(_format_dim(residual.unit), _format_dim(target.unit))
            target_mag = target.mag.expand_as(residual.mag)
        else:
            target_mag = torch.tensor(target, dtype=residual.mag.dtype, device=residual.mag.device)
            target_mag = target_mag.expand_as(residual.mag)

        return self.mse(residual.mag, target_mag)