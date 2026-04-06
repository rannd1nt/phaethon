---
seo_type: TechArticle
title: "Fluent API: Chainable Conversion"
description: "Typestate-enforced conversion pipeline for scientific computing. Chain methods securely to convert floats, physical tensors, or formatted string data."
keywords: "fluent API unit conversion, chainable dimensional pipeline python, string to physics tensor, high-performance unit conversion"
---

# The Fluent API

While instantiating massive `BaseUnit` tensors is perfect for rigorous scientific computing and dimensional tracking, sometimes you need a lightweight, lightning-fast method to convert numerical data inside a larger data engineering pipeline without carrying the entire physics payload.

Phaethon provides the `phaethon.convert` Fluent API—a typestate-enforced, chainable pipeline designed for high-performance data extraction, transformation, and formatting.

---

## The Conversion Pipeline

The Fluent API operates on a strict pipeline: **Initialize** `->` **Bind Target** `->` **Configure (Optional)** `->` **Resolve**.

```python
import phaethon
import phaethon.units as u

# 1. Initialize with a raw number and source unit
pipeline = phaethon.convert(10, 'kg')

# 2. The pipeline is 'Unbound' and cannot be executed yet
# pipeline.resolve() -> Raises ConversionError

# 3. Bind the target unit (now it's 'Bound' and executable)
pipeline.to('grams')

# 4. Resolve to get the final raw magnitude
result = pipeline.resolve()
print(result) # Output: 10000.0
```

You can chain these methods elegantly in a single line:

```python
import phaethon

result = phaethon.convert(10, 'm').to('cm').resolve()
print(result) # Output: 1000.0
```

---

## Modifying the Engine (`.use`)

By default, `.resolve()` returns a raw Python `float` (or a `numpy.ndarray` with `float64` dtype). You can drastically alter how the engine calculates and formats the result using the `.use()` method before resolving.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">out</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Determines the structure of the returned object:
    <ul>
      <li><code>'raw'</code> (Default): Returns a plain float or ndarray.</li>
      <li><code>'obj'</code>: Returns a fully instantiated <code>BaseUnit</code> tensor.</li>
      <li><code>'tag'</code>: Returns a formatted string with the unit symbol (e.g., <code>"10.0 kg"</code>).</li>
      <li><code>'verbose'</code>: Returns an equation string (e.g., <code>"10.0 m = 1000.0 cm"</code>).</li>
    </ul>
  </div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">dtype</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Forces NumPy to cast the underlying array to a specific C-type (e.g., <code>'float32'</code>, <code>'int32'</code>) to save memory.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">prec / sigfigs</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">Applies decimal places precision (<code>prec</code>) or strict significant figures (<code>sigfigs</code>) before returning the value.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">delim</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool | str</span>
  </div>
  <div class="p-desc">Adds thousands separators if outputting as a string.</div>
</div>

**Example Usage:**

```python
import phaethon
import numpy as np

# A raw sensor array
sensor_data = np.array([10.5, 20.7, 30.1], dtype=np.float64)

# Force the output to be memory-efficient float16
arr_f16 = phaethon.convert(sensor_data, 'kg').to('g').use(dtype='float16').resolve()
print(arr_f16.dtype) # Output: float16

# Return a highly formatted, verbose string
text = phaethon.convert(12000, 'm').to('km').use(out='verbose', delim=True, prec=2).resolve()
print(text) # Output: 12,000 m = 12.00 km
```

---

## Context Injection (`.context`)

Certain physical conversions require environmental context to resolve properly. For instance, converting a velocity skalar to Mach speed requires knowing the air temperature.

The `.context()` method dynamically injects these variables into the calculation pipeline. You can pass a dictionary of variables, or pass them as direct keyword arguments (`**kwargs`).

<div class="param-box">
  <div class="param-header">
    <span class="p-name">ctx</span>
    <span class="p-sep">—</span>
    <span class="p-type">dict | None</span>
  </div>
  <div class="p-desc">A dictionary of context variables.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">**kwargs</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Arbitrary keyword arguments representing physical conditions.</div>
</div>

**Example Usage:**

```python
import phaethon as ptn
import phaethon.units as u

# Converting 340 m/s to Mach number
# This conversion strictly requires 'temperature' to be defined in the context!
# Assuming the Mach axiom uses Celsius:
mach_speed = ptn.convert(340, u.MeterPerSecond) \
                .to(u.Mach) \
                .context(temperature=20.0) \
                .use(out='tag', prec=2) \
                .resolve()

print(mach_speed)
# Output: 0.99 Mach (Approximately, depending on axiom implementation)
```

---

## Semantic Time Formatting (`.flex`)

The Fluent API includes a specialized termination method called `.flex()` that acts as an alternative to `.resolve()`. It is exclusively available for time-based dimensions. It deconstructs total durations into human-readable strings.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">range</span>
    <span class="p-sep">—</span>
    <span class="p-type">tuple[str, str]</span>
  </div>
  <div class="p-desc">The (upper_bound, lower_bound) for the time breakdown (e.g., <code>('year', 'day')</code>).</div>
</div>

**Example Usage:**

```python
import phaethon

# Convert 1 Million seconds into a readable format
duration = phaethon.convert(1_000_000, 'seconds').flex()

print(duration)
# Output: 1 week 4 days 13 hours 46 minutes 40 seconds
```