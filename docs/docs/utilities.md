---
seo_type: TechArticle
title: "Utility API: Visualization & Inspection"
description: "Diagnostic tools for scientific computing. Safely unwrap physical tensors for Matplotlib visualization, generate axis labels, and introspect the registry."
keywords: "plot physical tensors python, matplotlib physics units, auto generate physics axis labels, introspect unit registry, scientific diagnostic API"
---

# Utility & Diagnostic API

The Phaethon ecosystem is built on layers of abstraction—from NumPy dimensional wrappers to PyTorch autograd computational graphs. 

The functions in this module provide low-level tools to safely strip those abstractions away for visual analytics (like Matplotlib or Plotly) and to introspect the global `UnitRegistry`.

---

## Visual Analytics Adapters

When feeding data into standard plotting libraries, passing complex custom objects often leads to unexpected behaviors or crashes. Phaethon provides universal extractors to prepare your data.

### `phaethon.unwrap()`

Universally extracts numerical payloads (NumPy arrays or primitives) from any Phaethon or PyTorch object. It safely detaches PyTorch computational graphs, unwraps `BaseUnits`, converts Decimals, and strips Pandas/Polars indices, making the data 100% safe for visualization tools.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">*args</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">One or more Phaethon BaseUnits, PTensors, PyTorch Tensors, Pandas Series, or a Dictionary containing them.</div>
</div>

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">np.ndarray | tuple | dict</span>
  </div>
  <div class="p-desc">A single NumPy array, a tuple of arrays, or a dictionary of arrays, matching the input structure.</div>
</div>

**Example Usage:**
```python
import phaethon as ptn
import matplotlib.pyplot as plt

# 1. Unwrapping multiple objects for X-Y plotting
x_np, y_np = ptn.unwrap(time_ptensor, velocity_baseunit)
plt.plot(x_np, y_np)

# 2. Unwrapping a Phaethon Dataset (.astensor output)
dataset = MySchema.astensor(df)
numpy_dict = ptn.unwrap(dataset)

plt.scatter(numpy_dict['v'], numpy_dict['drag'])
```

### `phaethon.symtag()`

Generates a scientifically formatted axis label (e.g., `"Velocity (m/s)"`). It intelligently extracts dimensions and symbols safely from PTensors or BaseUnits.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">label</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | None</span>
  </div>
  <div class="p-desc">The base text for the axis (e.g., <code>'Time'</code>). If <code>None</code>, only the unit symbol is returned.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">obj</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">The source object to extract the unit symbol from.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">auto_unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>False</code>, ignores the physical unit and returns the label as-is.</div>
</div>

**Example Usage:**
```python
# 1. Standard Physics Labeling
import phaethon.pinns as pnn
ptn.symtag("Velocity", pnn.PTensor([10], unit=u.MeterPerSecond))
# Output: 'Velocity (m/s)'

# 2. Ignoring Unit for Semantic/Dimensionless Tensors
ptn.symtag("Status ID", torch.tensor([0, 1]))
# Output: 'Status ID'
```

---

## Registry Introspection

These functions act as public wrappers around the global `UnitRegistry`, allowing you to inspect the active dimensions and classes currently loaded into the Python environment.

### `phaethon.dims()`

Retrieves a sorted list of all unique physical dimensions currently registered in the engine.

**Returns:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">list[str]</span>
  </div>
  <div class="p-desc">A list of dimension names.</div>
</div>

**Example:**
```python
print(ptn.dims())
# Output: ['acceleration', 'area', 'energy', 'force', 'length', 'mass', ...]
```

### `phaethon.unitsin()`

Retrieves all units associated with a specific physical dimension.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">dimension</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">The dimension name (e.g., <code>'mass'</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">ascls</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, returns the actual Class objects. If <code>False</code> (Default), returns a list of string symbols/aliases.</div>
</div>

**Example:**
```python
print(ptn.unitsin('length', ascls=False))
# Output: ['m', 'km', 'cm', 'mm', 'inch', 'ft', ...]

print(ptn.unitsin('temperature', ascls=True))
# Output: [<class 'Celsius'>, <class 'Fahrenheit'>, <class 'Kelvin'>, ...]
```

### `phaethon.baseof()`

Retrieves the canonical "Anchor" base unit class for a specific dimension. The anchor unit is the absolute reference point (multiplier = 1.0, offset = 0.0) for all conversions within that dimension.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">dimension</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">The dimension name.</div>
</div>

**Example:**
```python
anchor = ptn.baseof('temperature')
print(anchor.symbol)
# Output: 'K'
```

### `phaethon.dimof()`

Resolves the physical dimension of a string alias, a Unit Class, or an instantiated Unit/PTensor.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">obj</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type | BaseUnit</span>
  </div>
  <div class="p-desc">The object to inspect.</div>
</div>

**Example:**
```python
print(ptn.dimof('kg'))           
# Output: 'mass'

print(ptn.dimof(u.Celsius))      
# Output: 'temperature'

print(ptn.dimof(u.Meter(10)))    
# Output: 'length'
```