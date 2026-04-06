---
seo_type: TechArticle
title: "Scientific Computing: Linalg & Math"
description: "Physics-aware linear algebra for scientific computing. Track physical dimensions through matrix inversion, determinants, and stochastic distributions."
keywords: "physics-aware linear algebra, dimensional matrix inversion python, stochastic physics tensor, calculate determinant with units, numpy physical algebra"
---

# Scientific Computing

While Phaethon seamlessly intercepts standard mathematical operators (`+`, `-`, `*`, `/`), real-world scientific computing relies heavily on matrix operations and stochastic simulations. 

The `phaethon.linalg` and `phaethon.random` modules provide physics-aware wrappers around NumPy's core routines. These modules don't just calculate numbers; they actively synthesize, invert, and scale physical dimensions in real-time to match the mathematical transformation.

---

## Linear Algebra (`phaethon.linalg`)

In physical linear algebra, operations like matrix inversion or determinants fundamentally alter the dimensional DNA of the tensor. Phaethon tracks these transformations automatically.

### phaethon.linalg.inv

Computes the (multiplicative) inverse of a physical matrix. In dimensional algebra, the inverse of a matrix A with dimension [D] results in a matrix with dimension [1/D].

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">a</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">A square physical tensor.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A new tensor representing the inverse matrix with inverted physical dimensions.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn

mat = ptn.array([[4.0, 7.0], [2.0, 6.0]], unit='meter')
inv_mat = ptn.linalg.inv(mat)

print(inv_mat.dimension)
# Output: 'linear_attenuation' (which is 1/Length)
```

### phaethon.linalg.det

Computes the determinant of a physical matrix. The determinant of an N x N matrix with dimension [D] synthesizes a new physical dimension of [D^N]. 

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">a</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">A square physical tensor.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A scalar tensor representing the determinant with exponentiated dimensions.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn

# A 3x3 matrix of Length (Meter)
A_3x3 = ptn.array([[1, 2, 3], [0, 1, 4], [5, 6, 0]], unit='meter')

# The determinant of a 3D length matrix is Volume!
det_vol = ptn.linalg.det(A_3x3)

print(det_vol.dimension)
# Output: 'volume'
```

### phaethon.linalg.solve

Solves a linear matrix equation, or system of linear scalar equations (Ax = B). In physics, if A * x = B, then the dimension of the solution x must exactly equal the dimension of B divided by the dimension of A.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">a</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Coefficient physical matrix.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">b</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit | Any</span>
  </div>
  <div class="p-desc">Ordinate or "dependent variable" physical values.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A physical tensor 'x' satisfying the equation Ax = B.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

# Newton's Second Law matrix solver: M * a = F  =>  a = M⁻¹ * F
M_mass = ptn.array([[10.0, 2.0], [3.0, 5.0]], unit=u.Kilogram)
F_force = ptn.array([50.0, 25.0], unit=u.Newton)

# Solving for acceleration
accel_x = ptn.linalg.solve(M_mass, F_force)

print(accel_x.dimension)
# Output: 'acceleration'
```

### phaethon.linalg.norm

Computes the matrix or vector norm. Unlike determinants or inverses, the norm of a physical vector (like velocity or force) calculates its magnitude. Therefore, the physical dimension remains completely unaltered.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">x</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Input physical tensor.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">ord, axis, keepdims</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Standard NumPy norm parameters.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

# Velocity vector (m/s)
vec_v = ptn.array([3.0, 4.0], unit=u.MeterPerSecond)

# The magnitude of velocity is still velocity (speed)
mag_v = ptn.linalg.norm(vec_v)

print(mag_v)
# Output: 5.0 m/s
```

---

## Stochastic Physics (`phaethon.random`)

Generates highly-optimized stochastic tensors that are instantly bounded by physical dimensions.

!!! warning "Axiom Bounds & Stochastic Generation"
    Because `phaethon.random` functions automatically instantiate new `BaseUnit` tensors under the hood, generating stochastic values that violate the target unit's physical boundaries (e.g., generating negative `Kelvin` or `Mass`) will immediately trigger an `AxiomViolationError` under the `default` axiom strictness level. 
    
    To prevent unexpected crashes in your simulations, ensure your distribution parameters (`low`, `loc`, `scale`) remain within physically valid ranges, or temporarily adjust the axiom's strictness level using [`phaethon.using()`](config.md) or [`phaethon.config()`](config.md).

### phaethon.random.uniform / normal

Draws samples from continuous distributions (Uniform or Gaussian) and injects physical DNA.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">low, high / loc, scale</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">Distribution boundaries or mean/standard deviation.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">size</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Output array shape.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The physical dimension to attach.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn

# Uniform: Generate a 3x3 matrix of random pressures (10.5 to 20.5 Pascal)
pressures = ptn.random.uniform(low=10.5, high=20.5, size=(3, 3), unit='Pa')

# Normal: Generate 10 random mass values with a mean of 100kg
mass_dist = ptn.random.normal(loc=100.0, scale=2.5, size=10, unit='kg')
```

### phaethon.random.poisson

Draws samples from a Poisson distribution. Extremely useful in Phaethon for modeling discrete physical events over a continuous interval, such as radioactive decays (`u.Becquerel`) or photon strikes (`u.Photon`).

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">lam</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">Expected number of events occurring in a fixed-time interval.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The physical dimension to attach.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

# Simulating radioactive decay events per second (Becquerel)
# Expected average (lam) = 50 decays
decays = ptn.random.poisson(lam=50.0, size=(3,), unit=u.Becquerel)

print(decays.dimension)
# Output: 'radioactivity'
```

### phaethon.random.exponential

Draws samples from an exponential distribution. Ideal for simulating the time between independent physics events, such as the decay time of radioactive isotopes or thermodynamic relaxation times.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">scale</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">The scale parameter (beta = 1/lambda). Must be non-negative.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The physical dimension to attach (typically 's' or u.Second).</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

# Simulating time between particle arrivals (average 1.5 seconds)
arrival_times = ptn.random.exponential(scale=1.5, size=(3,), unit=u.Second)

print(arrival_times.dimension)
# Output: 'time'
```