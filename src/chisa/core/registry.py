from typing import Dict, List, Type, Optional, Set, Any, Union
from ..exceptions import UnitNotFoundError, DimensionMismatchError, AmbiguousUnitError

class UnitRegistry:
    """
    A centralized registry that manages the mapping of unit symbols and aliases
    to their respective classes using a Multi-Mapping architecture.
    """
    def __init__(self) -> None:
        self._units: Dict[str, List[Type]] = {}

    def _register(self, cls: Type) -> None:
        def add_alias(alias: str) -> None:
            key = alias.lower().strip()
            if key not in self._units:
                self._units[key] = []
            if cls not in self._units[key]:
                self._units[key].append(cls)

        if hasattr(cls, 'symbol') and cls.symbol:
            add_alias(cls.symbol)
            
        if hasattr(cls, 'aliases') and cls.aliases:
            for alias in cls.aliases:
                add_alias(alias)
    
    def get_unit_class(self, unit_name: str, expected_dim: Optional[str] = None) -> Type:
        """Internal engine method to resolve string abbreviations to classes."""
        key = unit_name.lower().strip()
        candidates = self._units.get(key)
        
        if not candidates:
            raise UnitNotFoundError(unit_name)
            
        if expected_dim:
            for cls in candidates:
                if getattr(cls, 'dimension', None) == expected_dim:
                    return cls
            raise DimensionMismatchError(
                expected_dim, 
                getattr(candidates[0], 'dimension', 'unknown'), 
                context=f"Resolving target '{unit_name}'"
            )

        if len(candidates) > 1:
            dims = [getattr(c, 'dimension', 'unknown') for c in candidates]
            raise AmbiguousUnitError(unit_name, dims)
            
        return candidates[0]

    def baseof(self, dimension: str) -> Type:
        dimension = dimension.lower().strip()
        for candidates in self._units.values():
            for cls in candidates:
                if getattr(cls, 'dimension', None) == dimension:
                    if getattr(cls, 'base_multiplier', None) == 1.0 and getattr(cls, 'base_offset', 0.0) == 0.0:
                        return cls
        raise ValueError(f"Dimension '{dimension}' does not have a valid Base Unit.")

    def dims(self) -> List[str]:
        dims: Set[str] = set()
        for candidates in self._units.values():
            for cls in candidates:
                if hasattr(cls, 'dimension') and cls.dimension:
                    dims.add(cls.dimension)
        return sorted(list(dims))

    def unitsin(self, dimension: str, ascls: bool = False) -> List[Union[str, Type]]:
        dimension = dimension.lower().strip()

        if ascls:
            classes: Set[Type] = set()
            for candidates in self._units.values():
                for cls in candidates:
                    if getattr(cls, 'dimension', None) == dimension:
                        classes.add(cls)
            return sorted(list(classes), key=lambda c: c.__name__)
        
        symbols: Set[str] = set()
        for candidates in self._units.values():
            for cls in candidates:
                if getattr(cls, 'dimension', None) == dimension and hasattr(cls, 'symbol'):
                    symbols.add(cls.symbol)
        return sorted(list(symbols))

    def dimof(self, obj: Any) -> str:
        if hasattr(obj, 'dimension') and getattr(obj, 'dimension'):
            return getattr(obj, 'dimension')
            
        if isinstance(obj, str):
            try:
                cls = self.get_unit_class(obj)
                return getattr(cls, 'dimension', 'unknown')
            except Exception:
                pass
                
        return 'unknown'
    
default_ureg = UnitRegistry()


def baseof(dimension: str) -> Type:
    """
    Retrieves the base unit class (the absolute reference point) for a dimension.
    Args:
        dimension: The dimension name (e.g., 'mass').

    >>> chisa.baseof('temperature') -> <class 'Celsius'>
    """
    return default_ureg.baseof(dimension)

def dims() -> List[str]:
    """
    Retrieves a list of all unique physical dimensions currently loaded.

    >>> chisa.dims() -> ['area', 'mass', 'speed', ...]
    """
    return default_ureg.dims()

def unitsin(dimension: str, ascls: bool = False) -> List[Union[str, Type]]:
    """
    Retrieves units associated with a specific dimension.
    
    Args:
        dimension: The dimension name (e.g., 'mass').
        ascls: If True, returns the actual Class objects instead of strings.
        
    
    >>> chisa.unitsin('mass') -> ['g', 'kg', 'lb', ...]
    >>> chisa.unitsin('mass', ascls=True) -> [<class 'Gram'>, <class 'Kilogram'>, ...]
    """
    return default_ureg.unitsin(dimension, ascls=ascls)

def dimof(obj: Any) -> str:
    """
    Resolves the physical dimension of a string alias, Unit Class, or Unit Instance.
    
    >>> chisa.dimof('kg') -> 'mass'
    >>> chisa.dimof(Celsius) -> 'temperature'
    >>> chisa.dimof(Meter(10)) -> 'length'
    """
    return default_ureg.dimof(obj)