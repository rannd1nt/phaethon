<div align="center">
<h1> Advanced Physics & Dimensional Algebra in Chisa</h1>
</div>

While `chisa.Schema` is designed to protect data pipelines, the core of Chisa is a highly strict, Metaclass-driven Object-Oriented physics engine. This document explores the advanced scientific features available for modeling complex physical systems, custom dimensions, and contextual thermodynamics.

---

## 1. The Metaclass Architecture: Units as First-Class Types

In standard libraries, a unit is often just a string or a multiplier attached to a float. In Chisa, **every unit is a dynamically generated class**, and every dimension is strictly isolated.

When you synthesize units algebraically, Chisa's metaclass engine compiles a completely new class in memory at runtime.

```python
import chisa as cs
from chisa import u

# 1. Base Instantiation
mass = u.Kilogram(50)
acceleration = (u.Meter / (u.Second ** 2))(9.8)

# 2. Canonical Resolution
# Chisa recognizes that kg * m/s^2 is exactly a Newton (N)
force = mass * acceleration

print(type(force))      # <class 'chisa.units.force.Newton'>
print(cs.dimof(force))  # 'force'

# 3. Anonymous Unit (When no match is found in the registry)
# There is no named unit for "Kilogram-Meter" in our registry
anonymous = mass * u.Meter(2)
print(type(anonymous))  # <class 'chisa.core.base.Derived_Kilogram_mul_Meter'>
```

### Pure C-Level Array Execution
Because units are just classes wrapping numbers, you can pass multi-dimensional `numpy.ndarray` objects into them. Chisa completely bypasses string evaluation, performing dimensional algebra at native C-speeds with zero memory overhead.

---

## 2. Precision & Type Safety (`.mag` vs `.exact`)

By default, Chisa strictly standardizes all scalar calculations to C-level `float64` (native Python `float`). This prevents unexpected `TypeError` crashes when feeding Chisa outputs directly into Machine Learning libraries like SciPy or Scikit-Learn. 

However, Chisa can dynamically juggle standard `float`, ultra-precise `decimal.Decimal`, and vectorized `numpy.ndarray`. To handle this, Chisa forces explicit extraction strategies:

- `unit.mag` **(Magnitude - Best for Math & ML):** Safely extracts the native Python `float` (or leaves `ndarray` intact). Use this 95% of the time for cross-dimensional physics calculations, Matplotlib charting, or machine learning pipelines.
- `unit.exact` **(Absolute Precision - Best for Audits):** Returns the raw, unadulterated `decimal.Decimal`. Use this strictly for financial tracking, material accounting, or extreme precision logging. 

*Note: To use `.exact`, you must explicitly initialize your unit with a string or Decimal object.*

```python
from decimal import Decimal
from chisa import u

distance = u.Kilometer(Decimal('2.5'))

# .mag safely downcasts to a standard Python float
print(repr(distance.to(u.Meter).mag)) # 2500.0

# .exact preserves the high-precision decimal.Decimal
print(repr(distance.to(u.Meter).exact)) # Decimal('2500.0')
```

---

## 3. The Axiom Engine: Enforcing the Laws of Physics

Mathematical operations don't care about reality; physics does. Chisa uses the `@axiom` decorator suite to model absolute physical truths.

### `@axiom.bound`: Absolute Limits
Certain dimensions have hard limits. Absolute temperature cannot drop below $0 \text{ K}$, and mass cannot be negative. Chisa enforces this natively.

```python
import chisa as cs
from chisa import u

try:
    # Attempting to create a temperature below Absolute Zero (-273.15 C)
    impossible_temp = u.Celsius(-300)
except cs.AxiomViolationError as e:
    print(e) 
    # Output: "Temperature cannot drop below Absolute Zero (-273.15 °C)!"
```

### `@axiom.require`: Strict Function Guardrails
Data scientists often write complex functions that expect specific units (e.g., energy). Python's standard type hints cannot prevent a user from passing a velocity value instead. Chisa's `@axiom.require` intercepts the execution and validates the **dimensional integrity** of the inputs.

```python
from chisa import axiom, u

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

Chisa allows you to build entirely new units or adjust existing ones dynamically based on environmental context (like temperature, gravity, or atmospheric pressure) using built-in physics utilities.

### Physics Utilities Included:
- `C` **(CtxProxy)**: A declarative Context Variable proxy for lazy-evaluated formulas.
- `vmath`: A universal math wrapper that intelligently routes calculations (`sqrt`, `cos`, `power`) to `math` or `numpy` based on input type.
- `const`: High-precision constants library (`SPEED_OF_LIGHT`, `STANDARD_ATMOSPHERE_PA`, etc.).

### Example A: Contextual Shift (Gauge Pressure)
In industrial piping, Gauge Pressure (`psig`) is Absolute Pressure minus the local Atmospheric Pressure. We can use `@axiom.shift` and `C` to model this dynamically.

```python
from chisa import axiom, C, u

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
from chisa import axiom, C, u

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
- `@axiom.derive(UnitA / UnitB)`: Synthesizes the unit by performing direct metaclass algebra on existing Chisa classes.
- `@axiom.bound(min_val, max_val)`: Enforces absolute physical limits during instantiation.
- `@axiom.scale(formula/C)`: Dynamically mutates the unit's multiplier based on runtime environmental context.
- `@axiom.shift(formula/C)`: Dynamically mutates the unit's offset base based on runtime environmental context.
- `@axiom.require(**kwargs)`: Strictly guards argument inputs, ensuring they match specified dimensions.
- `@axiom.prepare(**kwargs)`: Pre-processes incoming Chisa objects, converting them to the required unit and extracting their math-safe `.mag` value automatically.

---

## 5. Chisa Supported Dimensions & Base Units
Below is a reference of all 14 physical dimensions currently loaded into the Chisa Engine, along with their strict computational base units.

* **Area** *(Base: `SquareMeter`)*: `['a', 'ac', 'cm²', 'ha', 'km²', 'mm²', 'm²', 'sq_ft', 'sq_in', 'sq_mi', 'sq_yd']`
* **Data** *(Base: `Byte`)*: `['B', 'GB', 'Gb', 'GiB', 'KB', 'Kb', 'KiB', 'MB', 'Mb', 'MiB', 'PB', 'PiB', 'TB', 'Tb', 'TiB', 'b', 'nibble']`
* **Density** *(Base: `KilogramPerCubicMeter`)*: `['g/cm³', 'kg/m³', 'lb/ft³', 'lb/gal']`
* **Energy** *(Base: `Joule`)*: `['BTU', 'GJ', 'GWh', 'J', 'MJ', 'MMBtu', 'MWh', 'Wh', 'cal', 'eV', 'ft-lbf', 'kJ', 'kWh', 'kcal']`
* **Force** *(Base: `Newton`)*: `['MN', 'N', 'dyn', 'gf', 'kN', 'kgf', 'kip', 'lbf', 'ozf', 'pdl', 'short_tonf', 'tf']`
* **Frequency** *(Base: `Hertz`)*: `['BPM', 'GHz', 'Hz', 'MHz', 'RPM', 'kHz']`
* **Length** *(Base: `Meter`)*: `['au', 'barleycorn', 'chain', 'cm', 'dm', 'fm', 'ft', 'furlong', 'hand', 'in', 'km', 'league', 'link', 'ly', 'm', 'mi', 'mil', 'mm', 'nm', 'nmi', 'pc', 'pica', 'pm', 'pt', 'rod', 'um', 'yd', 'Å']`
* **Mass** *(Base: `Kilogram`)*: `['M_cer', 'M_earth', 'M_jup', 'M_mars', 'M_mer', 'M_moon', 'M_nep', 'M_plu', 'M_sat', 'M_sun', 'M_ura', 'M_ven', 'amu', 'arroba-es', 'arroba-pt', 'bale-aus', 'bale-cotton', 'bale-uk', 'bale-wool', 'ct', 'dr', 'eV/c^2', 'g', 'gr', 'kg', 'lb', 'longton', 'm_p', 'mark-de', 'mark-no', 'mg', 'ons', 'oz', 'oz_t', 'q', 'shortton', 'slug', 'st', 't']`
* **Power** *(Base: `Watt`)*: `['BTU/h', 'GW', 'MW', 'PS', 'TR', 'W', 'hp', 'kW', 'mW']`
* **Pressure** *(Base: `Pascal`)*: `['Ba', 'GPa', 'MPa', 'Pa', 'TPa', 'Torr', 'at', 'atm', 'bar', 'barg', 'hPa', 'inH2O', 'inHg', 'kPa', 'kgf/m2', 'ksi', 'mPa', 'mbar', 'mmH2O', 'nPa', 'pPa', 'psi', 'psig', 'tf/m2', 'tsf', 'tsi', 'μPa']`
* **Speed** *(Base: `MeterPerSecond`)*: `['c', 'cm/min', 'cm/s', 'ft/min', 'ft/s', 'in/s', 'km/h', 'kt', 'm/min', 'm/s', 'mach', 'mm/min', 'mm/s', 'mph']`
* **Temperature** *(Base: `Celsius`)*: `['K', '°C', '°F', '°R', '°Re']`
* **Time** *(Base: `Second`)*: `['bimonth', 'century', 'd', 'decade', 'generation', 'h', 'lustrum', 'millennium', 'min', 'mo', 'ms', 'ns', 'quadmester', 'quarter', 's', 'score', 'semester', 'w', 'windu', 'y', 'μs']`
* **Volume** *(Base: `CubicMeter`)*: `['L', 'bbl', 'cL', 'cm³', 'cup', 'dL', 'daL', 'dm³', 'fl_oz', 'ft³', 'gal', 'hL', 'in³', 'km³', 'mL', 'mm³', 'm³', 'nL', 'pt', 'qt', 'tbsp', 'tsp', 'uk_gal', 'yd³', 'µL']`