---
seo_type: TechArticle
title: "Dimensional Algebra: The Smart Engine"
description: "The smartest dimensional algebra engine for Python. Outperforms legacy unit libraries with dynamic synthesis, Isomorphic Firewalls, and logarithmic math."
keywords: "python dimensional analysis, smart unit conversion python, dimensional synthesis, isomorphic firewalls physics, python logarithmic units, advanced python units"
---

# Dimensional Algebra

The `phaethon.units` module is not a standard unit conversion utility; it is a strict, metaclass-driven algebraic physics engine. 

By defining physical dimensions as executable objects, Phaethon dynamically tracks mathematical signatures across complex algebraic expression chains. It inherently understands the laws of physics, preventing impossible mathematical operations before they contaminate data pipelines, numerical simulations, or machine learning models.

---

## Dynamic Synthesis

At runtime, Phaethon evaluates mathematical operations (`*`, `/`, `**`) between units by combining their dimensional signatures. If an operation yields a recognized physical dimension, Phaethon seamlessly casts the result into the appropriate canonical `BaseUnit`.

If an operation results in an unregistered physical dimension, Phaethon does not throw an error. Instead, it dynamically synthesizes an anonymous class to preserve the exact physical DNA of the intermediate calculation.

```python
import phaethon.units as u

# Standard Synthesis: Mass * Acceleration = Force
mass = u.Kilogram(1500)
acceleration = u.MeterPerSecondSquared(9.8)

force = mass * acceleration
print(repr(force))
# Output: <Newton: 14700.0 N>
print(force.dimension)
# Output: force

# Complex Synthesis: Maxwell's Speed of Light (c = 1 / sqrt(ε₀ * μ₀))
Epsilon0 = 8.854e-12 * (u.Ampere**2 * u.Second**4) / (u.Kilogram * u.Meter**3)
Mu0 = 1.256e-6 * (u.Kilogram * u.Meter) / (u.Second**2 * u.Ampere**2)

c_calc = (Epsilon0 * Mu0)**(-0.5)
speed_of_light = c_calc(1)

print(speed_of_light.to(u.MeterPerSecond))
# Output: 2.9987E+08 m/s
```

---

## Dimensional Collapse

When an algebraic operation results in perfectly balanced physical ratios, Phaethon automatically resolves the internal structure, triggering a **Dimensional Collapse** down to a pure scalar `Dimensionless` object.

```python
# (Kilometer / Meter) * (Hour / Minute) -> (Length/Length) * (Time/Time)
distance_ratio = u.Kilometer(1) / u.Meter(250)
time_ratio = u.Hour(2) / u.Minute(30)

result = distance_ratio * time_ratio

print(result.dimension)
# Output: dimensionless
print(result.mag)
# Output: 16.0
```

## Unary & Matrix Algebra

Phaethon expands standard scalar arithmetic to support complex matrix operations and Python unary operators.

### Matrix Multiplication (`@`)
If your physical tensors contain multi-dimensional arrays, Phaethon natively intercepts Python's matrix multiplication operator (`@` / `__matmul__`) and routes it to the highly optimized `np.matmul` C-backend. Just like scalar multiplication, it automatically triggers dimensional synthesis.

```python
import phaethon as ptn

# A 2x2 Matrix of Mass
mass_matrix = ptn.array([[2, 0], [0, 2]], unit='kg')

# A 2x1 Vector of Acceleration
accel_vector = ptn.array([[10], [5]], unit='m/s^2')

# Matrix Multiplication
force_matrix = mass_matrix @ accel_vector

print(force_matrix.shape)
# Output: (2, 1)

print(force_matrix.dimension)
# Output: force
```

### Unary Operators (`-`, `+`, `abs`, `round`)
Standard Python unary operators are natively supported and preserve the physical dimension.

```python
temp = u.Celsius(25.5)

print(-temp)      # Output: -25.5 °C
print(abs(-temp)) # Output: 25.5 °C
print(round(temp)) # Output: 26.0 °C
```

---

## Isomorphic Firewalls (Phantom Units)

In the standard International System of Units (SI), concepts like repeating cycles, radioactive decays, radiation counts, and discrete particles are often considered "dimensionless" (mathematically equal to `1`).

Phaethon actively rejects this ambiguity. It tracks these entities as **Phantom Units**. While they do not alter the base SI multiplier, they act as strict semantic signatures to prevent isomorphic dimensions (dimensions with the exact same SI backbone) from colliding or interacting illegally.

For example, Frequency (`Hertz`) and Radioactivity (`Becquerel`) both share the exact same SI signature: `Time⁻¹` (`1/s`). Phaethon erects an **Isomorphic Firewall** to prevent them from merging.

### The Phantom Registry

Phaethon internally tracks and orchestrates the following phantom particles to create distinct dimensional branches from shared SI baselines:

| Phantom Unit | Base Unit | Synthesized Dimension | Pure SI DNA |
| :--- | :--- | :--- | :--- |
| **Cycle** | `Hertz` | Frequency | `1 / Time` |
| **Decay** | `Becquerel` | Radioactivity | `1 / Time` |
| **SymbolData** | `Baud` | Baud Rate | `1 / Time` |
| **Expansion** | `ExpansionPerSecond` | Cosmology Expansion Rate | `1 / Time` |
| **Radiation** | `Gray` | Absorbed Dose | `Energy / Mass` |
| **BiologicalEffect** | `Sievert` | Equivalent Dose | `Energy / Mass` |
| **Photon** | `JoulePerPhoton` | Quantum Photon Energy | `Energy` |
| **Count** | `ParticlesPerCubicMeter`| Number Density | `1 / Volume` |
| **EnergyContent** | `JoulePerCubicMeter` | Energy Density | `Energy / Volume` |
| **Angle** | `Radian` | Angular Dimensions | Torque & Angular Momentum |
| **Solid Angle** | `Steradian` | Photometric Dimensions | Luminous flux & Illuminance |

**The Firewall in Action:**

```python
import phaethon.units as u

frequency = u.Hertz(50)          # Cycle / s
radioactivity = u.Becquerel(50)  # Decay / s

# Phaethon detects the Phantom Collision and blocks the addition
total = frequency + radioactivity
# SemanticMismatchError: Phantom Collision! Cannot add 'frequency' and 'radioactivity' despite sharing identical SI DNA.
```

**Dimensional Branching**
```python
import phaethon.units as u

rate = 1 / u.Second(30)
print(rate) # 0.0333 / s (rate of 30 per second) [SI unit: 1/s]

freq = u.Cycle(1) / u.Second(30)
print(freq) # 0.0333 Hz (frequency: cycle rate of 30 per second)

becquerel = u.Decay(1) / u.Second(30)
print(becquerel) # 0.0333 Bq (becquerel: decay rate of 30 per second)
```

---

## Exclusive Domain Locks

While Phantom Units protect parallel branches, highly specialized scientific domains often require an absolute quarantine. Phaethon implements **Exclusive Domain Locks** to prevent careless casting or interaction between boundaries that share mathematical foundations but imply drastically different physical behaviors.

You cannot directly cast an entity into an Exclusive Domain; you must explicitly synthesize it via multiplication or division with the correct Phantom Unit or spatial parameter (like Radians).

### The Heavily Guarded Domains

Phaethon places absolute domain locks on the following physical properties:

* **Absorbed Dose (`Gray`) & Equivalent Dose (`Sievert`)**: Guarded against raw Specific Energy (`Joule/kg`). You must synthesize them using the `Radiation` or `BiologicalEffect` phantom factors.
* **Torque (`NewtonMeter`)**: Guarded against Macroscopic Energy (`Joule`). Even though both are mathematically `Newton * Meter`, Torque requires spatial `Radian` division.
* **Action (`JouleSecond`) & Angular Momentum (`JouleSecondPerRadian`)**: Planck's constant (Action) and Angular Momentum share the same core `M·L²·T⁻¹` SI signature, but Angular momentum requires an angular relation. Phaethon isolates them completely.
* **Stiffness (`NewtonPerMeter`) & Surface Tension (`NewtonPerMeterSurface`)**: Kept separate to prevent mixing material elasticity (springs) with fluid surface boundary forces.
* **Energy Density (`JoulePerCubicMeter`)**: Guarded against Mechanical Pressure (`Pascal`). Both are `Newton/Meter²`, but squeezing a fluid is fundamentally different from storing energy in a battery cell.
* **Expansion Rate (`HubbleConstant`)**: Guarded against generic `Rate` or `Frequency`. Cosmic expansion operates on spatial scales (`km/s/Mpc`), completely isolated from temporal cycles.

**The Domain Lock in Action:**

```python
import phaethon.units as u

specific_energy = u.Joule(100) / u.Kilogram(1)

# Direct casting is strictly forbidden by the Domain Lock
specific_energy.to(u.Sievert)
# SemanticMismatchError: Exclusive Domain Locked: Cannot cast 'JoulePerKilogram' directly to 'Sievert'.

# To enter the domain, explicit algebraic synthesis via Phantom Units is required
equivalent_dose = specific_energy * u.BiologicalEffect(20)

print(equivalent_dose.dimension)
# Output: equivalent_dose
print(repr(equivalent_dose))
# Output: <Sievert: 2000.0 Sv>
```

---

## Non-Linear & Logarithmic Algebra

Phaethon natively supports non-linear unit scales, such as Decibels (`dB`), `dBm`, Stellar Magnitudes, and chemical `pH`. The engine intercepts standard mathematical operators, automatically drops the inputs to their linear counterparts (e.g., Watts, Moles), computes the physical result, and repacks it into the logarithmic scale in real-time.

### Implicit Linearization

When you add or subtract logarithmic units, Phaethon completely bypasses standard scalar arithmetic. It computes the actual physical energy/magnitude under the hood.

```python
import phaethon.units as u

# 30 dBm (1 Watt) + 30 dBm (1 Watt) = 2 Watts (Linear) -> ~33.01 dBm (Log)
signal_1 = u.DecibelMilliwatt(30.0)
signal_2 = u.DecibelMilliwatt(30.0)

# The engine handles the linear conversion implicitly
total_signal = signal_1 + signal_2

print(total_signal)
# Output: 33.0103 dBm
```

### The Zero-Linear Dilemma (Log 0)

A fundamental rule of logarithms is that log(0) is mathematically impossible (evaluating to negative infinity). If a subtraction operation results in a total cancellation of linear energy (e.g., 1 W - 1 W = 0 W), Phaethon's default strictness will halt execution to prevent a Python `ValueError`.

You can safely bypass this by utilizing the `phaethon.using` context manager to dictate how the engine should handle the infinite void.

```python
import phaethon as ptn

# Subtracting identical signals yields 0 Watts linear
# default_on_error='raise' -> AxiomViolationError

# Clip forces the math to the IEEE 754 standard for log(0)
with ptn.using(default_on_error='clip'):
    subtracted_clip = signal_1 - signal_2
    print(subtracted_clip) 
    # Output: -inf dBm

# Coerce neutralizes the impossible physics into a NaN for data pipelines
with ptn.using(default_on_error='coerce'):
    subtracted_nan = signal_1 - signal_2
    print(subtracted_nan) 
    # Output: nan dBm
```

### Dimensional Synthesis on Logs

While addition and subtraction preserve the logarithmic shell, **Multiplication and Division** trigger a phenomenon called *Dimensional Synthesis*. 

Multiplying two logarithmic units (e.g., dBm * dBm) is physically nonsensical as a log value. Therefore, Phaethon automatically strips the logarithmic envelope, calculates the cross-product of their linear bases, and creates an entirely new synthetic dimension.

```python
# Multiplying 30 dBm (1W) by 30 dBm (1W) creates Squared Watts!
multiplied = signal_1 * signal_2
print(multiplied) 
# Output: 1.0 W*W

# Viewing the absolute SI DNA of the new dimension
print(multiplied.decompose()) 
# Output: 1.0 kg²·m⁴/s⁶

# Division results in a clean, dimensionless ratio (1W / 1W = 1)
divided = signal_1 / signal_2
print(divided.dimension) 
# Output: 'dimensionless'
```

### Cross-Domain Math & Base Extraction

Phaethon allows you to mix different logarithmic references seamlessly. If you ever need to forcefully extract the pure linear value from a logarithmic tensor, use the `.si` property.

```python
# Mixing dBm and dBW safely
reduced_signal = total_signal - u.DecibelWatt(0.02)
print(reduced_signal) 
# Output: 29.9799 dBm

# Extracting the raw linear base unit (2 Watts)
print(total_signal.si) 
# Output: 2.0 W

# Explicitly casting the linear base to another unit
print(total_signal.si.to(u.Megawatt)) 
# Output: 2.0E-06 MW
```

**Chemical Applications:**
This logic applies universally to all logarithmic domains, including Chemistry.

```python
acid = u.pH(20)

# The linear base of pH is Concentration (Moles per Cubic Meter)
print(acid.si) 
# Output: 1.0000E-17 mol/m³

# Casting to standard laboratory units
print(acid.to(u.Molar)) 
# Output: 1.0000E-20 M
```

### Mathematical Guardrails

Phaethon mathematically disables illegal operations on non-linear units. Attempting to exponentiate (`**`), apply floor division (`//`), or modulo (`%`) to a logarithmic unit will trigger an immediate defense mechanism.

```python
import phaethon.units as u

sound = u.Decibel(60)

# You cannot mathematically exponentiate a logarithmic scale
sound_squared = sound ** 2
# AxiomViolationError: You cannot exponentiate, floor divide, or modulo a logarithmic unit (Decibel).
```

---

## Class vs. Instance Algebra (Avoiding Errors)

To master Phaethon's physics engine, you must understand the strict distinction between a **Unit Class** (the dimensional blueprint, handled by Phaethon's Metaclass) and a **Unit Instance** (the actual physical tensor containing data). 

Mixing them incorrectly will trigger specific, highly intentional errors. Here is the operational matrix:

### Instance + Scalar (Illegal)
You cannot add a dimensionless naked number to a physical tensor.

```python
import phaethon.units as u

distance = u.Meter(10.0)

# ILLEGAL: What does "+ 5" mean? 5 Meters? 5 Seconds? 
result = distance + 5
# TypeError: Cannot add a dimensionless scalar/array to a dimensioned unit 'Meter'.
```

### Class * Class (Metaclass Synthesis vs Instance Math)
AI Models and developers often confuse *Unit Classes* with *Data Instances*. 
Multiplying two blueprints (`u.Meter / u.Second`) is intercepted by Phaethon's `_PhaethonUnitMeta` Metaclass to synthesize a **new Class blueprint**, NOT data. There are no numbers being calculated here. 

However, if you multiply instantiated data (`u.Meter(10) / u.Second(2)`), the underlying NumPy C-API takes over to calculate the values (`5.0`), and automatically wraps the result in the synthesized class.

```python
import phaethon.units as u

# Yields a Class object (type[BaseUnit]) representing Speed
SpeedClass = u.Meter / u.Second

# You must instantiate it to use it
velocity = SpeedClass(50.0)
```

### Class * Scalar (Metaclass Scaling)
Multiplying a blueprint by a scalar creates a **new derived blueprint** with a scaled `base_multiplier`.

```python
import phaethon.units as u

# Synthesizes a new class representing "1000 Meters"
KiloMeterClass = u.Meter * 1000 
```

### Instance + Class (Auto-Instantiation)
If you perform an operation between a physical tensor and a naked Unit Class, Phaethon brilliantly assumes you mean exactly **1.0** of that class.

```python
import phaethon.units as u

distance = u.Meter(5.0)

# u.Centimeter is automatically instantiated as u.Centimeter(1.0)
new_distance = distance + u.Centimeter
print(new_distance)
# Output: 5.01 m
```

### Class + Class (Illegal)
You cannot "add" two conceptual blueprints together. Addition requires physical magnitude.

```python
import phaethon.units as u

# ILLEGAL: Metaclasses do not support addition.
TotalClass = u.Meter + u.Meter
# TypeError: unsupported operand type(s) for +: '_PhaethonUnitMeta' and '_PhaethonUnitMeta'
```

### Comparison Algebra (`==`, `<`, `>`)

Phaethon inherently understands that physical properties can be measured in different units. When you use comparison operators, Phaethon completely ignores the visual representation and mathematically compares their **absolute SI base values**.

Because of floating-point inaccuracies during complex dimensional conversions, Phaethon uses its global `rtol` (relative) and `atol` (absolute) configurations to determine equality.

```python
import phaethon.units as u

# 1 Kilometer is exactly equal to 1000 Meters
distance_a = u.Kilometer(1)
distance_b = u.Meter(1000)

print(distance_a == distance_b)
# Output: True

# Phaethon correctly compares magnitudes across domains
print(u.Hour(1) > u.Minute(50))
# Output: True
```

**The Dimension Guardrail:**
You cannot compare units from different physical dimensions. Doing so will instantly trigger a `DimensionMismatchError`.

```python
print(u.Kilogram(1) > u.Meter(1))
# DimensionMismatchError: Dimension mismatch (Greater-than (>)). Expected 'mass', but got 'length'.
```