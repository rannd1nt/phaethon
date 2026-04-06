---
seo_type: TechArticle
title: "Differential Calculus: PDE Engine"
description: "Physics-aware PDE calculus in PyTorch. Automatically compute gradients, Laplacians, divergence, and curl with derived unit synthesis."
keywords: "solve PDE pytorch physics, physics informed neural networks calculus, pytorch autograd physical units, compute gradient with units, calculate laplacian pytorch"
---

# Differential Calculus Engine

In Scientific Machine Learning (SciML), solving Partial Differential Equations (PDEs) requires computing complex derivatives of the neural network's outputs with respect to its inputs. 

While PyTorch provides `torch.autograd.grad` to compute raw numerical gradients, it strips away physical meaning. Phaethon's **Differential Calculus Engine** wraps PyTorch's automatic differentiation with a physics-aware layer. It computes derivatives while automatically inferring and synthesizing the derived physical units (e.g., computing the derivative of Position with respect to Time automatically yields Velocity).

All functions in this module enforce strict type safety, requiring `PTensor` inputs. Furthermore, the independent variable tensors must have the `requires_grad=True` flag enabled.

---

## Gradient / First Derivative (`pnn.grad`)

The foundational function of the calculus engine. It computes the first-order gradient of a target tensor with respect to an independent variable tensor. The resulting physical unit is synthesized by dividing the target's unit by the independent variable's unit.

### API Reference

```python
phaethon.pinns.grad(
    outputs: PTensor, 
    inputs: PTensor, 
    grad_outputs: torch.Tensor | None = None, 
    create_graph: bool = True
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">outputs</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">The dependent variable tensor (e.g., a model's prediction).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">inputs</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">The independent variable tensor (e.g., spatial coordinates or time). Must have <code>requires_grad=True</code>.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">create_graph</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If True (default), retains the computational graph, enabling the calculation of higher-order derivatives (like acceleration from position).</div>
</div>

### Example: Kinematics
Computing the derivative of a position tensor with respect to a time tensor automatically yields a velocity tensor.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# Define independent variables with gradient tracking enabled
position = pnn.PTensor([10.0, 25.0], unit=u.Meter, requires_grad=True)
time = pnn.PTensor([1.0, 2.0], unit=u.Second, requires_grad=True)

# Calculate the gradient (dp/dt)
velocity = pnn.grad(position, time)

print(velocity.unit.dimension)
# Output: 'speed'
```

---

## Laplacian (`pnn.laplace`)



Computes the Laplacian operator (the divergence of the gradient) of a scalar field. It is a critical component in diffusion models, Heat Equations, and Wave Equations. 

The resulting unit is synthesized as the output unit divided by the square of the spatial unit.

### API Reference

```python
phaethon.pinns.laplace(
    scalar_output: PTensor, 
    spatial_inputs: PTensor
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">scalar_output</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">A scalar field tensor representing the physical quantity distributing across space (e.g., Temperature, Pressure).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">spatial_inputs</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">A tensor containing the spatial coordinates (e.g., x, y, z axes). Must have <code>requires_grad=True</code>.</div>
</div>

### Example: Heat Diffusion
Evaluating how temperature diffuses over a spatial grid. Phaethon's registry natively recognizes this derived dimension.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# A scalar field representing temperature
temperature = pnn.PTensor([[100.0, 50.0]], unit=u.Kelvin, requires_grad=True)

# Spatial coordinates (x, y)
xyz = pnn.PTensor([[1.0, 2.0]], unit=u.Meter, requires_grad=True)

# Compute the Laplacian
heat_diffusion = pnn.laplace(temperature, xyz)

print(heat_diffusion.unit.dimension)
# Output: 'spatial_temperature_curvature'
```

---

## Divergence (`pnn.div`)



Computes the Divergence of a vector field. Divergence acts as a measure of the magnitude of a vector field's source or sink at a given point. It is essential for defining Mass Conservation and Continuity Equations in fluid dynamics.

The engine synthesizes the unit by dividing the vector field's unit by the spatial input's unit.

### API Reference

```python
phaethon.pinns.div(
    vector_field: PTensor, 
    spatial_inputs: PTensor
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">vector_field</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">A vector field tensor. Its feature dimension must match the spatial inputs' coordinate dimensions.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">spatial_inputs</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">A tensor containing spatial coordinates. Must have <code>requires_grad=True</code>.</div>
</div>

### Example: The Phantom Unit Advantage
When computing the divergence of velocity (m/s) over space (m), the strict mathematical result is `1/s`. In standard frameworks, this is ambiguous. Phaethon resolves this natively as a generic `rate`, but allows you to cast it to specific **Units** (like `Hertz` or `Becquerel`) depending on your domain.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# A 2D velocity vector field (u, v components)
velocity_field = pnn.PTensor([[10.0, 5.0]], unit=u.MeterPerSecond, requires_grad=True)

# 2D spatial coordinates (x, y)
xyz = pnn.PTensor([[1.0, 2.0]], unit=u.Meter, requires_grad=True)

# Compute the divergence
divergence = pnn.div(velocity_field, xyz)

print(divergence.unit.dimension)
# Output: 'rate'

# Cast to cyclical frequency
freq = divergence.asunit(u.Hertz)
print(freq.unit.dimension)
# Output: 'frequency'

# Cast to radioactive decay
bec = divergence.asunit(u.Becquerel)
print(bec.unit.dimension)
# Output: 'radioactivity'
```

---

## Curl (`pnn.curl`)



Computes the Curl of a strictly 3D vector field. The curl measures the rotation or vorticity of a vector field. It is a fundamental operator in solving Maxwell's Equations (Electromagnetism) and the Navier-Stokes equations (Fluid Vorticity).

**Strict Constraint:** The curl operator is mathematically defined only for three-dimensional vector fields. If the `spatial_inputs` or `vector_field` tensors do not have exactly 3 dimensions in their final axis, Phaethon will raise a `ValueError`.

### API Reference

```python
phaethon.pinns.curl(
    vector_field: PTensor, 
    spatial_inputs: PTensor
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">vector_field</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">A vector field tensor with exactly 3 feature dimensions.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">spatial_inputs</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">A tensor containing exactly 3 spatial coordinates (x, y, z axes). Must have <code>requires_grad=True</code>.</div>
</div>

### Example: Vector Rotation
Calculating the curl of a vector field automatically returns a new 3D vector field.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# A 3D vector field (using Weber for magnetic flux examples)
magnetic_field = pnn.PTensor([[0.0, 1.0, 0.0]], unit=u.Weber, requires_grad=True)

# 3D spatial coordinates (x, y, z)
xyz = pnn.PTensor([[1.0, 1.0, 1.0]], unit=u.Meter, requires_grad=True)

# Compute the curl
vorticity = pnn.curl(magnetic_field, xyz)

print(vorticity.shape)
# Output: torch.Size([1, 3]) - Returns a corresponding 3D vector field
```