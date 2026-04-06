from typing import List, Optional

class PhaethonError(Exception):
    """
    Base exception class for all custom errors within the Phaethon ecosystem.
    Catching this will catch any Phaethon-specific operational failures.
    """
    __module__ = "builtins"
    pass

class UnitNotFoundError(PhaethonError, ValueError):
    """
    Raised when a requested unit symbol or alias is not found in the global UnitRegistry.
    """
    __module__ = "builtins"
    
    def __init__(self, unit_name: str) -> None:
        self.unit_name = unit_name
        super().__init__(f"Unit '{unit_name}' is not recognized in the registry!")

class DimensionMismatchError(PhaethonError, TypeError):
    """
    Raised when attempting a mathematical operation or conversion across incompatible 
    physical dimensions (e.g., attempting to add Mass and Length).
    """
    __module__ = "builtins"
    
    def __init__(self, expected_dim: str, received_dim: str, context: Optional[str] = "") -> None:
        self.expected_dim = expected_dim
        self.received_dim = received_dim
        ctx_msg = f" ({context})" if context else ""
        super().__init__(f"Dimension mismatch{ctx_msg}. Expected '{expected_dim}', but got '{received_dim}'.")

class PhysicalAlgebraError(PhaethonError, TypeError):
    """
    Raised when a mathematical operation (+, -, ==, etc.) involves incompatible physical dimensions.
    """
    __module__ = "builtins"

    def __init__(self, op_name: str, left_dim: str, right_dim: str) -> None:
        self.op_name = op_name
        self.left_dim = left_dim
        self.right_dim = right_dim
        
        msg = (
            f"Mathematical operation '{op_name}' failed due to incompatible physical dimensions.\n"
            f"  Left operand  : {left_dim}\n"
            f"  Right operand : {right_dim}"
        )
        super().__init__(msg)

class EquationBalanceError(PhaethonError, ValueError):
    """
    Raised when a physics-informed loss function receives mismatched dimensions 
    between the computed residual and the target state.
    """
    __module__ = "builtins"

    def __init__(self, residual_dim: str, target_dim: str) -> None:
        self.residual_dim = residual_dim
        self.target_dim = target_dim
        
        msg = (
            f"The PDE residual and target state do not share the same physical dimension.\n"
            f"  Residual : {residual_dim}\n"
            f"  Target   : {target_dim}"
        )
        super().__init__(msg)

class SemanticMismatchError(PhaethonError):
    """Raised when two units have the same dimension but conflicting physical semantics (e.g., Cycle vs Decay)."""
    __module__ = "builtins"

class AxiomViolationError(PhaethonError, ValueError):
    """
    Raised when a scalar value violates the physical laws or strict boundaries 
    defined by the @axiom.bound decorator (e.g., negative absolute temperature).
    """
    __module__ = "builtins"
    
    def __init__(self, message: str) -> None:
        super().__init__(message)

class ConversionError(PhaethonError, ValueError):
    """
    Raised when a conversion calculation fails procedurally (e.g., missing target unit, 
    invalid calculation mode, or unsupported method invocation like .flex() on Mass).
    """
    __module__ = "builtins"
    pass

class AmbiguousUnitError(PhaethonError, ValueError):
    """
    Raised when an input unit symbol overlaps across multiple dimensions 
    (e.g., 'm' matching both Meter and Minute) and the engine lacks the 
    dimensional context to safely resolve it.
    """
    __module__ = "builtins"
    
    def __init__(self, unit_name: str, dimensions: List[str]) -> None:
        self.unit_name = unit_name
        self.dimensions = dimensions
        super().__init__(
            f"Ambiguous unit '{unit_name}'. It matches multiple dimensions: {dimensions}. "
            f"Please use a more specific alias (e.g., 'meter' or 'minute')."
        )

class NormalizationError(PhaethonError, ValueError):
    """
    Raised when a Schema fails to normalize a field, providing pinpoint debugging context.
    """
    __module__ = "builtins"
    
    def __init__(self, field: str, issue: str, indices: list, raw_sample: str = "", expected_dim: str = "", suggestion: str = "") -> None:
        self.field = field
        
        display_idx = str(indices[:3]).replace(']', '')
        idx_msg = f"{display_idx}, ...]" if len(indices) > 3 else f"{indices}"
        
        msg = f"\nNormalization failed for field '{field}' at index {idx_msg}.\n"
        msg += f"   ► Issue              : {issue}\n"
        if expected_dim:
            msg += f"   ► Expected Dimension : {expected_dim}\n"
        if raw_sample:
            msg += f"   ► Raw Value Sample   : '{raw_sample}'\n"
        if suggestion:
            msg += f"   ► Suggestion         : {suggestion}\n"
            
        super().__init__(msg)