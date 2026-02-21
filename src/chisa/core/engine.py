from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation
from typing import Literal, Union, Optional, Tuple
from math import log10, floor

from ..exceptions import ConversionError
from .registry import UnitRegistry


class _ConversionBuilder:
    """
    A private builder class that handles the fluent API chaining for unit conversions.
    It lazily stores the state, options, and context until the conversion is resolved or printed.
    """
    def __init__(self, value: Union[int, float, Decimal, str], source_unit: str, registry: UnitRegistry):
        self.raw_value = value
        
        try:
            self.value = Decimal(str(value)) if isinstance(value, (int, float, Decimal, str)) else Decimal(value)
        except (InvalidOperation, TypeError, ValueError):
            raise TypeError(f"Invalid input: '{value}' cannot be converted to a numeric type.")
            
        self.source_unit = source_unit
        self.registry = registry
        self._target_unit: Optional[str] = None
        
        # Default options: Set to 'raw' so it returns pure numbers out of the box!
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

    def to(self, target_unit: str) -> '_ConversionBuilder':
        """
        Sets the target unit for the conversion.

        Args:
            target_unit (str): The symbol or alias of the desired destination unit.

        Returns:
            _ConversionBuilder: The current instance for further method chaining.
        """
        self._target_unit = target_unit
        return self

    def use(
        self,
        mode: Literal["decimal", "float64"] = None,
        format: Literal["raw", "tag", "verbose"] = None,
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
            mode (Literal["decimal", "float64"], optional): The underlying math engine to use. Defaults to "decimal" for absolute precision.
            format (Literal["raw", "tag", "verbose"], optional): The cosmetic structure of the output. 
                'raw' returns pure numbers, 'tag' appends the unit symbol, 'verbose' shows full equation.
            roundin (Literal["half_even", "half_up"], optional): The rounding strategy.
            prec (int, optional): The number of decimal places to calculate/display.
            sigfigs (int, optional): The number of significant figures to enforce on the final value.
            scinote (bool, optional): If True, forces the output string to use scientific notation (e.g., 1.5e3).
            delim (Union[bool, str], optional): If True, adds thousands separators (commas). Can also be a custom string character.
            **kwargs: Allows alternative aliases for arguments (e.g., `precision=2`, `sci_note=True`).

        Returns:
            _ConversionBuilder: The current instance for further method chaining.
        """
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
        for context-dependent dimensional conversions (e.g., Mach speed needs temperature).

        Args:
            **kwargs: Arbitrary keyword arguments representing physical conditions (e.g., temp=25, pressure=101325).

        Returns:
            _ConversionBuilder: The current instance for further method chaining.
        """
        self._context.update(kwargs)
        return self

    def _round_sigfigs(self, num: Union[float, Decimal], sigfigs: int) -> Union[float, Decimal]:
        """Internal method to apply significant figures rounding."""
        if num == 0:
            return Decimal(0)
        elif isinstance(num, Decimal):
            shift = sigfigs - num.adjusted() - 1
            quantizer = Decimal('1e{}'.format(-shift))
            return num.quantize(quantizer, rounding=getcontext().rounding)
        else:
            return round(num, -int(floor(log10(abs(num)))) + (sigfigs - 1))

    def _compute(self) -> Union[float, Decimal]:
        """
        Internal mathematical engine that executes the dimensional algebra.
        Always returns a raw, unformatted scalar numeric value.
        """
        if not self._target_unit:
            raise ConversionError("Target unit missing. You must call .to('target_unit') before computing.")

        mode = str(self._options["mode"]).lower().strip()
        prec = self._options["prec"]
        roundin = str(self._options["roundin"]).lower().strip()

        SourceClass = self.registry.get_unit_class(self.source_unit)
        
        expected_dimension = SourceClass.dimension
        TargetClass = self.registry.get_unit_class(self._target_unit, expected_dim=expected_dimension)

        if mode in {"decimal", "dec"}:
            getcontext().prec = prec * 2
            getcontext().rounding = ROUND_HALF_EVEN if roundin == "half_even" else ROUND_HALF_UP

            source_obj = SourceClass(self.value, context=self._context)
            target_obj = source_obj.to(TargetClass)
            converted_value = target_obj.value

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
            converted_value = float(target_obj.value)
            
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
            final_value = self._round_sigfigs(final_value, sigfigs)

        return final_value

    def resolve(self) -> Union[float, Decimal, str]:
        """
        Executes the conversion pipeline and applies all configured formatting.
        
        Returns a pure numeric type (Decimal or float) if the format is set to 'raw' 
        (the default behavior) and no string-modifying options (like delimiters) are active. 
        Returns a beautifully formatted string if 'tag', 'verbose', 'delim', or 'scinote' are used.

        Returns:
            Union[float, Decimal, str]: The final computed and formatted value.
        """
        final_value = self._compute()
        
        output_fmt = str(self._options["output"]).lower().strip()
        scinote = self._options["scinote"]
        delim = self._options["delim"]
        sigfigs = self._options["sigfigs"]
        prec = self._options["prec"]

        if output_fmt == "raw" and not scinote and not delim and sigfigs is None:
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

        if output_fmt == "raw":
            return val_str
        elif output_fmt == "verbose":
            return f"{raw_str_formatted} {self.source_unit} = {val_str} {self._target_unit}"
        else:
            return f"{val_str} {self._target_unit}"

    def flex(self, range: Tuple[Optional[str], Optional[str]] = (None, None), delim: Union[bool, str] = True) -> str:
        """
        Executes a human-readable duration format (e.g., '1 year 2 months 5 days'). 
        Strictly available for the 'time' dimension.

        Args:
            range (Tuple[Optional[str], Optional[str]], optional): Defines the largest and smallest 
                time units to include in the breakdown string. For example, ('year', 'day') will 
                ignore hours and seconds. Defaults to (None, None) which includes all applicable units.
            delim (Union[bool, str], optional): The separator string to use between time segments. 
                Defaults to True (which uses a space).

        Returns:
            str: The breakdown of the time duration in natural language.
        """
        SourceClass = self.registry.get_unit_class(self.source_unit)
        source_obj = SourceClass(self.value, context=self._context)

        if not hasattr(source_obj, 'flex'):
            raise ConversionError(
                f"Unit '{self.source_unit}' (Dimension: {SourceClass.dimension}) "
                f"does not support the .flex() method. This feature is exclusive to time dimensions."
            )
        
        return source_obj.flex(range=range, delim=delim)
    
    def __str__(self) -> str:
        """String magic method now purely delegates to .resolve()"""
        if not self._target_unit:
            return f"<Chisa Pending: {self.value} {self.source_unit} -> Call .to()>"
        
        return str(self.resolve())

    def __repr__(self) -> str:
        target = self._target_unit if self._target_unit else "???"
        return f"<_ConversionBuilder: {self.value} {self.source_unit} -> {target}>"


class ChisaEngine:
    """The core engine wrapper that injects the dependency of the UnitRegistry."""
    def __init__(self, registry: UnitRegistry):
        self.registry = registry

    def convert(self, value: Union[int, float, Decimal, str], from_unit: str) -> _ConversionBuilder:
        """Starts the conversion pipeline."""
        return _ConversionBuilder(value, from_unit, self.registry)