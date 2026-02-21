import inspect
import functools
from decimal import Decimal
from typing import Callable, Union, Optional, Dict, Any, List, Type

from ..exceptions import AxiomViolationError, DimensionMismatchError

class Axiom:
    """
    Axiom defines a set of physical laws, constraints, and mathematical modifiers 
    that dynamically govern the instantiation and conversion of Chisa units.
    It acts as a physics rule engine using Python class decorators.
    """
    def __init__(self) -> None:
        pass

    def bound(
        self, 
        min_val: Optional[Union[float, Decimal, int]] = None, 
        max_val: Optional[Union[float, Decimal, int]] = None, 
        msg: Optional[str] = None
    ) -> Callable:
        """
        Enforces boundary limits on a unit's scalar value during instantiation.
        Prevents physical or mathematical impossibilities (e.g., negative Kelvin).

        Args:
            min_val (Optional[Union[float, Decimal, int]]): The absolute minimum allowed value.
            max_val (Optional[Union[float, Decimal, int]]): The absolute maximum allowed value.
            msg (Optional[str]): A custom error message to display upon violation.

        Returns:
            Callable: A class decorator.
        """
        def decorator(cls: Type) -> Type:
            original_init = cls.__init__
            
            @functools.wraps(original_init)
            def new_init(self_obj: Any, value: Union[int, float, Decimal, str], context: Optional[Dict[str, Any]] = None) -> None:
                original_init(self_obj, value, context)
                if min_val is not None and self_obj.value < Decimal(str(min_val)):
                    raise AxiomViolationError(msg or f"Value cannot be strictly less than {min_val}")
                if max_val is not None and self_obj.value > Decimal(str(max_val)):
                    raise AxiomViolationError(msg or f"Value cannot be strictly greater than {max_val}")
            
            cls.__init__ = new_init
            return cls
        return decorator

    def shift(
        self, 
        ctx: Optional[str] = None, 
        default: Union[float, Decimal, int] = 0.0, 
        op: str = "add", 
        formula: Optional[Callable[[Dict[str, Any]], Union[float, Decimal]]] = None
    ) -> Callable:
        """
        Applies a linear shift (addition or subtraction) to the base offset of a unit.
        The shift value can be statically defined, extracted dynamically from the context 
        dictionary, or calculated via a custom formula (e.g., Celsius to Kelvin).

        Args:
            ctx (Optional[str]): The key to look for in the context dictionary.
            default (Union[float, Decimal, int]): The fallback shift value if context is missing.
            op (str): The operation to perform ('add' or 'sub'). Defaults to "add".
            formula (Optional[Callable]): A custom function that takes the context dict and returns a scalar.

        Returns:
            Callable: A class decorator.
        """
        def decorator(cls: Type) -> Type:
            orig_to_base = cls._to_base_value
            orig_from_base = getattr(cls, '_from_base_value')

            def get_ctx_val(context: Dict[str, Any]) -> Decimal:
                if formula:
                    return Decimal(str(formula(context)))
                if ctx:
                    return Decimal(str(context.get(ctx, default)))
                return Decimal(str(default))

            def new_to_base(self_obj: Any) -> Decimal:
                base_val = orig_to_base(self_obj)
                ctx_val = get_ctx_val(self_obj.context)
                
                if op == "add": return base_val + ctx_val
                elif op == "sub": return base_val - ctx_val
                return base_val

            @classmethod
            def new_from_base(cls_obj: Type, base_val: Decimal, context: Dict[str, Any]) -> Decimal:
                ctx_val = get_ctx_val(context)
                
                if op == "add": base_val = base_val - ctx_val
                elif op == "sub": base_val = base_val + ctx_val
                return orig_from_base.__func__(cls_obj, base_val, context)

            cls._to_base_value = new_to_base
            cls._from_base_value = new_from_base
            return cls
        return decorator

    def scale(
        self, 
        ctx: Optional[str] = None, 
        default: Union[float, Decimal, int] = 1.0, 
        formula: Optional[Callable[[Dict[str, Any]], Union[float, Decimal]]] = None
    ) -> Callable:
        """
        Applies a scaling factor (multiplication or division) to the base multiplier.
        Highly useful for context-dependent units like Mach speed (which scales based on temperature).

        Args:
            ctx (Optional[str]): The key to look for in the context dictionary.
            default (Union[float, Decimal, int]): The fallback scale multiplier if context is missing.
            formula (Optional[Callable]): A custom function that takes the context dict and returns a multiplier.

        Returns:
            Callable: A class decorator.
        """
        def decorator(cls: Type) -> Type:
            orig_to_base = cls._to_base_value
            orig_from_base = getattr(cls, '_from_base_value')

            def get_ctx_val(context: Dict[str, Any]) -> Decimal:
                if formula:
                    return Decimal(str(formula(context)))
                if ctx:
                    return Decimal(str(context.get(ctx, default)))
                return Decimal(str(default))

            def new_to_base(self_obj: Any) -> Decimal:
                base_val = orig_to_base(self_obj)
                ctx_val = get_ctx_val(self_obj.context)
                return base_val * ctx_val

            @classmethod
            def new_from_base(cls_obj: Type, base_val: Decimal, context: Dict[str, Any]) -> Decimal:
                ctx_val = get_ctx_val(context)
                return orig_from_base.__func__(cls_obj, base_val / ctx_val, context)

            cls._to_base_value = new_to_base
            cls._from_base_value = new_from_base
            return cls
        return decorator

    def derive(
        self, 
        mul: Optional[List[Union[Type, float, int, str, Decimal]]] = None, 
        div: Optional[List[Union[Type, float, int, str, Decimal]]] = None
    ) -> Callable:
        """
        A powerful class decorator for Dimensional Synthesis.
        Automatically calculates the 'base_multiplier' of a custom unit class based on 
        the multiplication and division of other fundamental unit classes or scalar constants.
        
        Examples:
            @axiom.derive(mul=[Newton, Meter]) -> Assembles the Joule unit.\n
            @axiom.derive(mul=[0.5, Meter, Meter]) -> Assembles a custom triangle area unit.

        Args:
            mul (Optional[List]): A list of Unit Classes or scalar numbers to multiply.
            div (Optional[List]): A list of Unit Classes or scalar numbers to divide by.

        Returns:
            Callable: A class decorator that injects the computed multiplier.
        """
        def decorator(cls: Type) -> Type:
            mul_list = mul or []
            div_list = div or []
            
            multiplier = Decimal('1.0')
            
            for item in mul_list:
                if isinstance(item, (int, float, Decimal, str)):
                    multiplier *= Decimal(str(item))
                else:
                    multiplier *= Decimal(str(getattr(item, 'base_multiplier', 1.0)))
                    
            for item in div_list:
                if isinstance(item, (int, float, Decimal, str)):
                    val = Decimal(str(item))
                else:
                    val = Decimal(str(getattr(item, 'base_multiplier', 1.0)))
                    
                if val == 0:
                    raise ZeroDivisionError(f"Base multiplier or scalar cannot be zero in derive for {cls.__name__}.")
                multiplier /= val
                
            # Derived units strictly represent intervals/ratios, thus offset must be stripped.
            cls.base_offset = 0.0 
            cls.base_multiplier = multiplier
            return cls
        return decorator
    
    def require(self, **dim_or_class: Union[str, Type]) -> Callable:
        """
        Enforces strict dimension or unit constraints on function arguments.
        Acts as a protective guardrail for custom physics functions to prevent logical errors.

        Behaviors:
        - Pass a string (e.g., mass="mass") to strictly enforce a physical Dimension.
        - Pass a Class (e.g., mass=Kilogram) to enforce an exact Unit Class (Strict Type Mode).

        Args:
            **dim_or_class: Keyword arguments mapping function parameter names to their constraints.

        Returns:
            Callable: A function wrapper.
            
        Raises:
            DimensionMismatchError: If the argument does not match the expected dimension.
            TypeError: If the argument violates the strict Unit Class checking.
        """
        def decorator(func: Callable) -> Callable:
            sig = inspect.signature(func)
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for param_name, param_value in bound_args.arguments.items():
                    if param_name in dim_or_class:
                        constraint = dim_or_class[param_name]
                        
                        if isinstance(constraint, str):
                            if not hasattr(param_value, 'dimension'):
                                raise DimensionMismatchError(
                                    expected_dim=constraint, 
                                    received_dim=type(param_value).__name__,
                                    context=f"Argument '{param_name}' is not a valid Chisa unit object"
                                )
                            if param_value.dimension != constraint:
                                raise DimensionMismatchError(
                                    expected_dim=constraint, 
                                    received_dim=param_value.dimension,
                                    context=f"Argument '{param_name}' in function '{func.__name__}'"
                                )
                                
                        elif isinstance(constraint, type):
                            if not isinstance(param_value, constraint):
                                raise TypeError(
                                    f"Strict Type Violation: Argument '{param_name}' expected exactly "
                                    f"'{constraint.__name__}', but got '{type(param_value).__name__}'."
                                )
                            
                return func(*args, **kwargs)
            return wrapper
        return decorator