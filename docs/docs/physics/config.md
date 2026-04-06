---
seo_type: TechArticle
title: "Config & Axiom Guardrails"
description: "Control Phaethon's scientific configuration. Manage absolute zero-tolerance physics guardrails, floating-point tolerances, and environmental context."
keywords: "physics floating-point tolerance, dimensional strictness python, environmental context injection physics, handle missing sensor data python"
---

# Configuration & Guardrails

Phaethon operates across two distinct worlds: the **Hybrid Data Schema** (parsing and cleaning tabular data) and the **Physics Engine** (tensor mathematics and dimensional algebra). 

The `phaethon.config` and `phaethon.using` interfaces act as the unified Control Center for both worlds. They determine how strictly physical laws are enforced, how floating-point anomalies are handled, and how volatile environmental states are injected into calculations.

---

## State Management

Phaethon provides two ways to apply configurations: globally or locally.

### Global Configuration
Use `phaethon.config()` to set the behavior for the entire Python runtime. This is typically done once at the entry point of your application.

```python
import phaethon as ptn

# Set global physics strictness and tolerance
ptn.config(axiom_strictness_level="strict_warn", atol=1e-10)
```

### Contextual Overrides
Use the `phaethon.using()` context manager to temporarily override settings for a specific block of code. This is thread-safe and perfect for handling isolated, dirty data without affecting the rest of the application.

```python
import phaethon as ptn
import phaethon.units as u

# Temporarily ignore the laws of physics for this calculation
with ptn.using(axiom_strictness_level="ignore"):
    impossible_temp = u.Kelvin(-500)
```

---

## Axiom Strictness Levels

Physical units in Phaethon are often protected by `@axiom.bound` (e.g., Temperature cannot drop below 0 Kelvin; Particle Cross-Section Area cannot be negative). The `axiom_strictness_level` determines how aggressively Phaethon polices these boundaries. 

Adjusting this level is highly recommended when dealing with stochastic tensor generation (`phaethon.random`). Since statistical variance (like Gaussian noise) can naturally generate values that temporarily dip outside absolute physical boundaries, adjusting the strictness level prevents unexpected `AxiomViolationError` crashes.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">default</span>
  </div>
  <div class="p-desc"><strong>Standard Safety.</strong> Hard-blocks raw invalid instantiations (e.g., <code>Kelvin(-10)</code> throws an error), but silently allows intermediate physics violations during mathematical operations (e.g., <code>Kelvin(5) - Kelvin(10)</code>) to prevent blocking valid multi-step formulas.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">strict_warn</span>
  </div>
  <div class="p-desc"><strong>The Vigilant Observer.</strong> Hard-blocks raw invalid instantiations, and prints a <code>UserWarning</code> to the console if a mathematical operation temporarily violates physics.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">strict</span>
  </div>
  <div class="p-desc"><strong>The Physics Police.</strong> Absolute zero tolerance. Hard-blocks both raw instantiations and mathematical operations that violate physical boundaries. Even temporary intermediate violations will halt execution.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">loose_warn</span>
  </div>
  <div class="p-desc"><strong>Soft Guardrails.</strong> Allows raw invalid instantiations but prints a warning. Mathematical operations are completely silent.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">ignore</span>
  </div>
  <div class="p-desc"><strong>The Wild West.</strong> Complete freedom. All physical boundary checks are bypassed. Triggers an early return in the validation engine, skipping heavy NumPy masking and clipping operations (<code>np.where</code>, <code>np.clip</code>). Ideal for running large stochastic arrays (<code>ptn.random.normal</code>) where temporary physical boundary violations are statistically expected.</div>
</div>

---

## Error Handling Policies

When an axiom strictness level determines that a violation *must* be enforced, the `default_on_error` parameter dictates exactly *how* Phaethon neutralizes the threat.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">raise</span>
    <span class="p-sep">—</span>
    <span class="p-type">(Default)</span>
  </div>
  <div class="p-desc">Halts execution immediately and throws an <code>AxiomViolationError</code>.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">coerce</span>
  </div>
  <div class="p-desc">Silently neutralizes the invalid data. In the Physics Engine, the magnitude of the <code>BaseUnit</code> is converted to <code>float('nan')</code> or <code>numpy.nan</code>. Extremely useful for streaming messy IoT sensor data without crashing the pipeline.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">clip</span>
  </div>
  <div class="p-desc">Forces the value to stay within the specified <code>min_val</code> or <code>max_val</code> defined by the unit's axiom.</div>
</div>

**Example Usage:**

Even outside of a DataFrame schema, Phaethon's C-Engine intercepts invalid arrays and coerces them at the tensor level.

```python
import phaethon as ptn
import phaethon.units as u

# We use 'coerce' to survive impossible physics
with ptn.using(default_on_error="coerce"):
    # Trying to instantiate Kelvins below Absolute Zero
    temps = u.Kelvin([300.0, -15.0, 250.0])
    
    print(temps.mag)
    # Output: [300.  nan 250.] (The -15.0 is safely neutralized to NaN)
```

---

## Floating-Point Tolerances

Because dimensional algebra often involves irrational numbers, constants (e, pi), and complex logarithmic synthesis, direct equality (==) in floating-point physics is dangerous. Phaethon uses built-in tolerances for all equality and comparative operations (<, <=, >, >=).

<div class="param-box">
  <div class="param-header">
    <span class="p-name">atol</span>
  </div>
  <div class="p-desc"><strong>Absolute Tolerance</strong> (Default: <code>1e-12</code>). Used to determine equality for values extremely close to zero.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">rtol</span>
  </div>
  <div class="p-desc"><strong>Relative Tolerance</strong> (Default: <code>1e-9</code>). Used to determine equality for very large or complex floating points.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

a = u.Joule(1.000000000000001)
b = u.Joule(1.0)

# Phaethon evaluates them as equal based on the default tolerances
print(a == b) # Output: True

# Tightening the tolerance globally
with ptn.using(atol=1e-16, rtol=1e-16):
    print(a == b) # Output: False
```

---

## Environmental Context

Physics is rarely static. The value of a currency fluctuates, and the boiling point of water changes with atmospheric pressure. Phaethon allows you to inject dynamic environmental variables at runtime using the `context` dictionary.

These variables are intercepted by units decorated with `@axiom.scale` or `@axiom.shift`.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">context</span>
    <span class="p-sep">—</span>
    <span class="p-type">dict[str, Any]</span>
  </div>
  <div class="p-desc">A flat dictionary for injecting dynamic environmental variables at runtime.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

# Assuming USDollar is scaled against a "usd_to_idr" context
with ptn.using(context={"usd_to_idr": 15500}):
    budget = u.USDollar(10)
    
    # The algebraic engine intercepts the context variable
    in_rupiah = budget.to(u.IndonesianRupiah)
    print(in_rupiah)
    # Output: 155000.0 IDR
```

---

## Formatting Shims

These parameters are exclusively used by Phaethon's backend Rust engine to parse raw, dirty strings into valid numerics. They **do not** affect how physical tensors are rendered as text (`__str__`) in the Physics Engine. Instead, they are critically important when ingesting messy tabular datasets via the [Hybrid Data Schema](../data/schema.md), allowing Phaethon to correctly interpret European versus American number formats during data extraction and cleaning.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">decimal_mark</span>
  </div>
  <div class="p-desc">The character used to denote the decimal place (e.g., <code>"."</code> or <code>","</code>) when parsing string data.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">thousands_sep</span>
  </div>
  <div class="p-desc">The character used to separate thousands (e.g., <code>","</code> or <code>"."</code>) when parsing string data.</div>
</div>