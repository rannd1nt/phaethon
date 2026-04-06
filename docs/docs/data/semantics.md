---
seo_type: TechArticle
title: "Fuzzy Semantics & Classification"
description: "Map dirty strings for Sci-ML pipelines using C++ RapidFuzz. Translate continuous physics into discrete categories for PyTorch embedding layers."
keywords: "fuzzy string matching python physics, physical to categorical translation, rapidfuzz data engineering, pytorch embedding preparation"
---

# Fuzzy Semantics & Ontologies

In data engineering, not everything is a continuous mathematical tensor. Real-world datasets are littered with categorical strings full of typos, inconsistent naming conventions, and arbitrary business logic.

Phaethon provides two powerful mechanisms for handling discrete categorical data:
1. **`Ontology`**: Uses high-speed fuzzy matching (via C++ RapidFuzz) to clean and map dirty string categories into canonical concepts.
2. **`SemanticState`**: Automatically translates continuous physical measurements (like Temperature or Pressure) into discrete semantic labels (like `"OPTIMAL"` or `"DANGER"`) based on strictly bounded physical conditions.

---

## Ontology (Categorical Mapping)

An `Ontology` defines a vocabulary of discrete concepts for a specific domain. Instead of writing endless `if/else` statements or SQL `CASE` clauses to clean typos, you define an Ontology and let Phaethon map the dirty data automatically.

### Defining Concepts

You define an Ontology by subclassing `phaethon.Ontology` and assigning `phaethon.Concept` attributes.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">aliases</span>
    <span class="p-sep">—</span>
    <span class="p-type">list[str] | Ellipsis</span>
  </div>
  <div class="p-desc">A list of dirty strings/aliases that should automatically map to this concept. Defaults to <code>...</code> (Ellipsis), which tells the engine to auto-generate aliases based on the assigned variable name.</div>
</div>

**Example: Weather Ontology**
```python
import phaethon as ptn

class WeatherCondition(ptn.Ontology):
    # Explicit aliases
    CLEAR = ptn.Concept(aliases=["sunny", "clear sky", "sun", "no clouds"])
    RAIN = ptn.Concept(aliases=["raining", "rainy", "drizzle", "heavy rain"])
    
    # Auto-generated aliases (will match "snow", "snow storm")
    SNOW = ptn.Concept(aliases=["blizzard", "snow storm"])
```

### Fuzzy Matching in Schemas

To use an Ontology in a data pipeline, assign your defined subclass (e.g., `WeatherCondition`) as the type hint in a Schema `Field`.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">fuzzy_match</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code>, Phaethon utilizes the C++ <strong>RapidFuzz</strong> library to calculate Levenshtein string distances. If an exact match fails, it will map typos to the closest defined concept.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">confidence</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">The minimum similarity score (<code>0.0</code> to <code>1.0</code>) required to accept a fuzzy match. Defaults to <code>0.85</code> (85%). If the best match is below this threshold, it is coerced to <code>NaN/None</code>.</div>
</div>

**Executing the Fuzzy Pipeline:**
```python
import phaethon as ptn
import pandas as pd

class FlightLog(ptn.Schema):
    # Enable fuzzy matching with an 80% confidence threshold
    weather: WeatherCondition = ptn.Field(
        fuzzy_match=True, 
        confidence=0.80,
        impute_by="CLEAR"  # Default to CLEAR if matching fails completely
    )

dirty_df = pd.DataFrame({
    "weather": ["sunny", "Rianing", "snw storm", "aliens attacking"]
})

clean_df = FlightLog.normalize(dirty_df)

print(clean_df)
```

**Output:**
```text
  weather
0   CLEAR  <- Exact match from aliases
1    RAIN  <- Typo ('Rianing') fuzzy matched to 'raining'
2    SNOW  <- Typo ('snw storm') fuzzy matched to 'snow storm'
3   CLEAR  <- 'aliens attacking' failed confidence threshold, imputed to 'CLEAR'
```

---

## Semantic States (Physics-to-Category)

A `SemanticState` is a dynamic classifier. Instead of matching strings to strings, it intercepts **continuous physical data** (like 150°C), evaluates its magnitude against a set of rules, and outputs a discrete string category.

### Defining Conditions

You define a Semantic State by subclassing `ptn.SemanticState` and assigning `ptn.Condition` attributes.

<div class="param-box">
  <div class="param-header">
    <span class="p-name">target_unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">type[BaseUnit]</span>
  </div>
  <div class="p-desc">The strict physical unit class to which the raw data must be converted before evaluation. This ensures your logic is immune to unit mixing (e.g., mixing Fahrenheit and Celsius in the source data).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">min / max</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">The numeric boundaries for this condition to trigger.</div>
</div>

**Example: Engine Thermal States**
```python
import phaethon as ptn
import phaethon.units as u

class EngineState(ptn.SemanticState):
    # Evaluates everything strictly in Celsius, regardless of input
    FROZEN = ptn.Condition(target_unit=u.Celsius, max=-10.0)
    OPTIMAL = ptn.Condition(target_unit=u.Celsius, min=-10.0, max=105.0)
    OVERHEATING = ptn.Condition(target_unit=u.Celsius, min=105.0, max=150.0)
    MELTDOWN = ptn.Condition(target_unit=u.Celsius, min=150.0)
```

### Utilizing States in Schemas

Assign your subclass (e.g., `EngineState`) as a `Field` target. Phaethon will automatically parse the incoming data, validate its physical dimension, and classify it based on your conditions.

```python
import pandas as pd

class TelemetrySchema(ptn.Schema):
    # The source data has mixed units!
    status: EngineState = ptn.Field(
        source="sensor_temp", 
        parse_string=True,
        on_error="coerce"
    )

dirty_df = pd.DataFrame({
    "sensor_temp": ["5 C", "250 F", "ERR", "1000 K"]
})

clean_df = TelemetrySchema.normalize(dirty_df)

print(clean_df)
```

**Output:**
```text
        status
0      OPTIMAL  <- 5°C falls in OPTIMAL
1  OVERHEATING  <- 250°F is ~121°C (OVERHEATING)
2         None  <- "ERR" coerced to NaN/None
3     MELTDOWN  <- 1000K is ~726°C (MELTDOWN)
```

---

## Embedding Preparation (ML)

While `Ontology` and `SemanticState` output clean string columns in Pandas/Polars, strings cannot be fed directly into Neural Networks. 

When you push a normalized DataFrame through the `Schema.astensor()` pipeline, Phaethon completely bypasses the standard Physics Tensor (`PTensor`) creation for these specific columns. 

Instead, any column annotated with a Semantic subclass is **automatically factorized** (alphabetically or by appearance order) into a **zero-indexed integer `torch.Tensor`**. This behavior instantly prepares your categorical data for PyTorch `nn.Embedding` layers without requiring manual Scikit-Learn `LabelEncoders`.

**Example:**
```python
# 1. Normalize the data
clean_df = FlightLog.normalize(dirty_df)
# clean_df['weather'] -> ["CLEAR", "RAIN", "SNOW", "CLEAR"]

# 2. Extract to ML Tensors
dataset = FlightLog.astensor(clean_df, encode_categories=True)

# 3. Inspect the Semantic Tensor
weather_tensor = dataset['weather'].tensor

print(type(weather_tensor))
# Output: <class 'torch.Tensor'>  (Notice it is NOT a PTensor!)

print(weather_tensor.dtype)
# Output: torch.int64

print(weather_tensor)
# Output: tensor([[0], [1], [2], [0]])
```