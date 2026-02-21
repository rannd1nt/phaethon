from decimal import Decimal, getcontext
from typing import Union, Optional, List, Any, Type, Dict
from .registry import default_ureg
from ..exceptions import DimensionMismatchError

class BaseUnit:
    """
    The foundational core class for all physical and digital units in Chisa.
    Provides the standard interface for dimensional algebra, scalar conversions,
    and fluent formatting.
    """
    dimension: Optional[str] = None
    symbol: Optional[str] = None
    aliases: Optional[List[str]] = None
    base_multiplier: Union[float, Decimal] = 1.0
    base_offset: Union[float, Decimal] = 0.0

    def __init_subclass__(cls, **kwargs) -> None:
        """
        MAGIC METHOD: Automatically triggered whenever a user creates a subclass of BaseUnit.
        Completely eliminates the need for manual @register decorators by injecting 
        the new class directly into the global UnitRegistry.
        """
        super().__init_subclass__(**kwargs)
        default_ureg._register(cls)

    def __init__(self, value: Union[int, float, str, Decimal], context: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes a scalar unit object.

        Args:
            value (Union[int, float, str, Decimal]): The magnitude of the unit.
            context (Optional[Dict[str, Any]]): Contextual physical properties (e.g., temperature for Mach speed).
        """
        if not isinstance(value, (int, float, str, Decimal)):
            raise TypeError(f"Value must be numeric, got {type(value).__name__}")
        self.value = Decimal(str(value))
        self.context = context or {}

    def _to_base_value(self) -> Decimal:
        """Converts the current scalar value to its dimension's absolute base point."""
        val_with_offset = self.value + Decimal(str(self.base_offset))
        return val_with_offset * Decimal(str(self.base_multiplier))

    @classmethod
    def _from_base_value(cls, base_val: Decimal, context: Dict[str, Any]) -> Decimal:
        """Converts a value from the dimension's absolute base point to this specific unit."""
        val = base_val / Decimal(str(cls.base_multiplier))
        return val - Decimal(str(cls.base_offset))

    def __str__(self) -> str:
        val_str = str(self.value.normalize())
        return f"{val_str} {self.symbol}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.value} {self.symbol}>"

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def to(self, target_class: Type['BaseUnit']) -> 'BaseUnit':
        """
        Converts the current OOP unit object into another unit class within the same dimension.

        Args:
            target_class (Type[BaseUnit]): The target destination class (e.g., Meter).

        Returns:
            BaseUnit: A new instance of the target unit class.
            
        Raises:
            TypeError: If the target is not a valid Chisa BaseUnit.
            DimensionMismatchError: If the target belongs to a different physical dimension.
        """
        if not issubclass(target_class, BaseUnit):
            raise TypeError("Target must be a BaseUnit subclass")
        if self.dimension != target_class.dimension:
            raise DimensionMismatchError(self.dimension, target_class.dimension, context="Explicit OOP .to() method")
            
        base_val = self._to_base_value()
        target_val = target_class._from_base_value(base_val, self.context)
        
        return target_class(target_val, context=self.context)

    def format(
        self,
        prec: int = 4,
        sigfigs: Optional[int] = None,
        scinote: bool = False,
        delim: Union[bool, str] = False,
        tag: bool = True
    ) -> str:
        """
        A utility to format the object's value into a beautifully structured string.
        Highly useful for developers utilizing Chisa's strict OOP interface rather than the fluent convert() API.

        Args:
            prec (int): Number of decimal places to display. Defaults to 4.
            sigfigs (Optional[int]): Number of significant figures to enforce.
            scinote (bool): If True, forces scientific notation (e.g., 1.5E3).
            delim (Union[bool, str]): If True, applies thousands separators (commas). Can be a custom character.
            tag (bool): If True, appends the unit's symbol to the end of the string.

        Returns:
            str: The formatted cosmetic string.
        """
        val = self.value
        
        if sigfigs is not None:
            if val == 0:
                val = Decimal(0)
            else:
                shift = sigfigs - val.adjusted() - 1
                quantizer = Decimal('1e{}'.format(-shift))
                val = val.quantize(quantizer, rounding=getcontext().rounding)

        if scinote:
            digits = sigfigs - 1 if sigfigs is not None else prec
            val_str = f"{val:.{digits}E}"
        else:
            if sigfigs:
                decimal_places = max(sigfigs - (val.adjusted() + 1), 0)
                val_str = f"{val:.{decimal_places}f}"
            else:
                try:
                    quant = Decimal(f"1e-{prec}")
                    val = val.quantize(quant, rounding=getcontext().rounding)
                except Exception:
                    pass
                val_str = format(val, 'f')

        if not scinote and '.' in val_str:
            val_str = val_str.rstrip('0').rstrip('.')

        if delim:
            separator = "," if delim is True else str(delim)
            if not scinote:
                parts = val_str.split('.')
                parts[0] = f"{int(parts[0]):,}".replace(",", separator)
                val_str = '.'.join(parts) if len(parts) > 1 else parts[0]

        if tag:
            return f"{val_str} {self.symbol}"
        return val_str
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), context="Equality comparison (==)")
        return self._to_base_value() == other._to_base_value()

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), context="Less-than comparison (<)")
        return self._to_base_value() < other._to_base_value()

    def __add__(self, other: Any) -> 'BaseUnit':
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), context="Addition operator (+)")
        
        total_base = self._to_base_value() + other._to_base_value()
        final_value = total_base / Decimal(str(self.base_multiplier))
        return self.__class__(final_value, context=self.context)

    def __sub__(self, other: Any) -> 'BaseUnit':
        if not isinstance(other, BaseUnit):
            return NotImplemented
        if self.dimension != getattr(other, "dimension", None):
            raise DimensionMismatchError(str(self.dimension), str(getattr(other, 'dimension', None)), context="Subtraction operator (-)")
        
        total_base = self._to_base_value() - other._to_base_value()
        final_value = total_base / Decimal(str(self.base_multiplier))
        return self.__class__(final_value, context=self.context)