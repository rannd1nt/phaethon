<div align="center">
<h1> Advanced Physics & Dimensional Algebra in Phaethon</h1>
</div>

While `phaethon.Schema` is designed to protect data pipelines, the core of Phaethon is a highly strict, Metaclass-driven Object-Oriented physics engine. This document explores the advanced scientific features available for modeling complex physical systems, custom dimensions, and contextual thermodynamics.

---

## 1. The Metaclass Architecture: Units as First-Class Types

In standard libraries, a unit is often just a string or a multiplier attached to a float. In Phaethon, **every unit is a dynamically generated class**, and every dimension is strictly isolated.

[Image of a software architecture diagram showing a metaclass physics engine deriving complex dimensions from base units]

When you synthesize units algebraically, Phaethon's metaclass engine compiles a completely new class in memory at runtime.

```python
import phaethon as ptn
from phaethon import u

# 1. Base Instantiation
mass = u.Kilogram(50)
acceleration = (u.Meter / (u.Second ** 2))(9.8)

# 2. Canonical Resolution
# Phaethon recognizes that kg * m/s^2 is exactly a Newton (N)
force = mass * acceleration

print(type(force))      # <class 'phaethon.units.force.Newton'>
print(ptn.dimof(force)) # 'force'

# 3. Anonymous Unit (When no match is found in the registry)
# There is no named unit for "Kilogram-Meter" in our registry
anonymous = mass * u.Meter(2)
print(type(anonymous))  # <class 'phaethon.core.base.Derived_Kilogram_mul_Meter'>
```

### Pure C-Level Array Execution
Because units are just classes wrapping numbers, you can pass multi-dimensional `numpy.ndarray` objects into them. Phaethon completely bypasses string evaluation, performing dimensional algebra at native C-speeds with zero memory overhead.

---

## 2. Precision & Type Safety (`.mag` vs `.exact`)

By default, Phaethon strictly standardizes all scalar calculations to C-level `float64` (native Python `float`). This prevents unexpected `TypeError` crashes when feeding Phaethon outputs directly into Machine Learning libraries like SciPy or Scikit-Learn. 

However, Phaethon can dynamically juggle standard `float`, ultra-precise `decimal.Decimal`, and vectorized `numpy.ndarray`. To handle this, Phaethon forces explicit extraction strategies:

- `unit.mag` **(Magnitude - Best for Math & ML):** Safely extracts the native Python `float` (or leaves `ndarray` intact). Use this 95% of the time for cross-dimensional physics calculations, Matplotlib charting, or machine learning pipelines.
- `unit.exact` **(Absolute Precision - Best for Audits):** Returns the raw, unadulterated `decimal.Decimal`. Use this strictly for financial tracking, material accounting, or extreme precision logging. 

*Note: To use `.exact`, you must explicitly initialize your unit with a string or Decimal object.*

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

## 3. The Axiom Engine: Enforcing the Laws of Physics

Mathematical operations don't care about reality; physics does. Phaethon uses the `@axiom` decorator suite to model absolute physical truths.

### `@axiom.bound`: Absolute Limits
Certain dimensions have hard limits. Absolute temperature cannot drop below 0 K, and mass cannot be negative. Phaethon enforces this natively.

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

### `@axiom.require`: Strict Function Guardrails
Data scientists often write complex functions that expect specific units (e.g., energy). Python's standard type hints cannot prevent a user from passing a velocity value instead. Phaethon's `@axiom.require` intercepts the execution and validates the **dimensional integrity** of the inputs.

```python
from phaethon import axiom, u

@axiom.require(mass=u.MassUnit, velocity=u.SpeedUnit)
def compute_kinetic_energy(mass, velocity):
    # E = 0.5 * m * v^2
    j_val = 0.5 * mass.to(u.Kilogram).mag * (velocity.to(u.MeterPerSecond).mag ** 2)
    return u.Joule(j_val)

# SAFE: Passing Mass and Speed
energy = compute_kinetic_energy(mass=u.Kilogram(1500), velocity=u.MeterPerSecond(20))

# EXPLOSION: Passing Volume instead of Mass
try:
    compute_kinetic_energy(mass=u.Liter(1500), velocity=u.MeterPerSecond(20))
except TypeError:
    # "Argument 'mass' expected exactly 'MassUnit', but got 'VolumeUnit'"
    pass
```

---

## 4. Domain-Driven Design: Stacking Axioms

Phaethon allows you to build entirely new units or adjust existing ones dynamically based on environmental context (like temperature, gravity, or atmospheric pressure) using built-in physics utilities.

### Physics Utilities Included:
- `C` **(CtxProxy)**: A declarative Context Variable proxy for lazy-evaluated formulas.
- `vmath`: A universal math wrapper that intelligently routes calculations (`sqrt`, `cos`, `power`) to `math` or `numpy` based on input type.
- `const`: High-precision constants library (`SPEED_OF_LIGHT`, `STANDARD_ATMOSPHERE_PA`, etc.).

### Example A: Contextual Shift (Gauge Pressure)
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

### Example B: Dynamic Scaling & Metaclass Derivation (Planetary G-Force)
We can derive complex units cleanly using Metaclass math (`u.Length / u.Time ** 2`) and scale them dynamically. Let's model a dynamic G-Force unit that scales based on the local gravity of different planets.

```python
from phaethon import axiom, C, u

# @derive supports direct Metaclass algebra!
@axiom.derive(u.Meter / (u.Second ** 2))
# @scale grabs the local gravity from the context at runtime
@axiom.scale(formula=C("local_gravity", default=9.80665))
class PlanetaryGForce(u.SpeedUnit):
    symbol = "g_planet"

# Experiencing 3 Gs on Mars (Gravity is much weaker)
mars_acceleration = PlanetaryGForce(
    3.0,
    context={"local_gravity": 3.721} # Mars gravity in m/s^2
)

# Experiencing 3 Gs on Earth
earth_acceleration = PlanetaryGForce(
    3.0,
    context={"local_gravity": 9.80665} 
)

print(f"Mars Acceleration: {mars_acceleration.to(u.MeterPerSecond).mag} m/s^2")
print(f"Earth Acceleration: {earth_acceleration.to(u.MeterPerSecond).mag} m/s^2")
```

### Axiom Decorator Glossary
- `@axiom.derive(UnitA / UnitB)`: Synthesizes the unit by performing direct metaclass algebra on existing Phaethon classes.
- `@axiom.bound(min_val, max_val)`: Enforces absolute physical limits during instantiation.
- `@axiom.scale(formula/C)`: Dynamically mutates the unit's multiplier based on runtime environmental context.
- `@axiom.shift(formula/C)`: Dynamically mutates the unit's offset base based on runtime environmental context.
- `@axiom.require(**kwargs)`: Strictly guards argument inputs, ensuring they match specified dimensions.
- `@axiom.prepare(**kwargs)`: Pre-processes incoming Phaethon objects, converting them to the required unit and extracting their math-safe `.mag` value automatically.

*(Skipped Section 5 for brevity, the base unit list remains identical).*