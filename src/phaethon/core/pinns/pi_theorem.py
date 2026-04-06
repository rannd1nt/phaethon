"""
Buckingham Pi Theorem Engine.
Automatically extracts dimensionless groups from a set of physical variables
using PyTorch SVD and Null-Space projection.
"""
from __future__ import annotations

from typing import List, Dict, Any, TYPE_CHECKING
from ..compat import HAS_TORCH
if HAS_TORCH:
    import torch
    import torch.nn as nn

from .tensor import PTensor
from ...exceptions import AxiomViolationError

if TYPE_CHECKING:
    from ..units.scalar import Dimensionless

class BuckinghamPi(nn.Module):
    """
        A neural layer that projects dimensioned tensors into a pure Dimensionless latent space.
        
        Utilizes PyTorch's Singular Value Decomposition (SVD) to dynamically extract the 
        Null Space of the dimensional matrix formed by the input variables. It synthesizes 
        established dimensionless groups (e.g., Reynolds Number, Mach Number) on-the-fly.

        Raises:
            AxiomViolationError: If the input variables lack a valid null space and 
                cannot mathematically form a dimensionless group.

        Examples:
            >>> import phaethon.pinns as pnn
            >>> from phaethon import u
            >>> pi_layer = pnn.BuckinghamPi()
            >>> v = pnn.PTensor([10.0], unit=u.MeterPerSecond)
            >>> d = pnn.PTensor([0.5], unit=u.Meter)
            >>> rho = pnn.PTensor([1000.0], unit=u.KilogramPerCubicMeter)
            >>> mu = pnn.PTensor([0.001], unit=u.PascalSecond)
            >>> # Automatically discovers the Reynolds Number formula
            >>> reynolds = pi_layer(v, d, rho, mu)
            >>> print(reynolds.unit.dimension)
            'dimensionless'
        """
    if TYPE_CHECKING:
        def __call__(self, *inputs: PTensor[Any], **kwargs: Any) -> PTensor[Dimensionless]: ...
    
    def __init__(self):
        """
        A neural layer that projects dimensioned tensors into a pure Dimensionless latent space.
        
        Utilizes PyTorch's Singular Value Decomposition (SVD) to dynamically extract the 
        Null Space of the dimensional matrix formed by the input variables. It synthesizes 
        established dimensionless groups (e.g., Reynolds Number, Mach Number) on-the-fly.

        Raises:
            AxiomViolationError: If the input variables lack a valid null space and 
                cannot mathematically form a dimensionless group.

        Examples:
            >>> import phaethon.pinns as pnn
            >>> from phaethon import u
            >>> pi_layer = pnn.BuckinghamPi()
            >>> v = pnn.PTensor([10.0], unit=u.MeterPerSecond)
            >>> d = pnn.PTensor([0.5], unit=u.Meter)
            >>> rho = pnn.PTensor([1000.0], unit=u.KilogramPerCubicMeter)
            >>> mu = pnn.PTensor([0.001], unit=u.PascalSecond)
            >>> # Automatically discovers the Reynolds Number formula
            >>> reynolds = pi_layer(v, d, rho, mu)
            >>> print(reynolds.unit.dimension)
            'dimensionless'
        """
        super().__init__()
        self.target_dim = "dimensionless"
        
        self._is_compiled: bool = False
        self._exponents: torch.Tensor | None = None
        self._input_signatures: tuple[frozenset[Any], ...] | None = None

    def _build_dimensional_matrix(self, tensors: tuple[PTensor, ...]) -> torch.Tensor:
        """Constructs the Dimensional Matrix M."""
        signatures: List[Dict[str, int]] = []
        all_dims = set()

        for t in tensors:
            sig_frozenset = getattr(t.unit, '_signature', frozenset())
            sig_dict = dict(sig_frozenset)
            signatures.append(sig_dict)
            all_dims.update(sig_dict.keys())

        dim_list = sorted(list(all_dims))
        matrix = torch.zeros((len(dim_list), len(tensors)), dtype=torch.float32)
        
        for col_idx, sig in enumerate(signatures):
            for row_idx, dim in enumerate(dim_list):
                if dim in sig:
                    matrix[row_idx, col_idx] = sig[dim]

        return matrix

    def _rationalize_null_vector(self, v: torch.Tensor) -> torch.Tensor:
        mask = torch.abs(v) > 1e-4
        if not torch.any(mask):
            return v
        
        min_val = torch.min(torch.abs(v[mask]))
        v_scaled = v / min_val
        v_rounded = torch.round(v_scaled * 2.0) / 2.0
        
        first_nonzero = torch.nonzero(mask)[0].item()
        if v_rounded[first_nonzero] < 0:
            v_rounded = -v_rounded
            
        return v_rounded

    def compile(self, inputs: tuple[PTensor[Any], ...]) -> None:
        """
        Executes SVD Null-Space extraction and caches physical exponents.

        Args:
            inputs: A tuple of physical tensors used to form the dimensional matrix.
            
        Raises:
            AxiomViolationError: If the inputs cannot form a valid dimensionless group.
        """
        M = self._build_dimensional_matrix(inputs)

        U, S, Vh = torch.linalg.svd(M, full_matrices=True)
        
        tolerance = 1e-5
        rank = torch.sum(S > tolerance).item()
        num_vars = M.shape[1]
        
        if rank == num_vars:
            raise AxiomViolationError(
                "Axiom Violation: The dimensional matrix has an empty null space. "
                "These variables CANNOT form a dimensionless group! "
                "Check your physics inputs (e.g., missing a balancing unit like viscosity)."
            )

        null_vector = Vh[-1, :] 
        self._exponents = self._rationalize_null_vector(null_vector)
        
        self._input_signatures = tuple(getattr(t.unit, '_signature', frozenset()) for t in inputs)
        self._is_compiled = True

    def forward(self, *inputs: PTensor[Any]) -> PTensor[Dimensionless]:
        """
        Projects input variables into synthesized dimensionless groups.

        Args:
            *inputs: Variadic physical tensors to be processed.

        Returns:
            A dimensionless PTensor representing the synthesized Pi group.
        """
        if len(inputs) == 0:
            raise ValueError("BuckinghamPi requires at least one PTensor input.")

        if not self._is_compiled:
            self.compile(inputs)
        else:
            current_sigs = tuple(getattr(t.unit, '_signature', frozenset()) for t in inputs)
            if current_sigs != self._input_signatures:
                self.compile(inputs)

        pi_tensor: PTensor | None = None
        
        for tensor, power in zip(inputs, self._exponents): # type: ignore
            power_val = power.item()
            if abs(power_val) < 1e-4:
                continue
                
            term = tensor ** power_val 
            
            if pi_tensor is None:
                pi_tensor = term
            else:
                pi_tensor = pi_tensor * term

        if pi_tensor is None or getattr(pi_tensor.unit, 'dimension', None) != self.target_dim:
             dim_name = getattr(pi_tensor.unit, 'dimension', 'Unknown') if pi_tensor else 'None'
             raise AxiomViolationError(f"Fatal Engine Error: Expected dimensionless, got '{dim_name}'.")

        from ..registry import ureg
        Dimensionless = ureg().get_unit_class('dimensionless')
        return pi_tensor.asunit(Dimensionless)