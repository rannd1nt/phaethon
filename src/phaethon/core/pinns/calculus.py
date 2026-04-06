"""
Physics-Aware Differential Calculus Engine.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..compat import HAS_TORCH
from .tensor import PTensor

if TYPE_CHECKING:
    import torch
elif HAS_TORCH:
    import torch

def grad(
    outputs: PTensor[Any], 
    inputs: PTensor[Any], 
    grad_outputs: torch.Tensor | None = None, 
    create_graph: bool = True
) -> PTensor[Any]:
    """
    Computes the gradient of outputs with respect to inputs (d(outputs)/d(inputs)).
    
    Wraps `torch.autograd.grad` to compute derivatives while automatically 
    inferring and synthesizing the derived physical unit (e.g., Distance / Time = Speed).

    Args:
        outputs: The target Phaethon PINNs Tensor.
        inputs: The independent variable tensor (must have `requires_grad=True`).
        grad_outputs: The "vector" in the vector-Jacobian product. Defaults to None.
        create_graph: If True, retains the graph for higher-order derivatives. Defaults to True.

    Returns:
        PTensor: A new Phaethon Tensor containing the computed gradients and synthesized unit.

    Examples:
        >>> s = pnn.PTensor([10.0], unit=u.Meter, requires_grad=True)
        >>> t = pnn.PTensor([2.0], unit=u.Second, requires_grad=True)
        >>> v = pnn.grad(s, t) # Unit becomes MeterPerSecond!
    """
    if not isinstance(outputs, PTensor) or not isinstance(inputs, PTensor):
        raise TypeError("Phaethon calculus operations (grad) strictly require PTensor inputs with valid physical units.")

    if not inputs.requires_grad:
        raise ValueError("The 'inputs' tensor must have requires_grad=True.")

    if grad_outputs is None:
        grad_outputs = torch.ones_like(outputs)

    grad_tuple = torch.autograd.grad(
        outputs=outputs,
        inputs=inputs, 
        grad_outputs=grad_outputs,
        create_graph=create_graph,
        retain_graph=True,
        allow_unused=True
    )
    
    gradient = grad_tuple[0]
    if gradient is None:
        gradient = torch.zeros_like(inputs, requires_grad=True)

    out_unit = getattr(outputs, 'unit', None)
    in_unit = getattr(inputs, 'unit', None)
    derived_unit = (out_unit / in_unit) if (out_unit and in_unit) else (out_unit or in_unit)

    return PTensor(gradient, unit=derived_unit)

def laplace(scalar_output: PTensor[Any], spatial_inputs: PTensor[Any]) -> PTensor[Any]:
    """
    Computes the Laplacian (∇²f) of a scalar field.
    
    Crucial for evaluating Heat Equations and Wave Equations. The unit is 
    synthesized as: `output_unit / (spatial_unit ** 2)`.

    Args:
        scalar_output: A scalar field tensor (e.g., Temperature).
        spatial_inputs: A tensor containing spatial coordinates (x, y, z).

    Returns:
        PTensor: A scalar Phaethon Tensor representing the Laplacian.
    Examples:
        >>> T = pnn.PTensor([[100.0, 50.0]], unit=u.Kelvin, requires_grad=True)
        >>> xyz = pnn.PTensor([[1.0, 2.0]], unit=u.Meter, requires_grad=True)
        >>> heat_diffusion = pnn.laplace(T, xyz)
        >>> print(heat_diffusion.unit.dimension) # Kelvin / Meter²
    """
    if not isinstance(scalar_output, PTensor) or not isinstance(spatial_inputs, PTensor):
        raise TypeError("Phaethon calculus operations (laplace) strictly require PTensor inputs.")
    
    first_deriv = grad(scalar_output, spatial_inputs, create_graph=True)
    laplacian = torch.zeros_like(spatial_inputs[..., 0])
    
    for i in range(spatial_inputs.shape[-1]):
        second_deriv = grad(first_deriv[..., i:i+1], spatial_inputs, create_graph=True)
        laplacian += second_deriv[..., i]

    derived_unit = getattr(scalar_output, 'unit') / (getattr(spatial_inputs, 'unit') ** 2)
    return PTensor(laplacian, unit=derived_unit)

def div(vector_field: PTensor[Any], spatial_inputs: PTensor[Any]) -> PTensor[Any]:
    """
    Computes the Divergence (∇ · V) of a vector field.
    
    Essential for Mass Conservation (Continuity Equations). The unit is 
    synthesized as: `vector_unit / spatial_unit`.

    Args:
        vector_field: A vector field tensor. Must match the spatial inputs' dimensions.
        spatial_inputs: A tensor containing spatial coordinates.

    Returns:
        PTensor: A scalar field Phaethon Tensor representing the divergence.

    Examples:
        >>> V = pnn.PTensor([[10.0, 5.0]], unit=u.MeterPerSecond, requires_grad=True)
        >>> xyz = pnn.PTensor([[1.0, 2.0]], unit=u.Meter, requires_grad=True)
        >>> divergence = pnn.div(V, xyz)
        >>> print(divergence.unit.dimension) # 1 / Second (Frequency)
    """
    if not isinstance(vector_field, PTensor) or not isinstance(spatial_inputs, PTensor):
        raise TypeError("Phaethon calculus operations (div) strictly require PTensor inputs.")
    
    div_val = torch.zeros_like(spatial_inputs[..., 0])
    dims = spatial_inputs.shape[-1]
    
    for i in range(dims):
        grad_i = torch.autograd.grad(
            outputs=vector_field[..., i],
            inputs=spatial_inputs,
            grad_outputs=torch.ones_like(vector_field[..., i]),
            create_graph=True,
            retain_graph=True,
            allow_unused=True
        )[0]
        
        if grad_i is not None:
            div_val += grad_i[..., i]

    derived_unit = getattr(vector_field, 'unit') / getattr(spatial_inputs, 'unit')
    return PTensor(div_val, unit=derived_unit)

def curl(vector_field: PTensor[Any], spatial_inputs: PTensor[Any]) -> PTensor[Any]:
    """
    Computes the Curl (∇ × V) of a 3D vector field.
    
    Essential for Maxwell's Equations and Fluid Vorticity. The unit is 
    synthesized as: `vector_unit / spatial_unit`.

    Args:
        vector_field (Tensor): A strictly 3D vector field tensor.
        spatial_inputs (Tensor): A strictly 3D tensor containing spatial coordinates (x, y, z).

    Raises:
        ValueError: If either tensor does not have exactly 3 spatial dimensions.

    Returns:
        PTensor: A 3D vector field Phaethon Tensor representing the curl.
    
    Examples:
        >>> A = pnn.PTensor([[0.0, 1.0, 0.0]], unit=u.WeberPerSquareMeter, requires_grad=True)
        >>> xyz = pnn.PTensor([[1.0, 1.0, 1.0]], unit=u.Meter, requires_grad=True)
        >>> magnetic_curl = pnn.curl(A, xyz)
        >>> print(magnetic_curl.shape) # Returns a 3D vector field
    """
    if not isinstance(vector_field, PTensor) or not isinstance(spatial_inputs, PTensor):
        raise TypeError("Phaethon calculus operations (curl) strictly require PTensor inputs.")
    
    if spatial_inputs.shape[-1] != 3 or vector_field.shape[-1] != 3:
        raise ValueError("Curl is strictly defined for 3D vector fields.")

    grad_x = torch.autograd.grad(vector_field[..., 0], spatial_inputs, torch.ones_like(vector_field[..., 0]), create_graph=True, retain_graph=True, allow_unused=True)[0]
    grad_y = torch.autograd.grad(vector_field[..., 1], spatial_inputs, torch.ones_like(vector_field[..., 1]), create_graph=True, retain_graph=True, allow_unused=True)[0]
    grad_z = torch.autograd.grad(vector_field[..., 2], spatial_inputs, torch.ones_like(vector_field[..., 2]), create_graph=True, retain_graph=True, allow_unused=True)[0]

    def safe_extract(grad_tensor: torch.Tensor | None, idx: int) -> torch.Tensor:
        return grad_tensor[..., idx] if grad_tensor is not None else torch.zeros_like(spatial_inputs[..., 0])

    curl_x = safe_extract(grad_z, 1) - safe_extract(grad_y, 2)
    curl_y = safe_extract(grad_x, 2) - safe_extract(grad_z, 0)
    curl_z = safe_extract(grad_y, 0) - safe_extract(grad_x, 1)

    curl_val = torch.stack([curl_x, curl_y, curl_z], dim=-1)
    
    derived_unit = getattr(vector_field, 'unit') / getattr(spatial_inputs, 'unit')
    return PTensor(curl_val, unit=derived_unit)

grad.__module__ = "phaethon.pinns"
laplace.__module__ = "phaethon.pinns"
div.__module__ = "phaethon.pinns"
curl.__module__ = "phaethon.pinns"