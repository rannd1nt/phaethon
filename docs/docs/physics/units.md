---
seo_type: TechArticle
title: "Units & Tensors: NumPy Subclassing"
description: "Not a wrapper, but a native NumPy subclass. Deep C-API integration for Python units, offering zero-overhead physical tensors and flawless IDE type hinting."
keywords: "python units, numpy subclassing, python physical quantities, modern alternative to pint, python unit conversion, native numpy physics tensor"
---

# Units & Tensors

The `phaethon.units` module is the mathematical core of the Phaethon framework. At its center is the `BaseUnit`—a highly optimized, dimensionally-aware tensor that deeply integrates with NumPy's C-API. 

While `BaseUnit` is the underlying engine, you will never instantiate it directly. Instead, you interact with its concrete descendants (like `u.Meter`, `u.Newton`, or `u.Decibel`). Every physical entity you instantiate inherits a massive arsenal of properties, array mechanics, formatting tools, and casting methods from this foundational class.

*(Note: For documentation on how these units interact mathematically via operators like `+` or `*`, please refer to the [Dimensional Algebra](algebra.md) section).*

!!! note "BaseUnit (NumPy) vs. PTensor (PyTorch)"
    The `BaseUnit` class documented here is a pure **NumPy subclass** meant for high-speed CPU computations and Data Engineering. If you are building Physics-Informed Neural Networks (PINNs) and require autograd/GPU tracking, do not use `BaseUnit`. Instead, use the specialized PyTorch equivalent: [`PTensor`](../pinns/tensors.md).

---

## Unit Instantiation

The most direct way to create a physical entity in Phaethon is by calling the unit's class constructor directly. Because Phaethon is built on top of NumPy, these constructors natively accept scalars, standard Python lists, or raw multidimensional arrays.

**Example Usage:**

```python
import phaethon.units as u
import numpy as np

# 1. Scalar Instantiation
temperature = u.Kelvin(300.5)

# 2. Vector / List Instantiation
velocities = u.MeterPerSecond([10.0, 15.5, 20.0])

# 3. Wrapping Raw NumPy Tensors
raw_grid = np.random.rand(10, 10)
pressure_field = u.Pascal(raw_grid)

print(pressure_field.shape)
# Output: (10, 10)
```

---

## Native Array Proxies (NumPy Protocol)

Legacy unit libraries use slow, high-level "wrappers" that degrade performance. Phaethon takes a hyper-optimized approach: it implements the **NumPy Array Protocol** (`__array_ufunc__` and `__array_function__`). 

While structurally storing the array, `BaseUnit` acts as a **Zero-Overhead Native Proxy**. It completely bypasses Python-level bottlenecks by directly intercepting math operations at the NumPy C-API layer, ensuring your arrays retain their physical DNA without sacrificing raw C-speed.

### phaethon.array

A fast, physics-aware tensor constructor. It seamlessly converts Python lists, scalars, or existing NumPy `ndarray` objects directly into a Phaethon NumPy subclass, permanently fusing the specified physical dimension into the array.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">object</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">The raw data. Can be a scalar, a nested Python list, or a NumPy <code>ndarray</code>.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The physical dimension to attach. Can be a string alias (e.g., <code>'kg'</code>) or a class.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">dtype</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any | None</span>
  </div>
  <div class="p-desc">The desired data type. Defaults to the most efficient continuous type.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A new physics tensor wrapping the array data.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

velocity = ptn.array([[10.5, 20.1], [5.0, 9.8]], unit=u.MeterPerSecond, dtype="float32")
print(velocity.shape)
# Output: (2, 2)
```


### phaethon.asarray

Converts the input to an array, attaching physics **without copying** the underlying memory if the input is already a compatible `ndarray`. Essential for wrapping massive simulation grids with zero overhead.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">a</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Input data, in any form that can be converted to an array.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The physical dimension to safely wrap around the memory pointer.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A physics tensor sharing memory with the original array (if compatible).</div>
</div>

**Example Usage:**

```python
import numpy as np
import phaethon as ptn

# A massive 1GB numerical grid
massive_grid = np.zeros((1000, 1000, 125))

# Wraps the pointer instantly without duplicating the 1GB memory
physical_grid = ptn.asarray(massive_grid, unit='J')
```


### phaethon.asanyarray

Similar to `asarray`, but allows subclasses of `ndarray` (like `numpy.ma.MaskedArray`) to pass through without losing their subclass identity. Phaethon preserves the subclass behavior entirely inside the physics envelope.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">a</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Input data or array subclass.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The physical dimension to attach.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A physics tensor wrapping the array or array subclass.</div>
</div>

**Example Usage:**

```python
import numpy.ma as ma
import phaethon as ptn

# A masked array containing invalid/missing sensor data
sensor_data = ma.masked_array([10.5, -999.0, 12.0], mask=[0, 1, 0])

# Phaethon preserves the mask inside the physics tensor
safe_temp = ptn.asanyarray(sensor_data, unit='degC')

print(safe_temp.mag.mask)
# Output: [False  True False]
```

---

## Properties & Array Mechanics

Every instantiated physical tensor automatically exposes NumPy-native properties and methods. These methods route calculations directly to the underlying C-engine while perfectly preserving their physical dimension.

### Core Properties

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.mag</span>
    <span class="p-sep">—</span>
    <span class="p-type">float | ndarray</span>
  </div>
  <div class="p-desc"><strong>Magnitude.</strong> Returns the raw numerical value without physical metadata.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.dimension</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Returns the canonical name of the physical dimension (e.g., <code>"energy"</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.shape</span>
    <span class="p-sep">—</span>
    <span class="p-type">tuple[int, ...]</span>
  </div>
  <div class="p-desc">Tuple of array dimensions. Returns an empty tuple <code>()</code> for scalars.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.ndim</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">Number of array dimensions (0 for scalars, 1 for vectors, 2 for matrices, etc.).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.symbol</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | None</span>
  </div>
  <div class="p-desc">Retrieve the symbol of a unit as a string.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.aliases</span>
    <span class="p-sep">—</span>
    <span class="p-type">list[str] | None</span>
  </div>
  <div class="p-desc">Retrieve a list of strings containing all aliases for a unit.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.T</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Returns the transposed physical tensor.</div>
</div>

### Shaping & Reductions

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.reshape(shape)</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Gives a new shape to the physical tensor without changing its data.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.flatten()</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Return a copy of the tensor collapsed into one dimension.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.sum(axis=None, keepdims=False)</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Sum of tensor elements over a given axis. Physical dimension remains identical.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.mean(axis=None, keepdims=False)</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Compute the arithmetic mean along the specified axis.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.max() / .min()</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Returns the maximum or minimum value along a given axis.</div>
</div>

### NumPy Subclassing & Delegation

Phaethon's `BaseUnit` acts as a highly optimized NumPy proxy. It intercepts NumPy's C-API calls via `__array_ufunc__` and `__array_function__`, allowing you to use native NumPy functions directly on physical tensors.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">np.sum / np.max / np.mean</span>
  </div>
  <div class="p-desc">Standard mathematical reductions natively return a Phaethon tensor preserving the original physical dimension.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">np.abs / np.negative / np.rint</span>
  </div>
  <div class="p-desc">Unary universal functions (ufuncs) are strictly routed through the physics engine.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">np.sqrt / np.cbrt / np.square</span>
  </div>
  <div class="p-desc">These functions are intercepted and transformed into dimensional algebra (e.g., <code>np.sqrt(Area)</code> automatically returns <code>Length</code>).</div>
</div>

**Example Usage:**

```python
import numpy as np
import phaethon.units as u
import phaethon as ptn

# instantiating a negative velocity
with ptn.using(axiom_strictness_level='ignore'):
    velocities = u.MeterPerSecond([-10.0, 5.0, -2.5])

# Absolute value is safely passed to the NumPy C-Engine
absolute_v = np.abs(velocities)
print(absolute_v)
# Output: <MeterPerSecond Array: [10.   5.   2.5] m/s>

# NumPy square triggers Dimensional Synthesis
squared = np.square(velocities)
print(squared)
# Output: <JoulePerKilogram Array: [100, 25, 6.25]>

print(squared.dimension)
# Output: 'specific_energy'
```

**Direct Attribute Delegation:**
If a specific NumPy method is not natively overridden by Phaethon, the tensor will automatically search the underlying NumPy `ndarray` and delegate the call, wrapping the result back into the physics envelope if applicable.

```python
# Using a native NumPy attribute directly on a Phaethon tensor
print(velocities.size)
# Output: 3
```

---

## Diagnostics & Formatting

Phaethon units provide powerful built-in methods to inspect their underlying SI structure or format their output for UIs.

### .decompose()

Returns a string representation of the unit's absolute, canonical SI base structure (its fundamental DNA). It breaks down complex derived units (like Watts or Pascals) into their fundamental SI exponents (Kilograms, Meters, Seconds, etc.).

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">str</span>
  </div>
  <div class="p-desc">The SI mathematical signature.</div>
</div>

**Example Usage:**

```python
import phaethon.units as u

pressure = u.Pascal(100)

print(pressure.decompose())
# Output: kg/(m·s²)
```

### .format()

Applies precise structural and numeric formatting to the magnitude using pure float formatting, bypassing the default `__str__` behavior.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">prec</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">Number of decimal places to round to (Default: <code>4</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">sigfigs</span>
    <span class="p-sep">—</span>
    <span class="p-type">int | None</span>
  </div>
  <div class="p-desc">Overrides precision to strictly enforce Significant Figures.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">scinote</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">Force the output into Scientific Notation.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">delim</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool | str</span>
  </div>
  <div class="p-desc">Adds thousands separators (e.g., <code>True</code> for <code>","</code>, or supply a custom string like <code>"."</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">tag</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">Whether to append the unit symbol at the end of the string (Default: <code>True</code>).</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">str</span>
  </div>
  <div class="p-desc">A highly formatted string representation of the unit.</div>
</div>

**Example Usage:**

```python
import phaethon.units as u

distance = u.Meter(12500.55)

print(distance.format(delim=True, prec=1))
# Output: 12,500.6 m

print(distance.format(scinote=True, sigfigs=3, tag=False))
# Output: 1.25E+04
```

---

## Dimensional Casting & Escaping

Phaethon is designed to be strictly typed and physically guarded. However, advanced scientific computing often requires traversing domains, stripping semantic ghosts, or linearizing complex logarithmic scales. Phaethon provides deterministic methods to safely navigate these operations.

### .to() (Standard Casting)

Safely converts the unit instance to another physical unit within the **same** semantic domain. This operation is strictly guarded by the Physics Engine.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">target_unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The destination physical unit class or string alias.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">BaseUnit</span>
  </div>
  <div class="p-desc">A new instance safely cast to the requested unit.</div>
</div>

**Raises:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">TypeError</span>
  </div>
  <div class="p-desc">If the provided target is not a valid Phaethon class or registered alias.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">DimensionMismatchError</span>
  </div>
  <div class="p-desc">If you attempt to convert between fundamentally incompatible physics (e.g., Length to Mass).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">SemanticMismatchError</span>
  </div>
  <div class="p-desc">If you attempt to cross an <strong>Exclusive Domain Lock</strong> or trigger a <strong>Phantom Collision</strong> without explicit algebraic synthesis.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

distance = ptn.array([1.5, 3.2], unit='km')
speed = u.MeterPerSecond(150)

meters = distance.to('m') # <Meter Array: [1500.0, 3200.0]>
kmh = speed.to(u.KilometerPerHour) # # <KilometerPerHour: 540.0 km/h>
```


### .si (The Core Extractor / De-Phantomizer)

The semantic escape hatch. It explicitly attacks the **DNA** of the unit. It strips away all Phantom Units (e.g., `cycle`, `decay`, `radian`), gracefully downgrading the entity to its pure, generic SI blank canvas (multiplier = `1.0`).

Use this when you need to intentionally break a domain lock (e.g., extracting raw energy from torque) to perform generalized mathematics.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">Property Type:</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">Returns a newly synthesized, generic BaseUnit free from semantic constraints.</div>
</div>

**Example Usage:**

```python
import phaethon.units as u

# Torque possesses an Exclusive Domain Lock and a Phantom Unit (Angle⁻¹)
torque = u.NewtonMeter(100)  
print(torque.dimension)  
# Output: 'torque'

# Extracting the core strips the Phantom Unit, collapsing it back to basic Energy
raw_energy = torque.si  

print(raw_energy.dimension)
# Output: 'energy'

print(raw_energy)
# Output: <Joule: 100.0 J>
```


### ~ (The Base Converter / Linearizer)

The absolute canonical scale converter (triggered using the bitwise NOT `~` operator). Unlike `.si` which attacks the semantics, `~` attacks the **Scale**. 

It forces any derived multiplier (like `kilo`), physical constant (like `SpeedOfLight`), or non-linear shell (like `Decibel`) to collapse directly into the primary SI Base Unit of its respective dimension, **while perfectly preserving its Semantic Domain Lock.** It is also the primary tool for instantly linearizing logarithmic physics.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">Operator:</span>
    <span class="p-type">__invert__</span>
  </div>
  <div class="p-desc">Returns the linearized, SI Base Unit of the current dimensional state without stripping phantom semantics.</div>
</div>

**Example Usage: Scale Unrolling vs Semantic Extraction**

```python
import phaethon.units as u

# 1. Unrolling a Physical Constant
c = u.SpeedOfLight(1)
print(~c) 
# Output: <MeterPerSecond: 2.9979E+08 m/s>

# 2. Preserving the Semantic Domain
torque = u.NewtonMeter(100)
print(~torque) 
# Output: <NewtonMeter: 100.0 N·m> (Notice it remains Torque, unlike .si!)

# 3. Linearizing Logarithmic Scales natively
signal = u.DecibelMilliwatt(30.0) # 30 dBm

# Both approaches yield the linear SI Base (Watt), 
# because stripping the log shell naturally reveals the linear base core.
linear_power = ~signal            
si_power = signal.si              

print(linear_power)
# Output: <Watt: 1.0 W>

print(si_power.to(u.Milliwatt)) 
# Output: <Milliwatt: 1000.0 mW>
```