---
seo_type: TechArticle
title: "Fourier Neural Operators (FNO)"
description: "Physics-aware FNO layers for Sci-ML. Automatically invert physical units via FFT, and apply learned low-pass spectral convolutions securely."
keywords: "fourier neural operator python, spectral convolutions pytorch, buckingham pi theorem machine learning, physics aware neural layers, fft dimensional inversion"
---

# Spectral Operators & Buckingham Pi

Standard neural networks map finite-dimensional vectors. To map infinite-dimensional spaces (like resolving turbulent fluid dynamics across an entire continuous grid), Scientific Machine Learning utilizes **Neural Operators**.

Phaethon provides advanced, physics-aware neural layers that natively handle complex mathematical transformations—such as crossing into the frequency domain or projecting variables into dimensionless spaces—without ever losing track of the physical units or breaking the computation graph.

---

## The Buckingham Pi Layer (`pnn.BuckinghamPi`)

The Buckingham Pi Theorem is a foundational concept in dimensional analysis. It states that any physically meaningful equation involving a set of physical variables can be rewritten in terms of a smaller set of dimensionless parameters (called Pi groups).

Phaethon brings this fundamental theorem directly into Deep Learning via the `BuckinghamPi` neural layer. This layer utilizes PyTorch's Singular Value Decomposition (SVD) to dynamically extract the Null Space of the dimensional matrix formed by your input variables. 

It synthesizes established dimensionless groups (e.g., Reynolds Number, Mach Number) on-the-fly, giving your neural network highly robust, scale-invariant features to learn from.

### API Reference

```python
phaethon.pinns.BuckinghamPi()
```

The `BuckinghamPi` layer is instantiated without arguments. Its configuration happens dynamically during the first forward pass.

**Forward Pass Arguments:**
<div class="param-box">
  <div class="param-header">
    <span class="p-name">*inputs</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor</span>
  </div>
  <div class="p-desc">Variadic physical tensors representing the physical variables of your system. They must contain valid physical units.</div>
</div>

### Automatic Null-Space Extraction

You simply feed the layer raw physical tensors. On the first pass, the layer compiles the dimensional matrix, extracts the rationalized null vector (exponents), and executes the projection. On subsequent passes, it reuses the cached exponents for maximum O(1) performance.

```python
import phaethon.pinns as pnn
import phaethon.units as u

# 1. Init neural projection layer
pi_layer = pnn.BuckinghamPi()

# 2. Provide raw physical vars
v = pnn.PTensor(
    [10.0], unit=u.MeterPerSecond
)
d = pnn.PTensor(
    [0.5], unit=u.Meter
)
rho = pnn.PTensor(
    [1000.0], 
    unit=u.KilogramPerCubicMeter
)
mu = pnn.PTensor(
    [0.001], unit=u.PascalSecond
)

# 3. Dynamically discovers Pi group!
reynolds = pi_layer(v, d, rho, mu)

print(reynolds.unit.dimension)
# Output: 'dimensionless'
```

### Axiomatic Protection
If the input variables lack a valid null space (meaning they cannot mathematically form a dimensionless group, perhaps because you forgot to include a balancing unit like viscosity to cancel out the mass dimension), the layer will immediately halt execution and raise an `AxiomViolationError`. It strictly refuses to generate mathematical garbage for your model.

---

## Spectral Transforms (`pnn.fft` & `pnn.ifft`)

Fourier Neural Operators require moving data from the Spatial/Temporal domain into the Frequency domain. Phaethon provides physics-aware wrappers for PyTorch's Real Fast Fourier Transform algorithms.

When transforming a tensor, the physical units must invert mathematically. Phaethon handles this automatically: If you input a tensor with a unit of `Second`, the FFT operation automatically inverts the unit's dimensional signature to `1/Second` (Frequency).

### API Reference

```python
phaethon.pinns.fft(
    tensor: PTensor | torch.Tensor, 
    dim: int = -1
)
```
```python
phaethon.pinns.ifft(
    tensor: PTensor | torch.Tensor, 
    dim: int = -1, n: int | None = None)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">tensor</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor | torch.Tensor</span>
  </div>
  <div class="p-desc">The input tensor. For FFT, this is in the physical domain. For IFFT, this is the complex-valued spectral tensor.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">dim</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">The dimension along which to take the transform. Defaults to the last dimension (-1).</div>
</div>

### Example: Dimensional Inversion

```python
import phaethon.pinns as pnn
import phaethon.units as u

# Time-series tensor
t_arr = pnn.PTensor(
    [0.0, 0.5, 1.0, 0.5], 
    unit=u.Second
)

# Transform to Frequency Domain
f_arr = pnn.fft(t_arr)
print(f_arr.unit.dimension)
# Output: 'rate'

# Transform back to Time Domain
restored = pnn.ifft(f_arr)
print(restored.unit.dimension)
# Output: 'time'
```

---

## Spectral Convolutions (`pnn.SpectralConv1d`)

The `SpectralConv1d` layer is the core building block of 1D Fourier Neural Operators. 

Instead of processing data using standard sliding windows in the spatial domain, this layer:

1. Transforms physical data into the frequency domain via `fft`.
2. Applies a learned complex weight matrix (Linear Transformation) to the lower frequency modes, effectively acting as a learnable low-pass filter. High-frequency noise is truncated.
3. Transforms the convolved data back to the physical spatial domain via `ifft`.

Because Phaethon's FFT operators natively track units, the entire convolution process happens without losing the physical metadata of the input field.

### API Reference

```python
phaethon.pinns.SpectralConv1d(
    in_channels: int, 
    out_channels: int, 
    modes: int
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">in_channels</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">The number of input features or physical channels.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">out_channels</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">The number of output features.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">modes</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">The number of low-frequency Fourier modes to retain. Frequencies beyond this mode limit are truncated, filtering out high-frequency spatial noise.</div>
</div>

### Example: Fourier Forward Pass

The layer integrates seamlessly into standard PyTorch sequences. You feed it a `PTensor`, and it returns a `PTensor` in the exact same physical dimension, ready to be activated.

```python
import torch
import torch.nn.functional as F
import phaethon.pinns as pnn
import phaethon.units as u

# Spatial grid of Length
# Shape: (Batch, Channels, Grid Size)
raw = torch.randn(1, 64, 256)
x_pt = pnn.PTensor(raw, unit=u.Meter)

# Init 1D Spectral Convolution
# Keeps 16 low-frequency modes
conv = pnn.SpectralConv1d(
    in_channels=64, 
    out_channels=64, 
    modes=16
)

# FFT -> Complex Matmul -> IFFT
spec_out = conv(x_pt)

print(spec_out.unit.dimension)
# Output: 'length'

# Activate raw magnitude
act_mag = F.gelu(spec_out.mag)

# Rewrap physical tensor
x_out = pnn.PTensor(
    act_mag, unit=x_pt.unit
)
```