---
seo_type: TechArticle
title: "Extending the Dimensional Registry"
description: "Extend the physics-constrained framework. Seamlessly synthesize custom physical dimensions, context-driven units, and real-time logarithmic scales."
keywords: "custom physical units python, extend dimensional registry, create custom physics dimension, logarithmic scale synthesis, context-driven physics units"
---

# Extending the Registry

Phaethon is not a closed ecosystem. The engine is designed to be fully extensible, allowing you to seamlessly integrate niche scientific units, fictional currencies, or entirely undiscovered physical dimensions into the core mathematical engine.

Custom units are created using Phaethon's 4-tier Class Hierarchy and the `phaethon.axiom` decorators. Once a class is evaluated by the Python interpreter, Phaethon's Metaclass automatically registers its `symbol` and `aliases`, making it instantly available across the entire framework.

---

## Adding a Unit to an Existing Dimension

If the physical dimension already exists (e.g., Length, Mass, Force), you simply need to inherit from its **Dimensional Class** and use `phaethon.axiom.derive` to tell Phaethon how it relates to existing units.

Let's add a fictional Force unit: The **Jedi Push**. Let's say 1 Jedi Push equals exactly 5000 Newtons.

````python
import phaethon as ptn
import phaethon.units as u

# Inherit from the existing ForceUnit dimensional class
@ptn.axiom.derive(5000 * u.Newton)
class JediPush(u.ForceUnit):
    symbol = "JP"
    aliases = ["jedi_push", "force_push"]

# It is now permanently registered! You can use it natively.
attacks = ptn.array([1.5, 2.0], unit='jedi_push')

# Convert back to SI seamlessly
in_newtons = attacks.to('N')
print(in_newtons)
# Output: <Newton Array: [ 7500. 10000.] N>
````

---

## Creating a Completely New Dimension

If you are working in a highly specialized domain (e.g., Magic Systems, Video Game Engine Physics, or Abstract Economics), you can define a completely new physical dimension from scratch.

You must first define the **Dimensional Class** (inheriting from `phaethon.units.BaseUnit`), set its boundary using `phaethon.axiom.bound`, and then define its **Base Unit** (multiplier = 1.0).

Let's create a new dimension called `ManaDensity` (Mana per Cubic Meter).

````python
import phaethon as ptn
import phaethon.units as u

# 1. Define the Dimensional Class
# Mana cannot be negative, and we mark it as abstract
@ptn.axiom.bound(min_val=0, msg="Mana density cannot be negative!", abstract=True)
class ManaDensityUnit(u.BaseUnit):
    dimension = "mana_density"

# 2. Define the Concrete Base Unit
# Let's say the base unit is "Crystal per Cubic Meter"
@ptn.axiom.derive(u.Dimensionless / u.Meter**3)
class CrystalPerCubicMeter(ManaDensityUnit):
    __base_unit__ = True  # Marks this as the absolute SI-equivalent baseline
    symbol = "Cr/m³"
    aliases = ["crystal_density"]

# 3. Define a Derived Unit
# Let's say 1 "Elven Orb" packs the density of 100 Crystals/m³
@ptn.axiom.derive(100 * CrystalPerCubicMeter)
class ElvenOrb(ManaDensityUnit):
    symbol = "EO"

# Usage:
elven_magic = ElvenOrb(5)
raw_crystals = elven_magic.to('crystal_density')

print(raw_crystals) # Output: 500 Cr/m³
print(elven_magic)  # Output: 5 EO

print(repr(raw_crystals))
# Output: <CrystalPerCubicMeter: 500.0 Cr/m³>

# View the canonical dimensional signature
print(elven_magic.decompose())
# Output: 500 1/m³
````

---

## Contextual & Logarithmic Axioms

Phaethon allows you to create units whose values shift dynamically based on runtime environments, or units that operate on logarithmic scales (like Decibels or pH).

### Context-Driven Units
You can build units that read from `phaethon.config` context variables by utilizing the `phaethon.axiom.scale` or `phaethon.axiom.shift` decorators.

````python
import phaethon as ptn
import phaethon.units as u

@ptn.axiom.bound(abstract=True)
@ptn.axiom.scale(ctx="inflation_rate", default=1.0)
class EconomicUnit(u.BaseUnit):
    dimension = "economics"

@ptn.axiom.derive(u.Dimensionless)
class GoldCoin(EconomicUnit):
    __base_unit__ = True
    symbol = "GC"

# Usage with context injection
with ptn.using(context={"inflation_rate": 1.5}):
    # The value of the coin is dynamically scaled!
    wealth = GoldCoin(100)
````

### Logarithmic Units
Creates non-linear units via `phaethon.axiom.logarithmic`. Phaethon will automatically protect these units from illegal mathematical operations (like exponentiation) and resolve their linear values during addition/subtraction.

````python
import phaethon as ptn
import phaethon.units as u

# A logarithmic scale for Earthquake Intensity
# Base 10, Multiplier 1.5, Reference is 1.0 Joule
@ptn.axiom.logarithmic(reference=u.Joule(1.0), multiplier=1.5, base=10.0)
class QuakeMagnitude(u.EnergyUnit):
    symbol = "QM"

quake = QuakeMagnitude(7.0)
print((~quake).dimension) 
# Output: 'energy' (Automatically linearizes to the base Joule!)
````

## The Axiom Decorators (`phaethon.axiom`)

The `phaethon.axiom` module is the physics rule engine of the framework. It provides a suite of class and function decorators that dynamically govern instantiation, scaling, boundaries, and mathematical operations. 

By decorating a class, you manipulate its underlying Metaclass behavior without needing to write complex `__init__` or `__new__` boilerplate.

### Dimensional Synthesis (`@derive`)

The primary engine for creating derived physical units. It synthesizes the dimensional signature (`_signature`) and calculates the exact SI `base_multiplier` by evaluating direct metaclass algebra.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">unit_expr</span>
    <span class="p-sep">—</span>
    <span class="p-type">type[BaseUnit]</span>
  </div>
  <div class="p-desc">A mathematical expression of existing unit classes (e.g., <code>Joule / Meter</code>).</div>
</div>

**Example Usage:**
```python
import phaethon as ptn
import phaethon.units as u

# Synthesizes the exact dimensional DNA of Force (Mass * Length / Time²)
@ptn.axiom.derive(u.Kilogram * u.Meter / u.Second**2)
class Newton(u.ForceUnit):
    symbol = "N"
```

### Physical Guardrails (`@bound`)

Enforces absolute minimum and maximum physical limits. It natively respects Phaethon's global strictness configurations (`axiom_strictness_level` and `default_on_error`), seamlessly integrating with the DataFrame `Schema` engine to sanitize arrays.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">min_val / max_val</span>
    <span class="p-sep">—</span>
    <span class="p-type">float | str</span>
  </div>
  <div class="p-desc">The boundary limits. Arrays containing values outside these limits will trigger the active error policy (raise, coerce, or clip).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">abstract</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, explicitly prevents developers from instantiating this class directly, forcing them to use concrete subclasses.</div>
</div>

**Example Usage:**
```python
# Blocks the creation of Kelvin values below Absolute Zero
@ptn.axiom.bound(min_val=0.0, msg="Temperature cannot fall below Absolute Zero!")
class Kelvin(TemperatureUnit):
    symbol = "K"
```

### Environmental Relativity (`@scale` & `@shift`)

Physical constants are rarely static. The `@scale` (multiplication) and `@shift` (addition/subtraction) axioms allow units to dynamically alter their conversion math based on a runtime `context` dictionary.

To build complex relationships, Phaethon provides the `CtxProxy` (aliased as `C`). It acts as a deferred mathematical expression that evaluates only when the unit is instantiated.

**Best Practice:** Import the proxy explicitly as `C` to keep mathematical formulas clean.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">ctx</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">The key to extract from the runtime context dictionary.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">formula</span>
    <span class="p-sep">—</span>
    <span class="p-type">CtxProxy</span>
  </div>
  <div class="p-desc">A deferred mathematical formula evaluated against the context at runtime.</div>
</div>

**Example Usage:**
```python
import phaethon as ptn
from phaethon.axiom import C

# The gauge shifts by atmospheric pressure.
# Formula: (Atmospheric Pressure * 2.5) + 100
@ptn.axiom.shift(
    op="add", 
    formula=(C("atmospheric_pressure", default=101325.0) * 2.5) + 100
)
class CustomGaugePressure(PressureUnit):
    symbol = "cgPa"
```

### Logarithmic Physics (`@logarithmic`)

A highly specialized axiom that rewrites the core conversion math to operate on logarithmic scales (e.g., Decibels, pH, Stellar Magnitude). 

It acts as an impenetrable shield: it automatically linearizes values during addition/subtraction, and strictly blocks mathematically impossible operations (like exponentiating or modulo dividing a logarithmic unit).

<div class="param-box">
  <div class="param-header">
    <span class="p-name">reference</span>
    <span class="p-sep">—</span>
    <span class="p-type">NumericLike | BaseUnit</span>
  </div>
  <div class="p-desc">The linear reference baseline (e.g., <code>1.0 Watt</code> for dBW).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">multiplier / base</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">The log formula parameters. Example for Power: multiplier <code>10.0</code>, base <code>10.0</code>.</div>
</div>

**Example Usage:**
```python
@ptn.axiom.logarithmic(reference=u.Watt(1.0), multiplier=10.0, base=10.0)
class DecibelWatt(PowerUnit):
    symbol = "dBW"

# Phaethon blocks impossible math automatically
signal = DecibelWatt(30)
# signal ** 2 -> Raises AxiomViolationError!
```

### Function Gatekeepers (`@require` & `@prepare`)

These decorators are not for classes; they wrap standard Python functions to ensure they interact safely with Phaethon's physical tensors.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">@require</span>
    <span class="p-sep">—</span>
    <span class="p-type">Decorator</span>
  </div>
  <div class="p-desc">Halts execution if the arguments passed to the function do not match the explicitly specified physical dimensions or unit classes.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">@prepare</span>
    <span class="p-sep">—</span>
    <span class="p-type">Decorator</span>
  </div>
  <div class="p-desc">Intercepts incoming physical tensors, explicitly casts them to the requested baseline unit, and strips the physics envelope away—passing only pure <code>.mag</code> floats into the function. Perfect for wrapping external C/C++ libraries.</div>
</div>

**Example Usage:**
```python
import math

# Guarantees the function only receives a raw float representing Radians
@ptn.axiom.prepare(angle_input=u.Radian)
def fast_c_sine_wave(angle_input):
    return math.sin(angle_input)

# The user safely passes Degrees; Phaethon handles the conversion and stripping
result = fast_c_sine_wave(angle_input=u.Degree(90))
```