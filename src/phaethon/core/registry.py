from __future__ import annotations

import math
from typing import TYPE_CHECKING, overload, Literal
from ..exceptions import UnitNotFoundError, DimensionMismatchError, AmbiguousUnitError
from .compat import UnitLike, _Signature, _UnitT

if TYPE_CHECKING:
    from .base import BaseUnit


class _PhysicsGenome:
    _instance: _PhysicsGenome | None = None
    
    __dna: dict[_Signature, str]
    __sig_map: dict[str, _Signature]
    __phantoms: set[str]

    def __new__(cls) -> _PhysicsGenome:
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.__phantoms = {
                'cycle', 'decay', 'radiation', 'biological_effect', 
                'symbol', 'photon', 'count', 'angle', 'solid_angle',
                'energy_content', 'expansion'
            }

            cls._instance.__dna = {
                # 0. Scalar / Dimensionless & Angles
                frozenset(): 'dimensionless',
                frozenset({('time', -1)}): 'rate',
                frozenset({('cycle', 1), ('time', -1)}): 'frequency',
                frozenset({('angle', 1)}): 'angle', 
                frozenset({('solid_angle', 1)}): 'solid_angle', 
                frozenset({('symbol', 1), ('time', -1)}): 'baud_rate',
                frozenset({('photon', 1), ('time', -1)}): 'photon_flux',

                # 1. Kinematics & Classical Mechanics
                frozenset({('length', 1), ('time', -1)}): 'speed',
                frozenset({('length', 1), ('time', -2)}): 'acceleration',
                frozenset({('length', 3), ('mass', -1), ('time', -2)}): 'gravitational_parameter',
                frozenset({('length', 1), ('time', -3)}): 'jerk', 
                frozenset({('angle', 1), ('time', -1)}): 'angular_velocity', 
                frozenset({('angle', 1), ('time', -2)}): 'angular_acceleration',
                frozenset({('length', 2)}): 'area',
                frozenset({('length', 3)}): 'volume',
                frozenset({('length', 3), ('mass', -1)}): 'specific_volume',
                frozenset({('mass', 1), ('length', 1), ('time', -1)}): 'momentum',
                frozenset({('mass', 1), ('length', 2), ('time', -1), ('angle', -1)}): 'angular_momentum',
                frozenset({('mass', 1), ('length', 1), ('time', -2)}): 'force',
                frozenset({('mass', 1), ('length', 2), ('time', -2)}): 'energy',
                frozenset({('mass', 1), ('length', 2), ('time', -2), ('angle', -1)}): 'torque',
                frozenset({('mass', 1), ('length', 2), ('time', -3)}): 'power',
                frozenset({('mass', 1), ('length', -1), ('time', -2)}): 'pressure', 
                frozenset({('mass', -1), ('length', 1), ('time', 2)}): 'compressibility', 
                frozenset({('mass', 1), ('length', -3)}): 'density',
                frozenset({('mass', 1), ('length', 2)}): 'moment_of_inertia', 
                frozenset({('length', -1)}): 'linear_attenuation',
                frozenset({('angle', 1), ('length', -1)}): 'wavenumber',
                frozenset({('cycle', 1), ('length', -1)}): 'spatial_frequency',
                frozenset({('time', -1), ('expansion', 1)}): 'expansion_rate',

                # 2. Fluid Dynamics & Transport Phenomena
                frozenset({('mass', 1), ('time', -1)}): 'mass_flow_rate',
                frozenset({('length', 3), ('time', -1)}): 'volumetric_flow_rate',
                frozenset({('mass', 1), ('length', -2), ('time', -1)}): 'mass_flux', 
                frozenset({('mass', 1), ('length', -1), ('time', -1)}): 'dynamic_viscosity', 
                frozenset({('length', 2), ('time', -1)}): 'kinematic_viscosity',
                frozenset({('mass', 1), ('time', -2)}): 'force_per_length',

                # 3. Electromagnetism
                frozenset({('electric_current', 1), ('time', 1)}): 'electric_charge',
                frozenset({('electric_current', 1), ('length', 2)}): 'magnetic_dipole_moment',
                frozenset({('mass', 1), ('length', 2), ('time', -3), ('electric_current', -1)}): 'electric_potential',
                frozenset({('mass', -1), ('length', -2), ('time', 4), ('electric_current', 2)}): 'electrical_capacitance',
                frozenset({('mass', 1), ('length', 2), ('time', -3), ('electric_current', -2)}): 'electrical_resistance',
                frozenset({('mass', 1), ('length', 2), ('time', -2), ('electric_current', -1)}): 'magnetic_flux',
                frozenset({('mass', 1), ('time', -2), ('electric_current', -1)}): 'magnetic_flux_density',
                frozenset({('mass', 1), ('length', 1), ('time', -3), ('electric_current', -1)}): 'electric_field',
                frozenset({('electric_current', 1), ('length', -2)}): 'current_density',
                frozenset({('electric_current', 1), ('length', -1)}): 'magnetic_field_strength', 
                frozenset({('mass', 1), ('length', 2), ('time', -2), ('electric_current', -2)}): 'electrical_inductance', 
                frozenset({('mass', -1), ('length', -3), ('time', 4), ('electric_current', 2)}): 'electrical_permittivity', 
                frozenset({('mass', 1), ('length', 1), ('time', -2), ('electric_current', -2)}): 'magnetic_permeability',
                frozenset({('electric_current', 1), ('time', 1), ('mass', -1)}): 'specific_charge',

                # 4. Thermodynamics & Heat Transfer
                frozenset({('mass', 1), ('length', 2), ('time', -2), ('temperature', -1)}): 'entropy',
                frozenset({('length', 2), ('time', -2), ('temperature', -1)}): 'specific_heat_capacity', 
                frozenset({('mass', 1), ('length', 1), ('time', -3), ('temperature', -1)}): 'thermal_conductivity', 
                frozenset({('mass', 1), ('time', -3), ('temperature', -1)}): 'heat_transfer_coefficient', 
                frozenset({('mass', 1), ('time', -3)}): 'heat_flux_density',
                frozenset({('length', 2), ('time', -2)}): 'specific_energy',
                frozenset({('temperature', 1), ('length', -2)}): 'spatial_temperature_curvature',
                frozenset({('temperature', -1)}): 'thermal_expansion_coefficient',
                frozenset({('mass', 1), ('time', -3), ('temperature', -4)}): 'stefan_boltzmann_constant',
                frozenset({('mass', 1), ('length', -1), ('time', -2), ('energy_content', 1)}): 'energy_density',

                # 5. Photometry & Optics
                frozenset({('luminous_intensity', 1)}): 'luminous_intensity', 
                frozenset({('luminous_intensity', 1), ('solid_angle', 1)}): 'luminous_flux', 
                frozenset({('luminous_intensity', 1), ('solid_angle', 1), ('length', -2)}): 'illuminance', 
                frozenset({('luminous_intensity', 1), ('length', -2)}): 'luminance', 
                frozenset({('mass', 1), ('length', 2), ('time', -2), ('photon', -1)}): 'photon_energy',
                frozenset({('mass', 1), ('time', -3), ('photon', 1)}): 'irradiance',

                # 6. Chemistry & Material Science
                frozenset({('amount_of_substance', 1)}): 'amount_of_substance',
                frozenset({('amount_of_substance', 1), ('length', -3)}): 'molarity',
                frozenset({('mass', 1), ('amount_of_substance', -1)}): 'molar_mass',
                frozenset({('amount_of_substance', 1), ('time', -1)}): 'catalytic_activity',
                frozenset({('mass', 1), ('length', 2), ('time', -2), ('temperature', -1), ('amount_of_substance', -1)}): 'molar_heat_capacity',
                frozenset({('count', 1), ('length', -3)}): 'number_density',
                frozenset({('length', 3), ('amount_of_substance', -1)}): 'molar_volume',

                # 7. Computing & Information Theory
                frozenset({('data', 1), ('time', -1)}): 'data_rate',

                # 8. Econophysics
                frozenset({('currency', 1), ('time', -1)}): 'financial_flow_rate',
                frozenset({('currency', 1), ('mass', -1)}): 'price_per_mass',
                frozenset({('currency', 1), ('length', -3)}): 'price_per_volume',
                frozenset({('currency', 1), ('length', -2)}): 'price_per_area',
                frozenset({('currency', 1), ('data', -1)}): 'data_cost',
                frozenset({('currency', 1), ('mass', -1), ('length', -2), ('time', 2)}): 'price_per_energy', 

                # 9 Nulcear & Radioactive
                frozenset({('decay', 1), ('time', -1)}): 'radioactivity',
                frozenset({('length', 2), ('time', -2), ('radiation', 1)}): 'absorbed_dose',
                frozenset({('length', 2), ('time', -2), ('biological_effect', 1)}): 'equivalent_dose',
                frozenset({('length', 2), ('time', -3), ('radiation', 1)}): 'absorbed_dose_rate',
                frozenset({('length', 2), ('time', -3), ('biological_effect', 1)}): 'equivalent_dose_rate',

                # 10. Quantum Physics
                frozenset({('mass', 1), ('length', 2), ('time', -1)}): 'action',
            }
            cls._instance.__sig_map = {v: k for k, v in cls._instance.__dna.items()}
            
        return cls._instance

    def get_dimension(self, sig: _Signature) -> str | None:
        """Strict getter for dimension resolution."""
        return self.__dna.get(sig)

    def get_signature(self, dim: str) -> _Signature | None:
        """Strict getter for signature resolution."""
        return self.__sig_map.get(dim)

    def get_phantoms(self) -> set[str]:
        """Strict getter for retrieving registered phantom dimensions."""
        return self.__phantoms
    
    def inject(self, sig: _Signature, dim: str) -> None:
        """Controlled mutation gate for dynamically expanding physical axioms."""
        if not sig or not dim or dim == 'anonymous':
            return
        if sig not in self.__dna:
            self.__dna[sig] = dim
        if dim not in self.__sig_map:
            self.__sig_map[dim] = sig


class UnitRegistry:
    """
    A centralized registry that manages the mapping of unit symbols and aliases
    to their respective classes using a Multi-Mapping architecture.
    """
    _instance: UnitRegistry | None = None
    _units: dict[str, list[type[BaseUnit]]]
    _genome: _PhysicsGenome

    def __new__(cls) -> UnitRegistry:
        if cls._instance is None:
            cls._instance = super(UnitRegistry, cls).__new__(cls)
            cls._instance._units = {}
            cls._instance._genome = _PhysicsGenome()
        return cls._instance

    def _register(self, cls: type[BaseUnit]) -> None:
        def add_alias(alias: str) -> None:
            key = alias.strip()
            if key not in self._units:
                self._units[key] = []
            if cls not in self._units[key]:
                self._units[key].append(cls)

        if hasattr(cls, 'symbol') and cls.symbol is not None:
            add_alias(cls.symbol)
            
        if hasattr(cls, 'aliases') and cls.aliases:
            for alias in cls.aliases:
                add_alias(alias)
    
    def inject_dna(self, sig: _Signature, dim: str) -> None:
        """Self-learning mechanism to dynamically expand Phaethon's physics engine."""
        self._genome.inject(sig, dim)

    def get_signature_for_dim(self, dim: str) -> _Signature:
        sig = self._genome.get_signature(dim)
        if sig is not None:
            return sig
        return frozenset({(dim, 1)})
    
    def get_phantoms(self) -> set[str]:
        """Fetches the set of registered phantom dimensions from the genome."""
        return self._genome.get_phantoms()
    
    def resolve_signature(self, sig: _Signature) -> str:
        if not sig: 
            return 'dimensionless'
            
        if len(sig) == 1:
            dim, exp = next(iter(sig))
            if exp == 1:
                return dim
                
        resolved_dim = self._genome.get_dimension(sig)
        return resolved_dim if resolved_dim is not None else 'anonymous'
    
    def get_unit_class(self, unit_name: str, expected_dim: str | None = None) -> type[BaseUnit]:
        """Internal engine method to resolve string abbreviations to classes."""
        key = unit_name.strip()
        
        candidates = self._units.get(key)
        
        if not candidates:
            lower_key = key.lower()
            for k, v in self._units.items():
                if k.lower() == lower_key:
                    candidates = v
                    break
                    
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

    def baseof(self, dimension: str) -> type[BaseUnit]:
        from .config import get_config
        
        atol = get_config("atol")
        rtol = get_config("rtol")

        dimension = dimension.lower().strip()
        valid_candidates = []
        
        for candidates in self._units.values():
            for cls in candidates:
                if getattr(cls, 'dimension', None) == dimension:
                    
                    if getattr(cls, '__base_unit__', False) or getattr(cls, 'is_base_unit', False):
                        return cls
                        
                    b_mult = float(getattr(cls, 'base_multiplier', 0.0))
                    b_off = float(getattr(cls, 'base_offset', 0.0))

                    if math.isclose(b_mult, 1.0, rel_tol=rtol, abs_tol=atol) and math.isclose(b_off, 0.0, rel_tol=rtol, abs_tol=atol):
                        if cls not in valid_candidates:
                            valid_candidates.append(cls)
                            
        if not valid_candidates:
            raise ValueError(f"Dimension '{dimension}' does not have a valid Base Unit.")
            
        if len(valid_candidates) == 1:
            return valid_candidates[0]
            
        standard_anchors = {
            'speed': 'MeterPerSecond',
            'acceleration': 'MeterPerSecondSquared',
            'length': 'Meter',
            'mass': 'Kilogram',
            'time': 'Second',
            'temperature': 'Kelvin',
            'currency': 'USDollar',
            'dimensionless': 'Dimensionless',
            'data': 'Byte',
            'pressure': 'Pascal',
            'force': 'Newton',
            'energy': 'Joule',
            'power': 'Watt',
            'area': 'SquareMeter',
            'volume': 'CubicMeter',
            'density': 'KilogramPerCubicMeter'
        }
        
        if dimension in standard_anchors:
            for c in valid_candidates:
                if c.__name__ == standard_anchors[dimension]:
                    return c
                    
        valid_candidates.sort(
            key=lambda c: (not c.__name__.startswith('Derived_'), len(c.__name__)), 
            reverse=True
        )
        return valid_candidates[0]

    def dims(self) -> list[str]:
        dims: set[str] = set()
        for candidates in self._units.values():
            for cls in candidates:
                if hasattr(cls, 'dimension') and cls.dimension:
                    dims.add(cls.dimension)
        return sorted(list(dims))

    @overload
    def unitsin(self, dimension: str, ascls: Literal[False] = ...) -> list[str]: ...

    @overload
    def unitsin(self, dimension: str, ascls: Literal[True]) -> list[type[BaseUnit]]: ...

    def unitsin(self, dimension: str, ascls: bool = False) -> list[str] | list[type[BaseUnit]]:
        dimension = dimension.lower().strip()

        if ascls:
            classes: set[type[BaseUnit]] = set()
            for candidates in self._units.values():
                for cls in candidates:
                    if getattr(cls, 'dimension', None) == dimension:
                        classes.add(cls)
            return sorted(list(classes), key=lambda c: c.__name__)
        
        symbols: set[str] = set()
        for candidates in self._units.values():
            for cls in candidates:
                if getattr(cls, 'dimension', None) == dimension and hasattr(cls, 'symbol'):
                    symbols.add(cls.symbol)
        return sorted(list(symbols))

    def dimof(self, obj: UnitLike | BaseUnit) -> str:
        if hasattr(obj, 'dimension') and getattr(obj, 'dimension'):
            return getattr(obj, 'dimension')
            
        if isinstance(obj, str):
            try:
                cls = self.get_unit_class(obj)
                return getattr(cls, 'dimension', 'unknown')
            except Exception:
                pass
                
        return 'unknown'


# =========================================================================
# PUBLIC API WRAPPERS
# =========================================================================

def ureg() -> UnitRegistry:
    return UnitRegistry()

def baseof(dimension: str) -> type[BaseUnit]:
    """
    Retrieves the base unit class (the absolute reference point) for a dimension.
    Args:
        dimension: The dimension name (e.g., 'mass').

    >>> phaethon.baseof('temperature') -> <class 'Kelvin'>
    """
    return ureg().baseof(dimension)

def dims() -> list[str]:
    """
    Retrieves a list of all unique physical dimensions currently loaded.

    >>> phaethon.dims() -> ['area', 'mass', 'speed', ...]
    """
    return ureg().dims()

@overload
def unitsin(dimension: str, ascls: Literal[False] = ...) -> list[str]: ...

@overload
def unitsin(dimension: str, ascls: Literal[True]) -> list[type[BaseUnit]]: ...

def unitsin(dimension: str, ascls: bool = False) -> list[str] | list[type[BaseUnit]]:
    """
    Retrieves units associated with a specific dimension.
    
    Args:
        dimension: The dimension name (e.g., 'mass').
        ascls: If True, returns the actual Class objects instead of strings.
    """
    return ureg().unitsin(dimension, ascls=ascls)

def dimof(obj: UnitLike | BaseUnit) -> str:
    """
    Resolves the physical dimension of a string alias, Unit Class, or Unit Instance.
    
    >>> phaethon.dimof('kg') -> 'mass'
    >>> phaethon.dimof(Celsius) -> 'temperature'
    >>> phaethon.dimof(Meter(10)) -> 'length'
    """
    return ureg().dimof(obj)