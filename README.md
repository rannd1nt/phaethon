<div align="center">

<h1>Chisa - Dimensional Algebra & Physics Modelling Framework</h1>

<p>
<img src="https://img.shields.io/badge/MADE_WITH-PYTHON-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/INTEGRATION-NUMPY-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/LICENSE-MIT-red?style=for-the-badge" alt="License">
</p>

<p>
<a href="https://github.com/USERNAME/Chisa/issues">
<img src="https://img.shields.io/badge/Maintained%3F-Yes-238636?style=flat-square" alt="Maintenance">
</a>
<img src="https://img.shields.io/badge/Version-0.1.0-orange?style=flat-square" alt="Version">
</p>

</div>

**Chisa** is a logic-driven dimensional algebra and strict physics modeling framework for Python, powered by seamless NumPy vectorization. It merges the accessibility of a fluent conversion API with the rigorous architectural guardrails of an Object-Oriented physics engine.

Going beyond standard unit conversion, Chisa acts as a **Dimensional Integrity Enforcer** for your application. It features the **Axiom Engine** for modeling real-world physical limits, **Bidirectional Type Inferencing** to eliminate unit ambiguity, and native **C-Struct Array bypassing** for high-performance machine learning and data science workloads.

---

## Why a "Framework" and not just a Library?

A standard conversion library provides passive tools you call to multiply a number by a constant. **Chisa dictates the architecture of your physical data**. By utilizing Inversion of Control via Python decorators, Chisa provides a foundation where you define the rules of reality.

You construct mathematical constraints (e.g., Temperature cannot drop below Absolute Zero), derive complex units using physical formulas ($W = J/s$), and rely on the engine to autonomously intercept and prevent cross-dimensional logic errors before they corrupt your scientific pipelines.

---

## Key Features

* **Dual Engine API:** Use the *Fluent API* for quick, readable conversions, or the *Explicit OOP API* for strict mathematical operations.
* **Native Vectorization:** Drop multi-dimensional `numpy.ndarray` objects directly into Chisa. It bypasses scalar bottlenecks and processes millions of data points instantly.
* **The Axiom Ruleset:** Python class decorators (`@axiom`) that govern physical boundaries, dynamic context-scaling (e.g., Mach speed relative to temperature), and dimension synthesis.
* **Smart Inferencing:** Resolves ambiguous abbreviations (e.g., `'m'` for meter vs. minute) dynamically based on the target context.

---

## The Core Architecture (How Chisa Thinks)

At its absolute core, Chisa normalizes every unit into a universal "Base Value" using a highly optimized linear transformation. When you instantiate a unit, the engine calculates its true physical magnitude using this equation:

$$
y = (x + c) \cdot m
$$

Where:
- $x$ — The input magnitude provided by the user.
- $c$ — base_offset (e.g., -273.15 for converting Celsius to Kelvin). Controlled dynamically by `@axiom.shift`.
- $m$ — The `base_multiplier` (e.g., 1000 for converting Kilometers to Meters). Controlled dynamically by `@axiom.scale` and `@axiom.derive`.
- $y$ — The normalized absolute Base Value safely stored in the engine.

By exposing decorators rather than raw classes, Chisa allows you to dynamically inject physical variables into $c$ and $m$ at runtime.

---

## Precision & Type Safety (`.mag` vs `.exact`)
Chisa dynamically juggles standard `float`, ultra-precise `decimal.Decimal`, and vectorized numpy.ndarray. To prevent cross-type calculation crashes in complex physics formulas, Chisa forces you to be explicit about your extraction strategy:

- `unit.mag` (Magnitude - Best for Math & ML): Strips high-precision Decimals down to standard Python `float` (or leaves `ndarray` intact). Use this 95% of the time for safe, cross-dimensional physics calculations (e.g., Area * Length), Matplotlib charting, or machine learning pipelines.

- `unit.exact` (Absolute Precision - Best for Audits): Returns the raw, unadulterated `decimal.Decimal`. Use this strictly for financial tracking, database storage, or extreme precision logging. Warning: Multiplying a Decimal `.exact` with a standard Python float will intentionally trigger a TypeError to prevent precision drift.

---

## Quick Start

### 1. The Fluent API

A highly readable, chainable interface for straightforward conversions and aesthetic string formatting.

```python
from chisa import convert

# Simple scalar conversion
speed = convert(120, 'km/h').to('m/s').resolve()
print(speed) # 33.333333333333336

# Powerful cosmetic formatting for UI/Logs
text = convert(1000, 'm').to('cm').use(format='verbose', delim=True).resolve()
print(text) # "1,000 m = 100,000 cm"
```

### 2. High-Performance Vectorization
Pass NumPy arrays directly. Chisa safely bypasses string logic to maintain pure float64 matrix performance.
```python
import numpy as np
from chisa import convert

# Raw arrays from sensors or datasets
data = np.array([1, 10, 100, 1000])

# Fully vectorized mathematical conversion
res_array = convert(data, 'm').to('cm').use(format='raw').resolve()

print(repr(res_array))
# array([   100.,   1000.,  10000., 100000.])
```

### 3. Explicit OOP & Dimensional Mathematics
Treat units as first-class physical entities. Chisa automatically normalizes bases and prevents cross-dimensional logic errors.
```python
from chisa.units.length import Meter, Centimeter, Kilometer
from chisa.units.mass import Kilogram
from chisa import DimensionMismatchError

# 1. Seamless cross-unit math (Auto-normalization)
total_length = Meter(10.5) + Centimeter(500)
print(total_length) # <Meter: 15.5 m>

# 2. Precision Extraction (Method Chaining)
distance = Kilometer(2.5)

# .mag returns a standard Python float (Safe for external math & NumPy)
math_safe_val = distance.to(Meter).mag
print(repr(math_safe_val)) # 2500.0

# .exact returns a decimal.Decimal (For strict audits & extreme precision)
audit_safe_val = distance.to(Meter).exact
print(repr(audit_safe_val)) # Decimal('2500.0')

# 3. Dimensional Guardrails in action
try:
    invalid_math = Meter(10) + Kilogram(5)
except DimensionMismatchError as e:
    print(e) # "Dimension mismatch (Addition (+)). Expected 'length', but got 'mass'."
```


## Advanced Physics Modeling (Domain-Driven Design)
Chisa's true power lies in its explicit OOP API. Below is a three-part demonstration of modeling complex astrophysics using dynamic contexts, unit synthesis, and strict type guards.

### Part 1: Contextual Scaling (Gravitational Time Dilation)
Let's model how time slows down near a massive object using the Schwarzschild equation:

$$
\text{Scale Factor} =
\sqrt{
\max\left(
1 - \frac{2 G M}{r c^2}, 0
\right)
}
$$

```python
import numpy as np
from chisa import axiom, const, vmath
from chisa.units.time import TimeUnit, Second
from chisa.units.mass import Kilogram
from chisa.units.length import Meter

# 1. @prepare forces inputs into required Base Units safely before math execution
@axiom.prepare(mass=Kilogram, length=Meter)
def calc_time_dilation(mass=0.0, length=const.INF):
    r = vmath.maximum(length, 1.0)
    rs_term = (2 * const.GRAVITATIONAL_CONSTANT * mass) / (r * vmath.power(const.SPEED_OF_LIGHT, 2))
    safe_term = vmath.maximum(1.0 - rs_term, 0.0)
    return vmath.sqrt(safe_term)

# 2. @scale binds the physics formula to the unit's base multiplier
@axiom.scale(formula=calc_time_dilation)
class DilatedSecond(TimeUnit):
    symbol = "s_dil"
    base_multiplier = 1.0

# 3. Execution using Polymorphic Context Arrays
theoretical_time = DilatedSecond(
    10.0,
    context={
        "mass": Kilogram(1e25),
        "length": Meter(np.array([10_000_000.0, 5_000_000.0, 1_000_000.0])),
    },
)

print(theoretical_time.to(Second).mag)
# Output: [9.99999999  9.99999999  9.99999993]
```

### Part 2: Axiom Stacking & Derivation (Stellar Radiation)
We can derive complex units from simple ones (Watts = Joules / Seconds) and stack Axioms to calculate stellar flux based on the Stefan-Boltzmann law:

$$
\text{Flux} =
\left(\sigma T^4\right)\cos(\theta)
$$

```python
from chisa import axiom, const, vmath, C
from chisa.units.power import PowerUnit, Watt
from chisa.units.energy import Joule
from chisa.units.temperature import Celsius, Kelvin

@axiom.prepare(temperature=Kelvin)
def calc_stellar_emission(temperature=0.0, view_angle=0.0):
    flux = const.STEFAN_BOLTZMANN * vmath.power(temperature, 4)
    return flux * vmath.cos(view_angle)

# Axiom Stacking: Deriving W = J/s, applying a dynamic shift (noise), and scaling by physics!
@axiom.derive(mul=[Joule], div=[Second])
@axiom.shift(formula=C("power_noise", default=0.0))
@axiom.scale(formula=calc_stellar_emission)
class StellarRadiance(PowerUnit):
    symbol = "W_str"

# User passes Celsius; Chisa automatically normalizes it to Kelvin for the formula
emission = StellarRadiance(
    2.5,
    context={
        "temperature": Celsius(4726.85), # Equals exactly 5000 Kelvin
        "view_angle": 0.5, 
        "power_noise": Watt(1500.0), 
    },
)

print(emission.to(Watt).mag)
# Output: 77754964.21099459
```

### Part 3: Strict Function Guardrails (`@require`)
Never write manual `if type(x) != y` checks again. Let Chisa enforce dimensional integrity for your own domain logic.
```python
@axiom.require(duration=TimeUnit, radiation=PowerUnit)
def compute_total_energy(duration: TimeUnit, radiation: PowerUnit) -> Joule:
    # Safely extract .mag (floats/arrays) to perform cross-dimensional physics
    total_joules_raw = duration.to(Second).mag * radiation.to(Watt).mag
    return Joule(total_joules_raw)

# Calculate Energy = Array (Time) * Float (Power)
total_energy_array = compute_total_energy(theoretical_time, emission)

print(total_energy_array.mag)
# Output: [7.77549642e+08  7.77549641e+08  7.77549636e+08]
```

### Axiom Decorator Glossary
- `@axiom.derive(mul=[], div=[])`: Synthesizes the base multiplier of a unit by multiplying/dividing existing Chisa unit classes.
- `@axiom.bound(min_val, max_val)`: Enforces absolute physical limits (e.g., Temperature cannot fall below 0 Kelvin) during instantiation.
- `@axiom.scale(formula/ctx)`: Dynamically mutates the unit's multiplier based on runtime environmental context.
- `@axiom.shift(formula/ctx)`: Dynamically mutates the unit's offset base based on runtime environmental context.
- `@axiom.require(**kwargs)`: Function decorator that strictly guards argument inputs, ensuring they match specified dimensions or BaseUnit classes.
- `@axiom.prepare(**kwargs)`: Function decorator that pre-processes incoming Chisa objects, converting them to the required unit and extracting their math-safe .mag value automatically.

---

## Built-in Physics Utilities
To support the Axiom Engine and ensure safe cross-type mathematics (Scalars vs. NumPy Arrays), Chisa provides built-in utility modules optimized for scientific computing:

- `CtxProxy` **(aliased as `C`)**: A declarative Context Variable proxy. It allows you to build lazy-evaluated mathematical formulas directly inside decorators. For example, `C('power_noise') * 2` will wait until runtime to extract the `'power_noise'` value from the unit's context dictionary and multiply it.

- `chisa.vmath`: A universal math wrapper. Python's `math.sqrt` crashes on arrays, and `numpy.sqrt` can be overkill for pure scalars. `vmath` automatically detects the input type and routes the calculation to the safest, fastest engine (handling `maximum`, `power`, `cos`, `sqrt`, etc.) without you having to write a single if statement.

- `chisa.const`: A comprehensive, high-precision constants library (`SPEED_OF_LIGHT`, `GRAVITATIONAL_CONSTANT`, `STEFAN_BOLTZMANN`, `ABSOLUTE_ZERO_K`, `INF`, etc.). It eliminates "magic numbers" in your physics formulas.

---

## Root Helper Methods (Registry Introspection)
Chisa exposes lightweight utility functions directly at the root level. These helpers allow you to quickly interrogate the internal `UnitRegistry` without digging through the source code:

```python
import chisa
from chisa.units.temperature import Celsius

# 1. dimof(): Identify the dimension of a string alias, Class, or Instance!
print(chisa.dimof('celsius'))   # 'temperature'
print(chisa.dimof(Celsius))     # 'temperature'
print(chisa.dimof(Celsius(10))) # 'temperature'

# 2. dims(): List all physical dimensions currently loaded in the engine
print(chisa.dims()) 
# ['area', 'energy', 'length', 'mass', 'power', ...]

# 3. unitsin(): Discover all available unit symbols within a specific dimension
print(chisa.unitsin('mass')) 
# ['kg', 'g', 'lb', 'oz', 'MetricTon', ...]

# Pass `ascls=True` to retrieve the actual OOP Class objects for dynamic instantiation
mass_classes = chisa.unitsin('mass', ascls=True) 
# [<class 'Gram'>, <class 'Kilogram'>, ...]

# 4. baseof(): Identify the absolute computational baseline class for a dimension
print(chisa.baseof('temperature')) 
# <class 'chisa.units.temperature.Celsius'>
```

---

## Installation
**Install via pip:**
```bash
pip install chisa
```
**Requirements:**
- Python 3.8+
- numpy 
 
---

## Roadmap & TODOs

- **Enhanced Dimensional Synthesis:** Overhauling the `@axiom.derive` decorator to support native, highly readable mathematical syntax (e.g., `@axiom.derive(Joule / Second)` instead of passing lists).

- **Safe Cross-Dimensional OOP:** Unlocking the currently restricted `NotImplementedError` for cross-dimensional operations. This will allow natural OOP multiplication and division (e.g., `Meter(10) / Second(2) -> <SpeedUnit: 5.0 m/s>`) while strictly preserving dimensional integrity.

- **Global Context Manager:** (with `chisa.conf()`) Introduce a global state override to temporarily force data types (e.g., `dtype='float32'`) or ignore bounding rules across the entire computational environment.

- **Submodule Separation:** Refactoring the `@axiom` namespace into domain-specific submodules (e.g., `@axiom.unit...` for class definitions and `@axiom.formula...` for function injection) to enforce stricter separation of concerns.

---
---

##  Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make to Chisa are **greatly appreciated**.

If you have a suggestion that would make this framework better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". 
Don't forget to give the project a star!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See the `LICENSE` file for more information.

---

<p align="center">
  <i>"Measuring the universe, one dimension at a time."</i>
</p>