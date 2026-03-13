<div align="center">
<h1> Advanced Physics & Dimensional Algebra in Phaethon</h1>
</div>

While `phaethon.Schema` is designed to protect data pipelines, the core of Phaethon is a highly strict, Metaclass-driven Object-Oriented physics engine. This document explores the advanced scientific features available for modeling complex physical systems, custom dimensions, tensor algebra, and contextual thermodynamics.

---

## 1. The Metaclass Architecture: Units as First-Class Types

In standard libraries, a unit is often just a string or a multiplier attached to a float. In Phaethon, **every unit is a dynamically generated class**, and every dimension is strictly isolated. 

When you synthesize units algebraically, Phaethon's metaclass engine compiles a completely new class in memory at runtime.

```python
import phaethon as ptn
from phaethon import u

# 1. Syntactic Sugar for Cross-Entity Operations
# You can perform math directly between an Instance and a naked Class!
acceleration = u.Meter(9.8) / (u.Second(1) ** 2)

# 2. Canonical Resolution
mass = u.Kilogram(50)
force = mass * acceleration

print(type(force))      # <class 'phaethon.units.force.Newton'>
print(ptn.dimof(force)) # 'force'

# 3. Anonymous Unit (When no match is found in the registry)
anonymous = mass * u.Meter(2)
print(type(anonymous))  # <class 'phaethon.core.base.Derived_Kilogram_mul_Meter'>
```

### Dimensionless Collapse (The Void)
Operations that mathematically cancel out all dimensions do not arbitrarily decay into primitive Python floats. To preserve strict OOP API contracts, Phaethon intelligently collapses them into a dimensionless `BaseUnit` object.

```python
ratio = u.Meter(10) / u.Meter(2)
print(repr(ratio)) # <BaseUnit: 5.0 dimensionless>

# You can safely continue chaining API methods without TypeErrors
print(ratio.mag) # 5.0
```

### Class-Level Hierarchy Comparisons
Phaethon's Metaclasses natively support direct comparative operators (`<`, `>`, `<=`, `>=`). You can sort and validate unit hierarchies inherently without ever instantiating them.

```python
print(u.Gigabyte > u.Megabyte) # True
print(u.Kilogram < u.Gram)     # False
```

---

## 2. Advanced Tensor & Physics Operators

Because Phaethon units are proxy wrappers around raw numbers or matrices, the engine fully supports advanced Python and NumPy Dunder Methods (Double Underscores). This allows developers to express complex mathematical formulas natively.

### Vectorization & Properties (The NumPy Bridge)
Phaethon instances wrapping NumPy arrays natively support array slicing, multidimensional properties, and shape manipulation without losing their physical armor.

```python
import numpy as np
from phaethon import u

# Initialize a 3D velocity tensor (Time, Grid_X, Grid_Y)
raw_tensor = np.random.uniform(1, 10, (3, 2, 2))
velocity = u.MeterPerSecond(raw_tensor)

# Native NumPy properties are proxied automatically!
print(velocity.shape) # (3, 2, 2)
print(velocity.ndim)  # 3

# Slicing retains the unit wrapper
first_frame = velocity[0, :, :]
print(type(first_frame)) # <class 'phaethon.units.speed.MeterPerSecond'>

# Shape manipulations
flat_velocity = velocity.flatten()
transposed_vel = velocity.T 
```

### Matrix Multiplication / Dot Products (`@`)
Perfect for applying directional vectors, weight matrices, or executing dimensional synthesis across multi-dimensional arrays.

```python
# Unit @ Array = Unit
force_matrix = u.Newton(np.array([10, 20]))
direction_vector = np.array([[1, 0], [0, 1]])

result = force_matrix @ direction_vector 
# Output: [10, 20] Newtons

# Unit @ Unit = Synthesized Unit
distance_vector = u.Meter(np.array([5, 5]))
work_done = force_matrix @ distance_vector 
# Synthesizes into u.Joule!
```

### Modulo / Phase Resets (`%`)
Essential for calculating time loops, rotational physics (angles), or continuous signal phases.

```python
time_elapsed = u.Second(3650)
cycle_duration = u.Second(60)

# How many seconds into the current cycle?
current_phase = time_elapsed % cycle_duration
print(current_phase) # 50.0 s
```

### Floor Division for Discrete Quantization (`//`)
Useful when dealing with non-divisible physical goods (like counting exact pallets, shipping containers, or discrete operational cycles).

```python
total_mass = u.Kilogram(500)
crate_capacity = u.Kilogram(60)

full_crates = total_mass // crate_capacity
print(full_crates) # <BaseUnit: 8.0 dimensionless>
```

### Native Reductions
You can directly call vectorized statistical methods on the unit objects. They correctly return structurally instantiated physical tensors rather than naked `float64` arrays.

```python
vel = u.MeterPerSecond(np.random.uniform(0, 100, (5, 5)))

print(vel.max(axis=0))  # Max velocity per column (Retains Unit)
print(vel.mean())       # Average velocity of entire matrix (Retains Unit)
print(vel.sum())        # Total velocity
```

---

## 3. Precision & Type Safety (`.mag` vs `.exact`)

Phaethon dynamically juggles standard `float`, ultra-precise `decimal.Decimal`, and vectorized `numpy.ndarray`. To handle this safely, Phaethon forces explicit extraction strategies:

- `unit.mag` **(Magnitude - Best for Math & ML):** Safely extracts the native Python `float` (or leaves `ndarray` intact). Use this for cross-dimensional physics calculations, Matplotlib charting, or ML pipelines.
- `unit.exact` **(Absolute Precision - Best for Audits):** Returns the raw, unadulterated `decimal.Decimal`. Use this strictly for financial tracking or extreme precision logging. 

```python
from decimal import Decimal
from phaethon import u

distance = u.Kilometer(Decimal('2.5'))

# .mag safely downcasts to a standard Python float
print(repr(distance.to(u.Meter).mag)) # 2500.0

# .exact preserves the high-precision decimal.Decimal
print(repr(distance.to(u.Meter).exact)) # Decimal('2500.0')
```

---

## 4. The Axiom Engine: Enforcing the Laws of Physics

Mathematical operations don't care about reality; physics does. Phaethon uses the `@axiom` decorator suite to model absolute physical truths.

### `@axiom.bound`: Absolute Limits
Certain dimensions have hard limits. Absolute temperature cannot drop below 0 K, and mass cannot be negative. Phaethon enforces this natively across scalar and tensor arrays.

```python
import phaethon as ptn
from phaethon import u

try:
    # Attempting to create a temperature below Absolute Zero (-273.15 C)
    impossible_temp = u.Celsius(-300)
except ptn.AxiomViolationError as e:
    print(e) 
    # Output: "Temperature cannot drop below Absolute Zero (-273.15 °C)!"
```

### "God Mode" (`ignore_axiom_bound=True`)
For theoretical physics, Sci-Fi simulations, or extreme data imputation, you can completely bypass all intrinsic physical laws across the engine using the global or block context config:

```python
with ptn.using(ignore_axiom_bound=True):
    theoretical_temp = u.Kelvin(-500)
    print(f"Bypassed Physics: {theoretical_temp}")
```

### `@axiom.require`: Strict Function Guardrails
Data scientists often write complex functions that expect specific units. Phaethon's `@axiom.require` intercepts execution and validates the **dimensional integrity** of the inputs.

```python
from phaethon import axiom, u

@axiom.require(mass=u.MassUnit, velocity=u.SpeedUnit)
def compute_kinetic_energy(mass, velocity):
    j_val = 0.5 * mass.to(u.Kilogram).mag * (velocity.to(u.MeterPerSecond).mag ** 2)
    return u.Joule(j_val)

# EXPLOSION: Passing Volume instead of Mass
try:
    compute_kinetic_energy(mass=u.Liter(1500), velocity=u.MeterPerSecond(20))
except TypeError:
    # "Argument 'mass' expected exactly 'MassUnit', but got 'VolumeUnit'"
    pass
```

---

## 5. Domain-Driven Design: Dynamic Context Inheritance

Phaethon allows you to build entirely new units or adjust existing ones dynamically based on environmental context (like temperature, gravity, or real-time exchange rates).

### Physics Utilities Included:
- `C` **(CtxProxy)**: A declarative Context Variable proxy for lazy-evaluated formulas.
- `vmath`: A universal math wrapper shadowing `builtins` (e.g., `abs`, `max`, `round`).
- `const`: High-precision constants library (`SPEED_OF_LIGHT`, `STANDARD_ATMOSPHERE_PA`, etc.).

### Example A: Dynamic Context Inheritance (Derived Financial Units)
When you divide two units (e.g., `Currency / Mass`), the newly synthesized metaclass dynamically inherits the ability to evaluate base multipliers at runtime. This guarantees that complex econo-physics units instantly react to real-time context injections.

```python
from phaethon import u
import phaethon as ptn

# Synthesize a completely new Econo-physics dimension dynamically
PricePerWeight = u.Euro / u.Gram

# We have 50 EUR/gram. We inject real-time FX rates via the OOP `.to()` method.
asset_price = PricePerWeight(50).to(
    u.IndonesianRupiah / u.Kilogram, 
    context={'eur_to_usd': 1.10, 'usd_to_idr': 16000.0}
)

print(asset_price.format(delim=True)) 
# Output: "880,000,000 IDR/kg"
```

### Example B: Contextual Shift (Gauge Pressure)
In industrial piping, Gauge Pressure (`psig`) is Absolute Pressure minus the local Atmospheric Pressure. We can use `@axiom.shift` and `C` to model this dynamically.

```python
from phaethon import axiom, C, u

# We shift the base value by adding the dynamic atmospheric pressure
@axiom.shift(formula=C("atm_pressure", default=101325.0))
class CustomGaugePressure(u.PressureUnit):
    symbol = "psig_custom"
    base_multiplier = 6894.76 # PSI to Pascal

# Sensor reads 50 PSIG in a high-altitude facility (lower atm pressure)
sensor_reading = CustomGaugePressure(
    50.0, 
    context={"atm_pressure": u.Pascal(90000.0)}
)

print(sensor_reading.to(u.Pascal).mag)
```

### Axiom Decorator Glossary
- `@axiom.derive(UnitA / UnitB)`: Synthesizes the unit by performing direct metaclass algebra.
- `@axiom.bound(min_val, max_val)`: Enforces absolute physical limits during instantiation.
- `@axiom.scale(formula/C)`: Dynamically mutates the unit's multiplier based on context.
- `@axiom.shift(formula/C)`: Dynamically mutates the unit's offset base based on context.
- `@axiom.require(**kwargs)`: Strictly guards argument inputs ensuring dimensional matches.
- `@axiom.prepare(**kwargs)`: Pre-processes objects, converting them to the required unit and extracting their `.mag` value automatically.