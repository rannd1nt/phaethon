"""
PhaethonTensor: The Physics-Aware PyTorch Tensor.
"""
from __future__ import annotations
from typing import Any, Callable, TYPE_CHECKING, Generic, overload

from ..compat import HAS_TORCH, _UnitT_co, NumericLike, _UnitT
from ..registry import ureg
from ..base import BaseUnit
from ...exceptions import DimensionMismatchError

if TYPE_CHECKING:
    from torch import Tensor
else:
    Tensor = object if not HAS_TORCH else __import__('torch').Tensor

import torch
# =======================================================================
# OPTIMIZATION: O(1) Lookup Sets for __torch_function__
# =======================================================================
_EASY_OPS = frozenset({
    'mean', 'sum', 'clone', 'reshape', 'view', 'relu', 'tanh',
    '__getitem__', 'squeeze', 'unsqueeze', 'permute', 'transpose', 
    'expand', 'contiguous', 'cat', 'stack', 'to', 'cuda', 'cpu', 
    'float', 'double', 'half', 'bfloat16', 'type',
    'abs', 'neg', 'pos', 'round'
})
_ADD_SUB = frozenset({'add', 'sub'})
_MUL = frozenset({'mul'})
_DIV = frozenset({'div', 'truediv'})
_COMPARE = frozenset({'eq', 'ne', 'lt', 'le', 'gt', 'ge'})

class _TorchContextBox:
    """
    A lightweight bypass shell. It mimics a BaseUnit's internal state just 
    enough to pass through _to_base_value() and _from_base_value() 
    WITHOUT breaking PyTorch's computation graph.
    """
    __slots__ = ('_value', 'context', 'base_multiplier', 'base_offset')
    def __init__(self, val: Any, unit_cls: type[Any]):
        self._value = val
        self.context = {"__is_math_op__": True}
        self.base_multiplier = getattr(unit_cls, 'base_multiplier', 1.0)
        self.base_offset = getattr(unit_cls, 'base_offset', 0.0)

class PTensor(Tensor, Generic[_UnitT_co]): # type: ignore
    """
    A physics-native tensor designed for Scientific Machine Learning (SciML) and 
    Physics-Informed Neural Networks. 
    
    It natively evaluates dimensional algebra, maintains physical integrity during 
    complex matrix operations, and automatically tracks physical units through 
    the computational graph during automatic differentiation (backpropagation).
    """
    __module__ = "phaethon.pinns"

    _unit: type[_UnitT_co]

    if TYPE_CHECKING:
        def __init__(self, data: Any, unit: type[_UnitT_co] | str, **kwargs: Any) -> None:
            """
            A physics-native tensor designed for Scientific Machine Learning (SciML) and 
            Physics-Informed Neural Networks. 
            
            It natively evaluates dimensional algebra, maintains physical integrity during 
            complex matrix operations, and automatically tracks physical units through 
            the computational graph during automatic differentiation (backpropagation).

            Args:
                data: The numerical payload. Accepts lists, NumPy arrays, or existing tensors.
                unit: The governing physical unit class (e.g., u.Kilogram) 
                    or a registered string alias (e.g., 'kg').
                **kwargs: Additional tensor configuration (e.g., dtype, device, requires_grad).

            Raises:
                UnitNotFoundError: If the provided string alias cannot be resolved in the registry.
                DimensionMismatchError: If operations between PTensors violate fundamental physical laws.

            Examples:
                >>> import phaethon.pinns as pnn
                >>> import phaethon.units as u
                >>> velocity = pnn.PTensor([10.0, 15.0], unit=u.MeterPerSecond, requires_grad=True)
                >>> print(velocity.unit.dimension)
                'speed'
            """
            ...

        @property
        def unit(self) -> type[_UnitT_co]: ...
        @property
        def mag(self) -> Tensor: ...

        def __add__(self, other: PTensor[_UnitT_co] | NumericLike) -> PTensor[_UnitT_co]: ...
        def __sub__(self, other: PTensor[_UnitT_co] | NumericLike) -> PTensor[_UnitT_co]: ...
        
        @overload
        def __mul__(self, other: NumericLike) -> PTensor[_UnitT_co]: ...
        @overload
        def __mul__(self, other: PTensor[Any]) -> PTensor[Any]: ...
        
        @overload
        def __truediv__(self, other: NumericLike) -> PTensor[_UnitT_co]: ...
        @overload
        def __truediv__(self, other: PTensor[Any]) -> PTensor[Any]: ...

        def __pow__(self, exponent: NumericLike) -> PTensor[Any]: ...
        def __radd__(self, other: Any) -> PTensor[Any]: ...
        def __rmul__(self, other: Any) -> PTensor[Any]: ...

    def __new__(cls, data: Any, unit: type[_UnitT_co] | str, **kwargs: Any) -> PTensor[_UnitT_co]:
        """
        A physics-native tensor designed for Scientific Machine Learning (SciML) and 
        Physics-Informed Neural Networks.
        """
        if not HAS_TORCH:
            raise ImportError("PyTorch is required to use Phaethon PINNs Tensors.")
            
        req_grad = kwargs.pop('requires_grad', False)
        tmp_tensor = torch.as_tensor(data, **kwargs)
        
        if req_grad and not tmp_tensor.is_floating_point():
            tmp_tensor = tmp_tensor.float()

        obj = tmp_tensor.as_subclass(cls)
        obj._unit = ureg().get_unit_class(unit) if isinstance(unit, str) else unit
        
        if req_grad:
            obj.requires_grad_(True)
            
        return obj

    @property
    def unit(self) -> type[_UnitT_co]:
        """The physical unit class governing this tensor's dimensional identity."""
        return self._unit

    @property
    def mag(self) -> Tensor:
        """The raw numerical magnitude stripped of physical metadata."""
        return self.as_subclass(Tensor)

    @property
    def si(self) -> PTensor[Any]:
        """Strips Phantom Units and returns the pure SI Base version of this tensor."""
        dummy_base = self.unit(1.0, context=getattr(self, 'context', {}))
        target_unit = dummy_base.si.__class__
        return self.asunit(target_unit)

    def decompose(self) -> str:
        """Returns the canonical SI base structure signature."""
        return self.unit.decompose() # type: ignore

    def __invert__(self) -> PTensor[Any]:
        """The Base Unit Converter. Forces logarithmic/derived units to their canonical SI Base."""
        from ..registry import ureg
        base_cls = ureg().baseof(self.unit.dimension)
        return self.asunit(base_cls)
    
    def requires_grad_(self, requires_grad: bool = True) -> PTensor[_UnitT_co]:
        """In-place modification of autograd tracking, preserving physical DNA."""
        super().requires_grad_(requires_grad)
        return self
    
    @overload
    def asunit(self, target_unit: type[_UnitT]) -> PTensor[_UnitT]: ...
    
    @overload
    def asunit(self, target_unit: str) -> PTensor[Any]: ...

    def asunit(self, target_unit: type[BaseUnit] | str) -> PTensor[Any]:
        """
        Deterministically converts the tensor to a new physical unit.
        
        This method performs a JIT linear transformation to map the tensor's magnitude 
        from its current unit to a target unit within the same physical dimension. 
        It ensures that the underlying numerical values are scaled correctly while 
        preserving the absolute physical state.

        Args:
            target_unit: The destination unit class or its registered string alias.

        Returns:
            A new PTensor instance rescaled to the target unit.

        Raises:
            DimensionMismatchError: If the target unit belongs to a physical 
                dimension incompatible with the current tensor.
            SemanticMismatchError: If the conversion violates an Exclusive Domain 
                Lock or triggers a Phantom Unit collision.
            UnitNotFoundError: If a string alias is provided that does not exist 
                in the registry.

        Examples:
            >>> velocity_kmh = velocity_ms.asunit(u.KilometerPerHour)
            >>> print(velocity_kmh.unit.symbol)
            'km/h'
        """
        target_u = ureg().get_unit_class(target_unit) if isinstance(target_unit, str) else target_unit
        
        if self.unit is target_u:
            return self

        target_dim = getattr(target_u, "dimension", None)
        is_same_dimension = (self.unit.dimension == target_dim)
        
        self_sig = getattr(self.unit, '_signature', frozenset())
        target_sig = getattr(target_u, '_signature', frozenset())
        is_same_dna = (self_sig == target_sig)

        if not (is_same_dimension or is_same_dna):
            phantoms = ureg().get_phantoms()
            self_core = frozenset((d, e) for d, e in self_sig if d not in phantoms)
            target_core = frozenset((d, e) for d, e in target_sig if d not in phantoms)
            
            if self_core == target_core:
                self_phantoms = {d for d, e in self_sig if d in phantoms}
                target_phantoms = {d for d, e in target_sig if d in phantoms}
                
                if self_phantoms and target_phantoms and (self_phantoms != target_phantoms):
                    from ...exceptions import SemanticMismatchError
                    p1 = list(self_phantoms)[0]
                    p2 = list(target_phantoms)[0]
                    raise SemanticMismatchError(f"Phantom Collision: Cannot cast '{p1}' to '{p2}'. Expected '{target_dim}', but got '{self.unit.dimension}'.")
                is_same_dna = True

        if not (is_same_dimension or is_same_dna):
            raise DimensionMismatchError(str(self.unit.dimension), str(target_dim), "PTensor.asunit() conversion")

        this_semantic = getattr(self.unit, '__semantic__', None)
        target_semantic = getattr(target_u, '__semantic__', None)
        if this_semantic and target_semantic and (this_semantic != target_semantic):
            from ...exceptions import SemanticMismatchError
            raise SemanticMismatchError(f"Cannot convert '{self.unit.__name__}' to '{target_u.__name__}'. Semantic domains are strictly isolated.")

        is_exclusive = (getattr(self.unit, '__exclusive_domain__', False) or getattr(target_u, '__exclusive_domain__', False))
        if is_exclusive and not is_same_dimension:
            from ...exceptions import SemanticMismatchError
            raise SemanticMismatchError(f"Exclusive Domain Locked: Cannot cast '{self.unit.__name__}' directly to '{target_u.__name__}'.")
        
        dummy_box = _TorchContextBox(self.mag, self.unit)
        base_mag = self.unit._to_base_value(dummy_box) # type: ignore
        new_mag = target_u._from_base_value(base_mag, dummy_box.context)
        
        return PTensor(new_mag, unit=target_u)

    @classmethod
    def __torch_function__(cls, func: Callable[..., Any], types: tuple[type, ...], args: tuple[Any, ...] = (), kwargs: dict[str, Any] | None = None) -> Any:
        import torch
        if kwargs is None: kwargs = {}

        fname = func.__name__
        
        u1 = getattr(args[0], 'unit', None) if isinstance(args[0], PTensor) else None
        u2 = getattr(args[1], 'unit', None) if len(args) > 1 and isinstance(args[1], PTensor) else None
        
        def _fmtdim(u_cls: Any) -> str:
            if u_cls is None: return "unknown"
            dim = getattr(u_cls, 'dimension', 'unknown')
            sym = getattr(u_cls, 'symbol', '')
            sym_str = f" [{sym}]" if sym else ""
            return f"Unregistered DNA{sym_str}" if dim == 'anonymous' else f"{dim}{sym_str}"

        is_log = getattr(u1, '__is_logarithmic__', False) or getattr(u2, '__is_logarithmic__', False)
        if is_log and fname in ('add', 'sub', 'mul', 'div', 'truediv'):
            def _to_linear(arg: Any) -> Any:
                if isinstance(arg, PTensor):
                    box = _TorchContextBox(arg.mag, arg.unit)
                    return arg.unit._to_base_value(box) # type: ignore
                return arg
            
            lin_args = tuple(_to_linear(a) for a in args)
            raw_linear_result = getattr(torch, fname)(*lin_args, **kwargs)
            
            if fname in ('add', 'sub'):
                target_unit = u1
            elif fname == 'mul':
                target_unit = u1 * u2 if (u1 and u2) else (u1 or u2)
            else:
                target_unit = u1 / u2 if (u1 and u2) else (1 / u2 if u2 else u1)
                
            box = _TorchContextBox(raw_linear_result, target_unit)
            final_mag = target_unit._from_base_value(raw_linear_result, box.context)
            return PTensor(final_mag, unit=target_unit)

        raw_result = super().__torch_function__(func, types, args, kwargs)
        if not isinstance(raw_result, torch.Tensor):
            return raw_result

        new_unit = None
    
        if fname in _EASY_OPS:
            new_unit = u1
        
        elif fname in _ADD_SUB:
            if u1 is u2:
                new_unit = u1
            elif u1 and u2:
                if getattr(u1, 'dimension', None) != getattr(u2, 'dimension', None):
                    from ...exceptions import PhysicalAlgebraError
                    raise PhysicalAlgebraError(fname, _fmtdim(u1), _fmtdim(u2))
                new_unit = u1
            else:
                new_unit = u1 or u2

        elif fname in _MUL:
            if u1 and u2: new_unit = u1 * u2
            else: new_unit = u1 or u2

        elif fname in _DIV:
            if u1 and u2: 
                new_unit = u1 / u2
            elif u1: 
                new_unit = u1
            elif u2: 
                new_unit = 1 / u2 

        elif fname in _COMPARE:
            if u1 and u2:
                dim1 = getattr(u1, 'dimension', None)
                dim2 = getattr(u2, 'dimension', None)
                if dim1 != dim2:
                    from ...exceptions import PhysicalAlgebraError
                    raise PhysicalAlgebraError(fname, _fmtdim(u1), _fmtdim(u2))
            
            def _get_base_mag(arg: Any) -> Any:
                if isinstance(arg, PTensor):
                    box = _TorchContextBox(arg.mag, arg.unit)
                    return arg.unit._to_base_value(box) # type: ignore
                return arg
                
            val1 = _get_base_mag(args[0])
            val2 = _get_base_mag(args[1])
            
            if fname in ('eq', 'ne'):
                from ..config import get_config
                atol = get_config("atol")
                rtol = get_config("rtol")
                
                t1 = torch.as_tensor(val1, dtype=torch.float64)
                t2 = torch.as_tensor(val2, dtype=torch.float64, device=t1.device)
                
                is_close = torch.isclose(t1, t2, rtol=rtol, atol=atol)
                return is_close if fname == 'eq' else ~is_close
            
            return getattr(torch, fname)(val1, val2, **kwargs)
    
        elif fname == 'pow':
            if u1:
                power_val = args[1].item() if isinstance(args[1], torch.Tensor) else args[1]
                new_unit = u1 ** power_val

        if new_unit is not None:
            out = raw_result if isinstance(raw_result, cls) else raw_result.as_subclass(cls)
            out._unit = new_unit
            return out
        
        if isinstance(raw_result, cls):
            return raw_result.as_subclass(torch.Tensor)

        return raw_result

    def _parse_other(self, other: Any) -> Any:
        import torch
        if isinstance(other, type) and issubclass(other, BaseUnit):
            return PTensor(torch.tensor(1.0, device=self.device, dtype=self.dtype), unit=other)
        return other
    
    def __repr__(self) -> str:
        symbol = getattr(self._unit, 'symbol', getattr(self._unit, '__name__', 'Unknown'))
        raw_repr = repr(self.as_subclass(Tensor))
        return raw_repr.replace("tensor(", f"PTensor(unit='{symbol}', data=")

    def __add__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.add(self, self._parse_other(other))
    def __sub__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.sub(self, self._parse_other(other))
    def __mul__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.mul(self, self._parse_other(other))
    def __truediv__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.div(self, self._parse_other(other))
    def __pow__(self, exponent: Any) -> PTensor[Any]: 
        import torch; return torch.pow(self, exponent)
    def __matmul__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.matmul(self, self._parse_other(other))
    
    def __radd__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.add(self._parse_other(other), self)
    def __rsub__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.sub(self._parse_other(other), self)
    def __rmul__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.mul(self._parse_other(other), self)
    def __rtruediv__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.div(self._parse_other(other), self)
    def __rmatmul__(self, other: Any) -> PTensor[Any]: 
        import torch; return torch.matmul(self._parse_other(other), self)
    
    def __eq__(self, other: Any) -> Tensor:
        return torch.eq(self, self._parse_other(other))
    def __ne__(self, other: Any) -> Tensor:
        return torch.ne(self, self._parse_other(other))
    def __lt__(self, other: Any) -> Tensor:
        return torch.lt(self, self._parse_other(other))
    def __le__(self, other: Any) -> Tensor:
        return torch.le(self, self._parse_other(other))
    def __gt__(self, other: Any) -> Tensor:
        return torch.gt(self, self._parse_other(other))
    def __ge__(self, other: Any) -> Tensor:
        return torch.ge(self, self._parse_other(other))