---
seo_type: TechArticle
title: "Specialized Domains & Hierarchy"
description: "Phaethon's 4-tier unit hierarchy for scientific computing. Utilize domain-specific properties like trigonometric wrapping and thermodynamic scale checks."
keywords: "python physical domain methods, angle wrapping python physics, thermodynamic scale check, frequency to period python, physics unit hierarchy"
---

# Specialized Domains & Hierarchy

While every physical entity in Phaethon inherits the universal vectorization and casting abilities of the `BaseUnit`, they also possess domain-specific superpowers. A temperature reading knows how to check if it's absolute, an angle knows how to wrap itself within a circle, and digital data knows how to scale into binary prefixes.

These abilities are governed by Phaethon's strict, multi-tiered class hierarchy.

---

## The Physics Class Hierarchy

To understand how domain-specific methods and physics constraints (Axioms) are distributed, you must understand Phaethon's 4-tier inheritance model:

1. **BaseUnit (The God Class):** The ultimate abstract parent. It provides the core NumPy integration, dimensional algebra logic, and properties like `.mag` and `.dimension`. You cannot instantiate this directly.
2. **Dimensional Class (e.g., `PressureUnit`):** Inherits from `BaseUnit`. This abstract class defines the shared dimensional string (e.g., `"pressure"`) and acts as the host for `@axiom.bound` (setting minimum/maximum physical limits). **Domain-specific methods live here.**
3. **Contextual Class (e.g., `GaugePressureUnit`):** An optional, intermediate abstract class. It is used to apply environmental relativity using decorators like `@axiom.shift` (e.g., shifting gauge pressure by atmospheric pressure).
4. **Unit Class (e.g., `Pascal`, `PSIG`):** The concrete, instantiable leaf nodes. They define symbols, aliases, and use `@axiom.derive` if they are constructed from other base units.

### Hierarchy Example: Pressure

```python
import phaethon as ptn
import phaethon.units as u

# 1. Dimensional Class (Bound by a perfect vacuum)
@ptn.axiom.bound(min_val=0, abstract=True)
class PressureUnit(u.BaseUnit):
    dimension = "pressure"

# 2. Contextual Class (Relies on atmospheric context)
@ptn.axiom.bound(abstract=True)
@ptn.axiom.shift(ctx="atmospheric_pressure", default=101325.0, op="add")
class GaugePressureUnit(PressureUnit):
    pass

# 3. Concrete Unit Classes
@ptn.axiom.derive(u.Newton / u.Meter**2)
class Pascal(PressureUnit):
    __base_unit__ = True
    symbol = "Pa"

@ptn.axiom.derive(u.PoundForce / u.Inch**2)
class PSIG(GaugePressureUnit):
    symbol = "psig"
```

---

## Domain-Specific Methods

Because methods are attached to Dimensional Classes, they are automatically inherited by all valid units within that domain.

### Geometry & Angles (`AngleUnit`)

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.wrap()</span>
    <span class="p-sep">—</span>
    <span class="p-type">AngleUnit</span>
  </div>
  <div class="p-desc">Wraps an angle to the standard [0, 360) degree or [0, 2π) radian range.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.to_dms()</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Converts the angle into a formatted Degrees, Minutes, Seconds string.</div>
</div>

### Thermodynamics (`TemperatureUnit`)

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.isabsolute</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">Returns True if the temperature scale starts at absolute zero (e.g., Kelvin, Rankine).</div>
</div>

### Time & Duration (`TimeUnit`)

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.flex(range, delim)</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Deconstructs a total time duration into a natural language format (e.g., "1 year 2 months").</div>
</div>

### Frequency (`FrequencyUnit`)

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.period</span>
    <span class="p-sep">—</span>
    <span class="p-type">TimeUnit</span>
  </div>
  <div class="p-desc">Returns the time period (1/f) as a physical Time tensor.</div>
</div>

### Digital Data Storage (`DataUnit`)

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.bin()</span>
    <span class="p-sep">—</span>
    <span class="p-type">DataUnit</span>
  </div>
  <div class="p-desc">Auto-scales the data size to the most appropriate Binary/IEC unit (KiB, MiB, GiB).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.dec()</span>
    <span class="p-sep">—</span>
    <span class="p-type">DataUnit</span>
  </div>
  <div class="p-desc">Auto-scales the data size to the most appropriate Decimal/SI unit (KB, MB, GB).</div>
</div>

### Electromagnetism (`ElectricPotentialUnit`)

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.rms()</span>
    <span class="p-sep">—</span>
    <span class="p-type">ElectricPotentialUnit</span>
  </div>
  <div class="p-desc">Returns the Root Mean Square (RMS) value for a sinusoidal voltage wave.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.peak()</span>
    <span class="p-sep">—</span>
    <span class="p-type">ElectricPotentialUnit</span>
  </div>
  <div class="p-desc">Calculates the peak voltage value from an RMS reading.</div>
</div>

**Domain Methods in Action:**

```python
import phaethon.units as u

# Geometry
print(u.Degree(90).to(u.ArcMinute).wrap())       # Output: 5400.0 arcmin
print(u.Radian(1).to_dms())                      # Output: 57° 17' 44.81"

# Thermodynamics
print(u.Celsius(-37).isabsolute)                 # Output: False
print(u.Celsius(-37).to(u.Kelvin).isabsolute)    # Output: True

# Time & Frequency
print(u.Megahertz(0.5).period)                   # Output: 2.0000E-06 s
print(u.Year(3.21031).flex())                    # Output: 3 years 2 months 2 weeks 1 day 22 hours...

# Data Storage
print(u.Terabyte(1).bin())                       # Output: 931.3226 GiB

# Electromagnetism
print(u.Kilovolt(3.45).rms())                    # Output: 2.4395 kV
```

---

## Protecting Custom Physics Functions

When writing custom formulas or scientific pipelines, relying on arbitrary floats is dangerous. Phaethon provides two powerful decorators in the `phaethon.axiom` module to enforce domain compliance on standard Python functions.

### @axiom.require

Acts as an absolute guardrail. It forces incoming arguments to match a specific dimensional string or an exact Unit Class. If the user passes the wrong physical entity, it halts execution immediately.

```python
import phaethon as ptn
import phaethon.units as u

# The function demands 'mass' and 'acceleration' dimensions
@ptn.axiom.require(m="mass", a="acceleration")
def calculate_force(m, a):
    return m * a

# Valid execution
f = calculate_force(m=u.Kilogram(10), a=u.GravityPerSecond(1))

# Crash: Passing Volume instead of Acceleration
f_error = calculate_force(m=u.Kilogram(10), a=u.CubicMeter(5))
# DimensionMismatchError: Argument 'a' expected 'acceleration', got 'volume'.
```

### @axiom.prepare

A data-preprocessing pipeline for pure math functions. It intercepts Phaethon tensors, converts them to your specifically requested baseline units, and explicitly strips away the physical envelope, injecting pure `.mag` floats/arrays into your function.

This is highly recommended when wrapping external C/C++ libraries or legacy codebases that do not understand Phaethon objects.

```python
import phaethon as ptn
import phaethon.units as u
import math

# Automatically casts 'angle_input' to Radians, then strips it to a raw float
@ptn.axiom.prepare(angle_input=u.Radian)
def pure_math_sine_wave(angle_input):
    # angle_input is guaranteed to be a raw float representing Radians
    return math.sin(angle_input)

# The user passes Degrees
result = pure_math_sine_wave(angle_input=u.Degree(90))

print(result)
# Output: 1.0 (Since sin(90 deg) == sin(π/2 rad) == 1.0)
```