---
seo_type: TechArticle
title: "Tabular Schema: Data Pipelines"
description: "Physics-constrained data normalization. Declarative pipelines using Rust string parsing, vectorized bounds clipping, and feature synthesis for Sci-ML."
keywords: "physics-constrained data normalization, parse physical units pandas, rust string parser python, impute missing sensor data, dimensional feature engineering"
---

# Hybrid Tabular Schema

The real world does not produce clean data. Sensors fail, human operators mix units (e.g., entering `"10 kg"` and `"22 lbs"` in the same column), formatting varies by region, and anomalies spike. 

Phaethon's `Schema` module is a declarative data engineering engine designed to brutally normalize these chaotic datasets. It enforces the laws of physics directly at the ingestion layer, healing and standardizing millions of rows into strict physical dimensions.

**The Dual-Engine Architecture**
Phaethon is backend-agnostic. It seamlessly integrates with both **Pandas** and **Polars**. The engine automatically detects the type of DataFrame you pass into the pipeline and natively routes the execution to the appropriate C/C++ backend. Combined with Phaethon's dedicated **Rust parser** for zero-allocation string extraction, this guarantees extreme-speed physical data processing with absolutely minimal overhead.

---

## Defining a Schema

A Phaethon Schema is defined declaratively by subclassing `phaethon.Schema` and defining attributes with `phaethon.Field()`. You must bind each field to a specific physical dimension using standard Python type hints.

```python
import phaethon as ptn
import phaethon.units as u
import pandas as pd

class RocketTelemetry(ptn.Schema):
    # Extracts numbers from text, converts to Celsius, and coerces anomalies
    engine_temp: u.Celsius = ptn.Field(
        source="Raw_Temp",
        parse_string=True,
        min=-273.15,
        on_error="coerce",
        impute_by="mean"
    )
    
    # Simple numeric column mapped directly to Pascals
    chamber_pressure: u.Pascal = ptn.Field(source="Pressure_Pa")

# The Dirty Data
dirty_df = pd.DataFrame({
    "Raw_Temp": [" 450.5 C ", "ERR_SENSOR", "1200 K", "-500 C"], # -500 C violates Absolute Zero!
    "Pressure_Pa": [101325, 105000, None, 98000]
})

# Execute the Pipeline
clean_df = RocketTelemetry.normalize(dirty_df)

print(clean_df)
```

**Output:**
```text
   engine_temp  chamber_pressure
0       450.50          101325.0
1       688.67          105000.0  <- 'ERR_SENSOR' imputed with column mean
2       926.85          101441.6  <- 1200 K accurately converted to Celsius, pressure imputed
3       688.67           98000.0  <- -500 C violated physics, coerced to NaN, then imputed
```

---

## The Field API

The `ptn.Field()` constructor is the workhorse of the pipeline. It defines the extraction logic, physical boundaries, formatting, and data healing strategies for a single column.

### Mapping & Parsing

These parameters dictate how Phaethon locates the data and extracts numerical magnitudes from messy text formats using the Rust engine.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">source</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">The name of the column in the raw DataFrame. If omitted (or set to <code>...</code>), it auto-maps to the variable name.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">parse_string</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, routes the column through Phaethon's Rust backend to safely extract numeric magnitudes and unit strings from mixed text (e.g., <code>" 1.5e3 kg "</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">source_unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | type[BaseUnit]</span>
  </div>
  <div class="p-desc">The assumed starting unit if the raw data consists of naked numbers (or if <code>require_tag=False</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">require_tag</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code> (Default), the Rust parser will reject string entries that lack a physical unit tag unless a <code>source_unit</code> fallback is defined.</div>
</div>

**Example: Parsing complex strings with fallbacks**
```python
class ParsingSchema(ptn.Schema):
    weight: u.Kilogram = ptn.Field(source="W", parse_string=True, source_unit="lbs", require_tag=False)

# Raw: ["10 kg", "20", "50 lbs"]
# Output (in kg): [10.0, 9.07, 22.67]  <- '20' falls back to 'lbs' and converts to kg!
```

### Physical Bounds & Error Handling

Enforce the laws of physics directly at the ingestion layer. Determine how Phaethon reacts when it encounters anomalies or data that violates physical boundaries.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">min / max</span>
    <span class="p-sep">—</span>
    <span class="p-type">float | str</span>
  </div>
  <div class="p-desc">The absolute minimum and maximum allowed magnitudes. You can pass a string like <code>"10 kg"</code> to dynamically bound the data relative to the target unit.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">on_error</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Strategy for boundary violations or unparseable data:
    <ul>
      <li><code>'raise'</code>: Halts execution immediately and throws an <code>AxiomViolationError</code>.</li>
      <li><code>'coerce'</code>: Neutralizes the invalid value to <code>NaN</code> for later imputation.</li>
      <li><code>'clip'</code>: Forces the value to the nearest <code>min</code> or <code>max</code> bound.</li>
    </ul>
  </div>
</div>

**Example: The effects of `on_error`**
```python
class BoundSchema(ptn.Schema):
    # If pressure goes below 0, force it to exactly 0 (perfect vacuum)
    pressure: u.Pascal = ptn.Field(min=0, on_error="clip")

# Raw: [105000, -500, 98000]
# Output: [105000.0, 0.0, 98000.0]
```

### Data Healing & Imputation

<div class="param-box">
  <div class="param-header">
    <span class="p-name">null_values</span>
    <span class="p-sep">—</span>
    <span class="p-type">list[Any]</span>
  </div>
  <div class="p-desc">A list of custom sensor error codes (e.g., <code>["ERR", -9999]</code>) that should be converted to <code>NaN</code> before processing.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">impute_by</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Strategy to fill static <code>NaN</code> values: <code>'mean'</code>, <code>'median'</code>, <code>'mode'</code>, <code>'ffill'</code>, <code>'bfill'</code>, or a constant physical string (e.g., <code>"0 K"</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">interpolate</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Algorithmic curve-fitting strategy to heal missing time-series data (e.g., <code>'linear'</code>, <code>'spline'</code>). <em>Note: Polars backend natively supports only 'linear' and 'nearest'.</em></div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">outlier_std</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">Z-Score threshold to detect statistical anomalies. Values exceeding this standard deviation are coerced to <code>NaN</code>.</div>
</div>

**Example: Time-Series Interpolation**
```python
class TimeSeriesSchema(ptn.Schema):
    # Nullifies -999, then draws a linear line between valid points
    voltage: u.Volt = ptn.Field(null_values=[-999], interpolate="linear")

# Raw: [10.0, -999, -999, 25.0]
# Output: [10.0, 15.0, 20.0, 25.0]
```

### Localization & Formatting

Real-world datasets often use regional formatting or undocumented colloquialisms. Phaethon intercepts and standardizes these before the physics engine evaluates them.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">decimal_mark</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Overrides the global decimal character (e.g., <code>","</code> for European numbers like <code>"1,50"</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">thousands_sep</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Overrides the global thousands separator to strip it during extraction.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">aliases</span>
    <span class="p-sep">—</span>
    <span class="p-type">dict</span>
  </div>
  <div class="p-desc">Provides custom local aliases mapping dirty strings to official Phaethon symbols (e.g., <code>{"kg": ["kilos", "kilo-grams"]}</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">round</span>
    <span class="p-sep">—</span>
    <span class="p-type">int</span>
  </div>
  <div class="p-desc">Number of decimal places to strictly round the final output.</div>
</div>

*(Note: Parameters for `fuzzy_match` and `confidence` are utilized exclusively for Ontology mapping. Refer to the [Fuzzy Semantics](semantics.md) section).*

---

## Feature Engineering (`DerivedField`)

While standard `Fields` clean external data, `DerivedField` synthesizes entirely new Machine Learning features using cross-column dimensional algebra. 

Derived Fields are evaluated in a **second pass** of the pipeline. They utilize the `phaethon.col()` abstraction to build deferred Abstract Syntax Trees (AST), which are ultimately executed securely using native Pandas or Polars vectorized math.

```python
class AircraftSchema(ptn.Schema):
    # Pass 1: Clean raw extraction
    mass: u.Kilogram = ptn.Field(source="mass_kg", on_error="coerce", impute_by="mean")
    velocity: u.MeterPerSecond = ptn.Field(source="vel_ms")
    
    # Pass 2: Feature Synthesis (Kinetic Energy = 0.5 * m * v²)
    kinetic_energy: u.Joule = ptn.DerivedField(
        formula=0.5 * ptn.col("mass") * (ptn.col("velocity") ** 2),
        round=2
    )

# If mass is [1000] and velocity is [10], kinetic_energy becomes [50000.0]
```

---

## Lifecycle Hooks (Decorators)

If you need to perform complex DataFrame-level operations (like joining tables or manipulating datetime indices) before or after Phaethon processes the physics schema, you can use lifecycle hooks.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">@ptn.pre_normalize</span>
    <span class="p-sep">—</span>
    <span class="p-type">Decorator</span>
  </div>
  <div class="p-desc">Executes a method <em>before</em> any physical validation or Rust parsing occurs. The method receives and must return the raw DataFrame.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">@ptn.post_normalize</span>
    <span class="p-sep">—</span>
    <span class="p-type">Decorator</span>
  </div>
  <div class="p-desc">Executes a method <em>after</em> all fields and derived formulas are processed. Receives and returns the clean DataFrame.</div>
</div>

```python
class AdvancedSchema(ptn.Schema):
    speed: u.MeterPerSecond = ptn.Field()

    @ptn.pre_normalize
    def filter_bad_flights(cls, df):
        # Drop rows where test flights were aborted before passing to the engine
        return df[df['status'] != 'ABORTED']
```

---

## Schema Execution API

Once defined, the `Schema` class acts as an execution engine.

### .normalize()

```python
def normalize(
    df: _DataFrameT@normalize,
    keep_unmapped: bool = False,
    drop_raw: bool = True
) -> _DataFrameT@normalize
```
The primary entry point. It evaluates the input DataFrame (Pandas or Polars), routes it to the appropriate backend engine, and executes the normalization pipeline.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">df</span>
    <span class="p-sep">—</span>
    <span class="p-type">_DataFrameT</span>
  </div>
  <div class="p-desc">The dirty Pandas or Polars DataFrame.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">keep_unmapped</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, retains columns from the original DataFrame that were not defined in the schema. (Default: <code>False</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">drop_raw</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, drops the original source columns after they have been mapped and cleaned. (Default: <code>True</code>).</div>
</div>

**Scenario Setup:**
```python
class FlightSchema(ptn.Schema):
    temp: u.Celsius = ptn.Field(source="t_raw", parse_string=True)

dirty_df = pd.DataFrame({
    "t_raw": ["10 C", "20 C"],
    "flight_id": ["F-01", "F-02"]  # Metadata not defined in the Schema
})
```

#### Standard Normalization (Default)
By default, Phaethon completely drops the raw source columns and removes any unmapped metadata to guarantee a strictly physical, mathematically safe DataFrame.
```python
clean_df = FlightSchema.normalize(dirty_df)
# Columns remaining: ['temp']
```

#### Retaining Metadata
Use `keep_unmapped=True` to preserve important non-physical columns (like IDs, Timestamps, or String labels) alongside the cleaned tensors.
```python
clean_df = FlightSchema.normalize(dirty_df, keep_unmapped=True)
# Columns remaining: ['flight_id', 'temp']
```

#### Retaining Raw Source Data
Use `drop_raw=False` (in conjunction with `keep_unmapped=True`) to keep the original messy columns side-by-side with the cleaned physical columns. Highly useful for auditing, debugging, or comparing parser accuracy.
```python
clean_df = FlightSchema.normalize(dirty_df, keep_unmapped=True, drop_raw=False)
# Columns remaining: ['flight_id', 't_raw', 'temp']
```

### .blueprint()

```python
def blueprint() -> dict[str, _FieldBlueprint]
```
Generates a structural, JSON-serializable dictionary of the schema. Highly useful for Data Governance, automated Data Catalogs, or rendering API specifications.

**Example:**
```python
schema_json = RocketTelemetry.blueprint()
print(schema_json['engine_temp'])
```

**Output:**
```json
{
    "type": "Physical Dimension",
    "source_column": "Raw_Temp",
    "target": "Celsius",
    "bounds": "-273.15 to None",
    "imputation": "mean",
    "fuzzy_match": false,
    "target_unit": null
}
```

---

### .astensor()
```python
def astensor(
    df: DataFrameLike,
    requires_grad: GradTarget = False,
    encode_categories: bool = True,
    *,
    as_tuple: Literal[False] = False
) -> Dataset: ...

def astensor(
    df: DataFrameLike,
    requires_grad: GradTarget = False,
    encode_categories: bool = True,
    *,
    as_tuple: Literal[True]
) -> TensorLikeTuple: ...
```
This method bridges the declarative Data Engineering pipeline directly into the Deep Learning frontier. It transforms the normalized tabular DataFrame into an ecosystem of computation-ready PyTorch Tensors.


**How it routes your data:**
1. **Continuous Physics (`PTensor`)**: Any column defined as a standard `BaseUnit` (e.g., `Meter`, `Joule`) is wrapped in a [`PTensor`](../pinns/tensors.md)—Phaethon's custom PyTorch tensor that natively preserves physical dimensions and autograd computational graphs.
2. **Discrete Semantics (`torch.Tensor`)**: Any column defined using [Fuzzy Semantics](semantics.md) (like categories or ontologies) is automatically factorized into a standard, zero-indexed integer `torch.Tensor`, making it instantly ready for PyTorch `nn.Embedding` layers.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">df</span>
    <span class="p-sep">—</span>
    <span class="p-type">DataFrameLike</span>
  </div>
  <div class="p-desc">The normalized DataFrame yielding the data.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">requires_grad</span>
    <span class="p-sep">—</span>
    <span class="p-type">GradTarget</span>
  </div>
  <div class="p-desc">Specifies which physical fields should track computational gradients for Physics-Informed Neural Networks (PINNs). Can be a global boolean (<code>True/False</code>) or a specific list of field names.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">encode_categories</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code> (Default), string-based semantic fields are factorized into integers. If <code>False</code>, they remain raw strings.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">as_tuple</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, unpacks the tensors into a raw Python tuple matching the declaration order. If <code>False</code> (Default), returns a structured <a href="io.md">Phaethon Dataset</a> mapping.</div>
</div>

**Scenario Setup:**
```python
import phaethon as ptn
import phaethon.units as u

# Define a concrete Semantic State for our categories
class EngineStatus(ptn.SemanticState):
    OPTIMAL = ptn.Condition(target_unit=u.Celsius, max=100.0)
    CRITICAL = ptn.Condition(target_unit=u.Celsius, min=100.0)

class DeepLearningSchema(ptn.Schema):
    velocity: u.MeterPerSecond = ptn.Field()      # Continuous Physics
    temperature: u.Celsius = ptn.Field()          # Continuous Physics
    status: EngineStatus = ptn.Field(...)         # Discrete Semantic State

# Assume `clean_df` has been normalized via DeepLearningSchema.normalize()
```

#### Targeted Gradients
Returns a `phaethon.Dataset` mapping where only specific physical tensors track gradients for backpropagation.

```python
dataset = DeepLearningSchema.astensor(clean_df, requires_grad=['velocity'])

v_tensor = dataset['velocity'].tensor
status_tensor = dataset['status'].tensor

print(v_tensor.requires_grad) 
# Output: True (Ready for neural PDE differentiation!)

print(dataset['temperature'].tensor.requires_grad)
# Output: False

print(type(status_tensor), status_tensor.dtype)
# Output: <class 'torch.Tensor'> torch.int64 (Ready for nn.Embedding)
```

#### Tuple Unpacking
Bypasses the `phaethon.Dataset` wrapper entirely and hands you the raw tensors in the exact order they were declared in the Schema. Highly useful for pushing directly into `torch.Tensor` or `phaethon.pinns.PTensor`.

```python
v_tensor, temp_tensor, status_tensor = DeepLearningSchema.astensor(
    clean_df, 
    as_tuple=True
)

print(v_tensor.shape)
# Output: torch.Size([N, 1])
```

#### Raw Semantic Categories
By setting `encode_categories=False`, the semantic strings bypass integer factorization entirely. This is useful if you are exporting the data for non-PyTorch visualization tools.

```python
dataset = DeepLearningSchema.astensor(clean_df, encode_categories=False)

raw_strings = dataset['status'].to_numpy()
print(raw_strings)
# Output: ['OPTIMAL', 'CRITICAL', 'OPTIMAL', ...]
```