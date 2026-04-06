---
seo_type: TechArticle
title: "PTensor: Physics-Aware PyTorch"
description: "Physics-constrained deep learning tensor. PTensor retains physical DNA during PyTorch GPU delegation, matrix operations, and gradient descent."
keywords: "physics-aware pytorch tensor, track units in autograd, pytorch tensor dimensional analysis, physics-constrained deep learning, assemble heterogeneous tensors"
---

# Physics Tensors & Operations

Standard PyTorch tensors (`torch.Tensor`) are mathematically blind. A standard computational graph cannot differentiate whether a floating-point value represents absolute temperature, velocity, or raw image pixels. 

The core of Phaethon's SciML engine is the `PTensor` (Phaethon Tensor). It is a strict subclass of `torch.Tensor` injected with physical DNA. Through an optimized O(1) routing architecture, `PTensor` natively evaluates dimensional algebra, maintains physical integrity during matrix operations, and automatically tracks physical units through the computational graph during backpropagation—all with near-zero overhead.

---

## The PTensor API

A `PTensor` operates exactly like a PyTorch tensor. It supports all native device movements (`.to('cuda')`), data type casting (`.double()`), and neural network operations, but it requires a physical unit upon instantiation.

**Type Safety:** While you can pass string aliases (e.g., 'm/s') to the `unit` parameter, it is highly recommended to pass the explicit class from `phaethon.units` (e.g., `u.MeterPerSecond`). Because `PTensor` is a Python `Generic`, passing the class provides flawless static type hinting (e.g., `PTensor[MeterPerSecond]`) to your IDE.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">data</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">The numerical payload. Accepts lists, NumPy arrays, or existing PyTorch tensors.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The governing physical unit class (Recommended) or string alias.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">requires_grad</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">Standard PyTorch autograd flag. If True, automatically casts integers to floating-point tensors. Defaults to <code>False</code>.</div>
</div>

### Initialization & GPU Delegation

Moving a `PTensor` across hardware devices or changing its data type does not strip its physical properties. The dimensional metadata travels safely with the tensor memory.

```python
import torch
import phaethon.pinns as pnn
import phaethon.units as u

# Init tensor on the CPU
mass = pnn.PTensor(
    [10.0, 20.0], 
    unit=u.Kilogram
)

# Delegate to GPU & cast to Double
has_gpu = torch.cuda.is_available()
device = 'cuda' if has_gpu else 'cpu'
mass_gpu = mass.to(device).double()

print(mass_gpu.unit.dimension) # 'mass'
print(mass_gpu.dtype) # torch.float64
```

---

## Dimensional Algebra & Synthesis

Phaethon dynamically tracks mathematical signatures across the PyTorch computational graph. When you multiply, divide, or exponentiate `PTensor` objects, the engine inherently synthesizes the correct physical dimension without breaking the chain rule of automatic differentiation.

```python
import phaethon.pinns as pnn
import phaethon.units as u

velocity = pnn.PTensor(
    [5.0, 10.0], 
    unit=u.MeterPerSecond, 
    requires_grad=True
)
mass = pnn.PTensor(
    [2.0, 2.0], 
    unit=u.Kilogram
)

# Synthesis: kg * m/s -> Momentum
momentum = mass * velocity 

print(momentum.unit.dimension)
# Output: 'momentum'

# Backprop tracks physics seamlessly
loss = momentum.sum()
loss.backward()

# Grad of Momentum vs Velocity = Mass
print(velocity.grad)
# Output: tensor([2., 2.])
```

### Matrix Multiplication & Unary Operators
`PTensor` supports PyTorch's native matrix operations (`@`, `torch.matmul`, `torch.bmm`) and unary operators (`abs`, `neg`, `round`). Matrix multiplication automatically triggers dimensional synthesis just like standard scalar multiplication.

### The Forensic Logger
If an operation violates physical laws (e.g., attempting to subtract frequency from acceleration), `PTensor` will halt the PyTorch graph construction immediately. Phaethon utilizes a forensic logger to extract the SI DNA of the mismatched tensors, providing clear, deterministic error traces instead of ambiguous exceptions.

```text
PhysicalAlgebraError: Mathematical operation 'sub' failed due to incompatible physical dimensions.
  Left operand  : acceleration [m/s2]
  Right operand : Unregistered DNA [m/(s*m2)]
```

---

## Comparison Algebra & Floating-Point Immunity

Comparing raw floating-point tensors in PyTorch is notoriously dangerous due to memory precision artifacts (e.g., 5.0000001 != 5.0). Furthermore, standard PyTorch evaluates `1 > 500` as `False`, completely ignoring if the underlying units are Kilometers and Meters.

Phaethon solves this by routing all comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`) through a dimensional alignment engine. 
1. `PTensor` automatically aligns the underlying magnitudes to their SI Base equivalents before evaluation.
2. For equality checks (`==`, `!=`), Phaethon uses `torch.isclose` based on the global relative and absolute tolerances (`rtol`, `atol`), granting absolute immunity against floating-point noise.

```python
import phaethon.pinns as pnn
import phaethon.units as u

len_a = pnn.PTensor([5.0], unit=u.Meter)
len_b = pnn.PTensor(
    [500.0], unit=u.Centimeter
)

# Aligns scales & resolves float noise
print(len_a == len_b)
# Output: tensor([True])

# Incompatible dimensions are blocked
mass = pnn.PTensor([5.0], unit=u.Kilogram)
print(len_a > mass)
# Raises: PhysicalAlgebraError
```

---

## Diagnostics & Formatting

To maintain parity with Phaethon's core `BaseUnit`, `PTensor` provides native diagnostic properties to inspect complex equations or strip semantic constraints during advanced neural architecture design.

### `.decompose()`
Returns a string representation of the tensor's absolute, canonical SI base structure. This is critical for debugging anonymously synthesized dimensions in complex Partial Differential Equations (PDEs).

```python
import phaethon.pinns as pnn
import phaethon.units as u

# Synthesis: Force * Length
f = pnn.PTensor([100.0], unit=u.Newton)
d = pnn.PTensor([2.0], unit=u.Meter)
energy = f * d

print(energy.decompose())
# Output: 'kg*m2/s2'
```

### .si (The Core Extractor / De-Phantomizer)
The semantic escape hatch. Explicitly attacks the DNA of the tensor by stripping away Phantom Units (e.g., Cycle, Decay) and Exclusive Domain Locks, returning a new `PTensor` rooted in its pure, generic SI base canvas.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# Dimension: torque
torque = pnn.PTensor(
    [100.0], unit=u.NewtonMeter
)

# Strips the 'Angle-1' lock
raw_energy = torque.si

print(raw_energy.unit.dimension)
# Output: 'energy'
```

### ~ (The Base Converter / Linearizer)
The absolute canonical scale converter. Triggered via the bitwise NOT operator (`~`), this forces any derived, scaled, or non-linear unit to collapse directly into the primary Base Unit of its respective dimension **while perfectly preserving its Semantic Domain Lock**. It acts as an instant linearization tool for logarithmic tensors.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# 30 dBm signal
signal = pnn.PTensor(
    [30.0], unit=u.DecibelMilliwatt
) 

# Linearizes to SI Base (Watt)
linear_power = ~signal

print(linear_power)
# Output: PTensor(unit='W', ...)
```

---

## Tensor Alignment & Neural Assembly

Standard PyTorch data manipulation layers cannot process physical metadata. Phaethon provides dimensional-safe tensor operations directly from the `pnn` facade to prepare heterogeneous physical data for standard hidden layers.

### Concatenation & Stacking (`pnn.cat`, `pnn.stack`)
Phaethon explicitly overrides PyTorch's concatenation functions to enforce dimensional homogeneity. If you attempt to join tensors with differing scales of the same dimension, the engine automatically executes a JIT linear transformation to align all tensors with the unit of the first sequence element.

```python
import phaethon.pinns as pnn
import phaethon.units as u

dist_1 = pnn.PTensor([1000.0], unit=u.Meter)
dist_2 = pnn.PTensor([2.0], unit=u.Kilometer)

# Automatically scales dist_2 (2.0 km) into 2000.0 Meters before concatenation
combined = pnn.cat([dist_1, dist_2], dim=0)

print(combined)
# Output: PTensor(unit='m', data=tensor([1000., 2000.]))
```

### The Gateway (`pnn.assemble`)

The `pnn.assemble` function acts as the final gateway before your physical data enters a standard PyTorch `nn.Module`. It safely strips the physics metadata (`.mag`) and concatenates heterogeneous tensors into a single, raw computational feature block that standard layers like `nn.Linear` can digest.

**Architecture Rule:** Always use `.asunit()` to standardize your tensors before assembly. This guarantees that your Neural Network weights do not suffer from vanishing or exploding gradients due to erratic unit scales (e.g., mixing millimeters and light-years).

```python
import torch.nn as nn
import phaethon.pinns as pnn
import phaethon.units as u

class PhysicsNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden = nn.Sequential(
            nn.Linear(2, 64), 
            nn.SiLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, x_raw: pnn.PTensor, t_raw: pnn.PTensor):
        # 1. Standardize physical scales to ensure stable gradient flow
        x_std = x_raw.asunit(u.Meter)
        t_std = t_raw.asunit(u.Second)
        
        # 2. Assemble naked features (strips physics, joins tensors)
        features = pnn.assemble(x_std, t_std, dim=-1)
        
        # 3. Process through standard PyTorch layers
        u_mag = self.hidden(features)
        
        # 4. Re-apply the expected physical dimension to the raw prediction
        return pnn.PTensor(u_mag, unit=u.MeterPerSecond)
```