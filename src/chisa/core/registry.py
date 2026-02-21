from typing import Dict, List, Type, Optional, Set
from ..exceptions import UnitNotFoundError, DimensionMismatchError, AmbiguousUnitError

class UnitRegistry:
    """
    A centralized registry that manages the mapping of unit symbols and aliases
    to their respective classes using a Multi-Mapping architecture.
    """
    def __init__(self) -> None:
        # Multi-mapping dictionary to handle symbol collisions across dimensions
        # Example: {'m': [<class 'Meter'>, <class 'Minute'>]}
        self._units: Dict[str, List[Type]] = {}

    def _register(self, cls: Type) -> None:
        """
        Internal method to automatically register a unit class.
        Employs a Multi-Mapping architecture to handle symbol collisions.
        """
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
        """
        Retrieves a unit class based on its name or alias.
        Supports dimension filtering to resolve ambiguities (e.g., 'm' for meter vs. minute).

        Args:
            unit_name (str): The symbol or alias of the unit.
            expected_dim (Optional[str]): The expected physical dimension to filter by.

        Returns:
            Type: The corresponding unit class.

        Raises:
            UnitNotFoundError: If the unit is not found in the registry.
            DimensionMismatchError: If the resolved unit does not match the expected dimension.
            AmbiguousUnitError: If the unit matches multiple dimensions and expected_dim is not provided.
        """
        key = unit_name.lower().strip()
        candidates = self._units.get(key)
        
        if not candidates:
            raise UnitNotFoundError(unit_name)
            
        # If the expected dimension is known, filter the candidates to avoid ambiguity
        if expected_dim:
            for cls in candidates:
                if getattr(cls, 'dimension', None) == expected_dim:
                    return cls
            raise DimensionMismatchError(
                expected_dim, 
                getattr(candidates[0], 'dimension', 'unknown'), 
                context=f"Resolving target '{unit_name}'"
            )

        # If no expected dimension is provided, check for cross-dimensional collisions
        if len(candidates) > 1:
            dims = [getattr(c, 'dimension', 'unknown') for c in candidates]
            raise AmbiguousUnitError(unit_name, dims)
            
        return candidates[0]

    def get_base_unit(self, dimension: str) -> Type:
        """
        Finds the Base Unit class (the absolute reference point) for a specific dimension.
        Base Units are identified by a base_multiplier of 1.0 and a base_offset of 0.0.

        Args:
            dimension (str): The physical dimension to query.

        Returns:
            Type: The Base Unit class.

        Raises:
            ValueError: If no valid Base Unit is found for the given dimension.
        """
        dimension = dimension.lower().strip()
        for candidates in self._units.values():
            for cls in candidates:
                if getattr(cls, 'dimension', None) == dimension:
                    if getattr(cls, 'base_multiplier', None) == 1.0 and getattr(cls, 'base_offset', 0.0) == 0.0:
                        return cls
        raise ValueError(f"Dimension '{dimension}' does not have a valid Base Unit in the registry.")

    def get_dimensions(self) -> List[str]:
        """
        Retrieves a list of all unique physical dimensions currently supported by the registry.

        Returns:
            List[str]: A sorted list of dimension names.
        """
        dims: Set[str] = set()
        for candidates in self._units.values():
            for cls in candidates:
                if hasattr(cls, 'dimension') and cls.dimension:
                    dims.add(cls.dimension)
        return sorted(list(dims))

    def get_units_by_dimension(self, dimension: str) -> List[str]:
        """
        Retrieves all primary symbols (excluding aliases) associated with a specific dimension.

        Args:
            dimension (str): The physical dimension to query.

        Returns:
            List[str]: A sorted list of primary unit symbols.
        """
        dimension = dimension.lower().strip()
        symbols: Set[str] = set()
        for candidates in self._units.values():
            for cls in candidates:
                if getattr(cls, 'dimension', None) == dimension and hasattr(cls, 'symbol'):
                    symbols.add(cls.symbol)
        return sorted(list(symbols))

    def dimension_of(self, unit_name: str) -> str:
        """
        Resolves the physical dimension of a given unit string.

        Args:
            unit_name (str): The symbol or alias of the unit.

        Returns:
            str: The physical dimension of the unit.

        Raises:
            AmbiguousUnitError: If the unit input is ambiguous and maps to multiple dimensions.
        """
        cls = self.get_unit_class(unit_name)
        return getattr(cls, 'dimension', 'unknown')
    
default_ureg = UnitRegistry()