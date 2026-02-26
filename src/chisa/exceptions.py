from typing import List, Optional

class ChisaError(Exception):
    """
    Base exception class for all custom errors within the Chisa ecosystem.
    Catching this will catch any Chisa-specific operational failures.
    """
    __module__ = "builtins"
    pass

class UnitNotFoundError(ChisaError, ValueError):
    """
    Raised when a requested unit symbol or alias is not found in the global UnitRegistry.
    """
    __module__ = "builtins"
    
    def __init__(self, unit_name: str) -> None:
        self.unit_name = unit_name
        super().__init__(f"Unit '{unit_name}' is not recognized in the registry!")

class DimensionMismatchError(ChisaError, TypeError):
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

class AxiomViolationError(ChisaError, ValueError):
    """
    Raised when a scalar value violates the physical laws or strict boundaries 
    defined by the @axiom.bound decorator (e.g., negative absolute temperature).
    """
    __module__ = "builtins"
    
    def __init__(self, message: str) -> None:
        super().__init__(message)

class ConversionError(ChisaError, ValueError):
    """
    Raised when a conversion calculation fails procedurally (e.g., missing target unit, 
    invalid calculation mode, or unsupported method invocation like .flex() on Mass).
    """
    __module__ = "builtins"
    pass

class AmbiguousUnitError(ChisaError, ValueError):
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

class NormalizationError(ChisaError, ValueError):
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