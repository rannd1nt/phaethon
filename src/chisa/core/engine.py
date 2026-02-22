from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from typing import Literal, Union, Optional, Tuple, Any, Type
from math import log10, floor

from ..exceptions import ConversionError, AmbiguousUnitError, UnitNotFoundError
from .registry import UnitRegistry, default_ureg

try:
    from .base import BaseUnit
except ImportError:
    pass

# NUMPY SOFT-DEPENDENCY CHECK
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class _ConversionBuilder:
    """
    A private builder class that handles the fluent API chaining for unit conversions.
    It lazily stores the state, options, and context until the conversion is resolved.
    """
    def __init__(self, value: Any, source_unit: Union[str, Any], registry: UnitRegistry):
        """
        Initializes the conversion builder.

        Args:
            value: The magnitude to be converted (scalar, list, or NumPy array).
            source_unit: The source unit class or string alias.
            registry: The global unit registry instance.
            
        Raises:
            TypeError: If the input value cannot be converted to a numeric type.
        """
        self.raw_value = value
        
        # NumPy Vectorization Bypass
        if HAS_NUMPY and isinstance(value, (np.ndarray, np.generic, list, tuple)):
            self._internal_val = value if isinstance(value, (np.ndarray, np.generic)) else np.array(value, dtype=float)
            self.is_array = True
        else:
            # Scalar Decimal Enforcement
            self.is_array = False
            try:
                self._internal_val = Decimal(str(value)) if isinstance(value, (int, float, Decimal, str)) else Decimal(value)
            except (InvalidOperation, TypeError, ValueError):
                raise TypeError(f"Invalid input: '{value}' cannot be converted to a numeric type.")
                
        self.source_unit = source_unit
        self.registry = registry
        self._target_unit: Optional[Union[str, Any]] = None 
        
        self._options = {
            "mode": "decimal",
            "prec": 9,
            "roundin": "half_even",
            "output": "raw", 
            "sigfigs": None,
            "scinote": False,
            "delim": False
        }
        self._context = {}

    def to(self, unit: Union[Type['BaseUnit'], str]) -> '_ConversionBuilder':
        """
        Sets the target unit for the conversion.

        Args:
            unit: The symbol, alias, or BaseUnit class of the destination unit.
            
        Returns:
            The current builder instance to allow method chaining.
        """
        self._target_unit = unit
        return self

    def use(
        self,
        mode: Literal["decimal", "float64"] = None,
        format: Literal["raw", "exact", "str", "tag", "verbose"] = None,
        roundin: Literal["half_even", "half_up"] = None,
        prec: Optional[int] = None,
        sigfigs: Optional[int] = None,
        scinote: Optional[bool] = None,
        delim: Union[bool, str, None] = None,
        **kwargs
    ) -> '_ConversionBuilder':
        """
        Configures the conversion output format, mathematical precision, and calculation engine.

        Args:
            mode: The underlying math engine to use ("decimal" or "float64").
            format: The cosmetic structure of the output ("raw", "tag", or "verbose").
            roundin: The rounding strategy to apply ("half_even" or "half_up").
            prec: The number of decimal places to calculate or display.
            sigfigs: The number of significant figures to enforce on the final value.
            scinote: If True, forces the output string to use scientific notation.
            delim: If True, adds thousands separators. Can also be a custom string character.
            **kwargs: Alternative parameter aliases (e.g., `precision=2`, `sci_note=True`).

        Returns:
            The current builder instance to allow method chaining.
            
        Raises:
            ConversionError: If Decimal mode is explicitly forced on a vectorized array.
        """
        # Prevent forcing Decimal mode on vectorized inputs to avoid precision loss bugs
        if mode in {"decimal", "dec"} and getattr(self, 'is_array', False):
            raise ConversionError(
                "Decimal mode is not supported for vectorized array operations. "
                "NumPy arrays natively use float64 for performance. Remove the mode argument or set it to 'float64'."
            )
        
        if mode is not None: self._options["mode"] = mode
        if format is not None: self._options["output"] = format
        if roundin is not None: self._options["roundin"] = roundin
        if prec is not None: self._options["prec"] = prec
        if sigfigs is not None: self._options["sigfigs"] = sigfigs
        if scinote is not None: self._options["scinote"] = scinote
        if delim is not None: self._options["delim"] = delim

        aliases_map = {
            'prec': ['precision'],
            'delim': ['delimiter'],
            'roundin': ['rounding', 'round'],
            'sigfigs': ['significant_figures'],
            'scinote': ['scientific_notation', 'sci_note'],
            'output': ['fmt', 'format', 'out']
        }
        for main_key, aliases in aliases_map.items():
            for alias in aliases:
                if alias in kwargs:
                    self._options[main_key] = kwargs[alias]
                    
        return self

    def context(self, **kwargs) -> '_ConversionBuilder':
        """
        Dynamically injects physical variables or environmental conditions required 
        for context-dependent dimensional conversions (e.g., temperature for Mach speed).

        Args:
            **kwargs: Arbitrary keyword arguments representing physical conditions 
                (e.g., temp_c=25, atm_pressure_pa=101325).

        Returns:
            The current builder instance to allow method chaining.
        """
        self._context.update(kwargs)
        return self

    def _round_sigfigs(self, num: Union[float, Decimal], sigfigs: int) -> Union[float, Decimal]:
        """Applies significant figures rounding."""
        if num == 0:
            return Decimal(0)
        elif isinstance(num, Decimal):
            shift = sigfigs - num.adjusted() - 1
            quantizer = Decimal('1e{}'.format(-shift))
            return num.quantize(quantizer, rounding=getcontext().rounding)
        else:
            return round(num, -int(floor(log10(abs(num)))) + (sigfigs - 1))

    def _compute(self) -> Union[float, Decimal, Any]:
        """Executes the dimensional algebra and returns the raw scalar/vector."""
        if not self._target_unit:
            raise ConversionError("Target unit missing. You must call .to('unit') before computing.")

        SourceClass = None
        TargetClass = None
        expected_dimension = None

        if getattr(self.source_unit, 'dimension', None):
            SourceClass = self.source_unit
            expected_dimension = SourceClass.dimension
        elif getattr(self._target_unit, 'dimension', None):
            TargetClass = self._target_unit
            expected_dimension = TargetClass.dimension

        if expected_dimension is None:
            target_ambiguous = False
            source_ambiguous = False
            
            try:
                TargetClass = self.registry.get_unit_class(self._target_unit)
                expected_dimension = TargetClass.dimension
            except AmbiguousUnitError:
                target_ambiguous = True
            except UnitNotFoundError:
                pass
                
            if expected_dimension is None:
                try:
                    SourceClass = self.registry.get_unit_class(self.source_unit)
                    expected_dimension = SourceClass.dimension
                except AmbiguousUnitError:
                    source_ambiguous = True
                except UnitNotFoundError:
                    pass

            if expected_dimension is None:
                if target_ambiguous and source_ambiguous:
                    self.registry.get_unit_class(self.source_unit)
                elif source_ambiguous:
                    self.registry.get_unit_class(self.source_unit)
                elif target_ambiguous:
                    self.registry.get_unit_class(self._target_unit)
                else:
                    raise ConversionError(
                        f"Cannot resolve dimension for conversion from "
                        f"'{self.source_unit}' to '{self._target_unit}'."
                    )

        if SourceClass is None:
            SourceClass = self.registry.get_unit_class(self.source_unit, expected_dim=expected_dimension)
        if TargetClass is None:
            TargetClass = self.registry.get_unit_class(self._target_unit, expected_dim=expected_dimension)

        if getattr(TargetClass, 'dimension', None) != getattr(SourceClass, 'dimension', None):
            raise ConversionError(
                f"Dimension mismatch! Expected '{getattr(SourceClass, 'dimension', None)}', "
                f"got '{getattr(TargetClass, 'dimension', None)}'"
            )

        # Cache symbols for string formatting
        self._src_symbol = getattr(SourceClass, 'symbol', getattr(SourceClass, '__name__', str(self.source_unit)))
        self._tgt_symbol = getattr(TargetClass, 'symbol', getattr(TargetClass, '__name__', str(self._target_unit)))

        # ---------------------------------------------------------
        # Path A: Native Array Computation (Bypass scalar mechanics)
        # ---------------------------------------------------------
        if self.is_array and HAS_NUMPY:
            source_obj = SourceClass(self._internal_val, context=self._context)
            target_obj = source_obj.to(TargetClass)
            return target_obj.exact

        # ---------------------------------------------------------
        # Path B: Scalar Computation (Decimal / Float64)
        # ---------------------------------------------------------
        mode = str(self._options["mode"]).lower().strip()
        prec = self._options["prec"]
        roundin = str(self._options["roundin"]).lower().strip()

        if mode in {"decimal", "dec"}:
            getcontext().prec = prec * 2
            getcontext().rounding = ROUND_HALF_EVEN if roundin == "half_even" else ROUND_HALF_UP

            source_obj = SourceClass(self._internal_val, context=self._context)
            target_obj = source_obj.to(TargetClass)
            
            converted_value = target_obj.exact

            if HAS_NUMPY and isinstance(converted_value, (np.ndarray, np.generic)):
                return converted_value

            digits = converted_value.adjusted() + 1
            decimal_places = prec - digits

            if 0 <= decimal_places <= 50:
                try:
                    quant = Decimal(f"1e-{decimal_places}")
                    final_value = converted_value.quantize(quant, rounding=getcontext().rounding)
                except (InvalidOperation, ValueError):
                    final_value = converted_value.normalize()
            else:
                final_value = converted_value.normalize()

        elif mode in {"float", "float64"}:
            source_obj = SourceClass(float(self.raw_value), context=self._context)
            target_obj = source_obj.to(TargetClass)
            
            converted_value = target_obj.exact
            
            if HAS_NUMPY and isinstance(converted_value, (np.ndarray, np.generic)):
                if prec is not None:
                    final_value = np.round(converted_value, prec)
                else:
                    final_value = converted_value
            else:
                final_value = round(converted_value, prec)
        else:
            raise ConversionError(f"Computation mode '{mode}' is not recognized. Use 'decimal' or 'float64'.")

        if isinstance(final_value, (float, Decimal)) and final_value == int(final_value):
            final_value = int(final_value)

        sigfigs = self._options["sigfigs"]
        if sigfigs:
            try:
                sigfigs = int(sigfigs)
                if sigfigs <= 0: raise ValueError()
            except Exception:
                raise ConversionError("Significant figures (sigfigs) must be a positive integer!")
            
            if mode in {"decimal", "dec"}:
                getcontext().prec = max(getcontext().prec, sigfigs * 2)
            
            if not (HAS_NUMPY and isinstance(final_value, (np.ndarray, np.generic))):
                final_value = self._round_sigfigs(final_value, sigfigs)

        return final_value
    
    def resolve(self) -> Union[float, Decimal, str, Any]:
        """
        Executes the conversion pipeline and applies all configured string formatting.
        Safely formats vectorized array outputs if 'tag', 'str', or 'verbose' is requested.
        """
        final_value = self._compute()
        output_fmt = str(self._options["output"]).lower().strip()
        
        src_name = getattr(self, '_src_symbol', str(self.source_unit))
        tgt_name = getattr(self, '_tgt_symbol', str(self._target_unit))
        
        scinote = self._options["scinote"]
        delim = self._options["delim"]
        sigfigs = self._options["sigfigs"]
        prec = self._options["prec"]

        if HAS_NUMPY and isinstance(final_value, (np.ndarray, np.generic)):
            if output_fmt == "exact":
                return final_value
        
            if output_fmt == "raw":
                if isinstance(final_value, Decimal):
                    return float(final_value)
                return final_value

            def format_elem(x):
                if scinote:
                    digits = sigfigs - 1 if sigfigs is not None else prec
                    return f"{x:.{digits}E}"
                
                s = f"{float(x):.{prec}f}"
                if '.' in s:
                    s = s.rstrip('0').rstrip('.')
                    if s.endswith('-'): s = s + "0"
                    if not s: s = "0"
                
                if delim:
                    separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
                    parts = s.split('.')
                    parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                    s = '.'.join(parts) if len(parts) > 1 else parts[0]
                    
                return s

            val_str = np.array2string(
                final_value, 
                formatter={'float_kind': format_elem, 'int': format_elem},
                separator=', ',
                suppress_small=not scinote 
            )
            
            if output_fmt == "verbose":
                raw_str = np.array2string(
                    np.asarray(self.raw_value), 
                    formatter={'float_kind': format_elem, 'int': format_elem},
                    separator=', ',
                    suppress_small=not scinote
                )
                return f"{raw_str} {src_name} = {val_str} {tgt_name}"
            
            if output_fmt == "tag":
                return f"{val_str} {tgt_name}"
            
            return val_str

        if output_fmt == "raw":
            return final_value

        if scinote:
            digits = sigfigs - 1 if sigfigs is not None else prec
            val_str = f"{final_value:.{digits}E}" if isinstance(final_value, Decimal) else format(final_value, 'e')
        else:
            if sigfigs and isinstance(final_value, Decimal):
                decimal_places = max(sigfigs - (final_value.adjusted() + 1), 0)
                val_str = f"{final_value:.{decimal_places}f}"
            else:
                val_str = format(final_value, 'f')

        if sigfigs is not None and not scinote:
            if '.' in val_str:
                val_str = val_str.rstrip('0').rstrip('.')
        elif not scinote and '.' in val_str:
            val_str = val_str.rstrip('0').rstrip('.')

        if delim:
            separator = "," if delim is True or str(delim).lower() == "default" else str(delim)
            
            if not scinote:
                parts = val_str.split('.')
                parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                val_str = '.'.join(parts) if len(parts) > 1 else parts[0]
            
            raw_str = str(self.raw_value)
            if '.' in raw_str:
                raw_parts = raw_str.split('.')
                raw_parts[0] = f"{int(raw_parts[0]):,}".replace(",", separator)
                raw_str_formatted = '.'.join(raw_parts)
            else:
                raw_str_formatted = f"{int(self.raw_value):,}".replace(",", separator)
        else:
            raw_str_formatted = str(self.raw_value)

        if output_fmt == "verbose":
            return f"{raw_str_formatted} {src_name} = {val_str} {tgt_name}"
        if output_fmt == "tag":
            return f"{val_str} {tgt_name}"
            
        return val_str

    def flex(self, range: Tuple[Optional[str], Optional[str]] = (None, None), delim: Union[bool, str] = True) -> str:
        """
        Deconstructs the total time duration into a natural language format.
        Exclusive to units within the time dimension.
        
        Args:
            range: A tuple defining the upper and lower bounds for the output units (e.g., ('year', 'day')).
            delim: The separator string to use between time segments, or a boolean to use defaults.

        Returns:
            The human-readable formatted time string.
            
        Raises:
            ConversionError: If applied to a non-time dimension or a NumPy array.
        """
        if self.is_array:
            raise ConversionError(".flex() method cannot be applied to NumPy arrays.")
            
        SourceClass = self.registry.get_unit_class(self.source_unit) if isinstance(self.source_unit, str) else self.source_unit
        source_obj = SourceClass(self._internal_val, context=self._context)

        if not hasattr(source_obj, 'flex'):
            raise ConversionError(
                f"Unit '{getattr(SourceClass, 'symbol', self.source_unit)}' (Dimension: {SourceClass.dimension}) "
                f"does not support the .flex() method. This feature is exclusive to time dimensions."
            )
        
        return source_obj.flex(range=range, delim=delim)
    
    def __str__(self) -> str:
        if not self._target_unit:
            src_name = getattr(self.source_unit, 'symbol', getattr(self.source_unit, '__name__', str(self.source_unit)))
            return f"<Chisa Pending: {self._internal_val} {src_name} -> Call .to()>"
        return str(self.resolve())

    def __repr__(self) -> str:
        target = getattr(self._target_unit, 'symbol', getattr(self._target_unit, '__name__', str(self._target_unit))) if self._target_unit else "???"
        src = getattr(self.source_unit, 'symbol', getattr(self.source_unit, '__name__', str(self.source_unit)))
        return f"<_ConversionBuilder: {self._internal_val} {src} -> {target}>"


class _ChisaEngine:
    """The core engine wrapper connecting the fluent API to the UnitRegistry."""
    def __init__(self, registry: UnitRegistry):
        """
        Initializes the Chisa Engine.
        
        Args:
            registry: The global UnitRegistry instance containing loaded unit definitions.
        """
        self.registry = registry

    def convert(self, value: Any, unit: Union[Type['BaseUnit'], str]) -> _ConversionBuilder:
        return _ConversionBuilder(value, unit, self.registry)
    
_default_engine = _ChisaEngine(registry=default_ureg)

def convert(value: Any, unit: Union[Type['BaseUnit'], str]) -> _ConversionBuilder:
    """
    Initializes a fluent conversion pipeline for physical and digital units.

    This method serves as the primary entry point for the Chisa library. 
    It provides a chainable, intuitive, and highly precise conversion interface 
    driven by an underlying logic-driven Dimensional Algebra Engine. Supports 
    scalar values as well as iterables and NumPy arrays for vectorized calculations.

    Args:
        value: The magnitude to be converted (scalar, list, or NumPy array).
        unit: The source unit class or string alias.

    Returns:
        _ConversionBuilder: A builder object allowing chained execution methods 
        like `.to()`, `.use()`, `.context()`, and finally `.resolve()`.
    """
    return _default_engine.convert(value, unit)