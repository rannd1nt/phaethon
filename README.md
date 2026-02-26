<div align="center">

<h1>Chisa — Unit-Safe Data Pipeline Schema</h1>

<p>
<img src="https://img.shields.io/badge/MADE_WITH-PYTHON-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/INTEGRATION-NUMPY-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/INTEGRATION-PANDAS-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
<img src="https://img.shields.io/badge/LICENSE-MIT-red?style=for-the-badge" alt="License">
</p>

<p>
<i>Normalize messy heterogeneous units and enforce physical integrity before your data hits ML or production systems.</i>
</p>

</div>

**Chisa** is a declarative schema validation and semantic data transformation tool designed for Data Engineers. It rescues your data pipelines from the nightmare of mixed units, bizarre abbreviations, and impossible physical values.

While standard schema tools (like Pydantic or Pandera) only validate *data types* (e.g., ensuring a value is a `float`), Chisa validates **physical reality**. If you are ingesting IoT sensor streams, parsing messy logistics CSVs, or processing manufacturing Excel sheets, Chisa ensures your numbers obey the laws of physics before they enter your database.

---

## 🚀 The Nightmare vs. The Chisa Way

Real-world data is rarely clean. A single dataset might contain `"1.5e3 lbs"`, `"  -5 kg  "`, missing values, and typos like `"20 pallets"`. Standard pandas workflows force you to write fragile regex and manual `if-else` blocks. 

**Chisa solves this declaratively.**

```python
import pandas as pd
import chisa as cs
from chisa import u

class GlobalFreightSchema(cs.Schema):
    gross_weight: u.Kilogram = cs.Field(
        source="Weight_Log", 
        parse_string=True, 
        on_error='coerce', 
        round=2,
        min=0 # Axiom Bound: Cargo mass cannot be negative!
    )
    cargo_volume: u.CubicMeter = cs.Field(
        source="Volume_Log", 
        parse_string=True, 
        on_error='coerce'
    )

df_messy = pd.DataFrame({
    'Weight_Log': ["1.5e3 lbs", "  -5 kg  ", "20 pallets", "150", "kg"],
    'Volume_Log': ["100 m^3", "500 cu_ft", "1000", "", "NaN"]
})

# Execute the pipeline instantly via vectorized masking
clean_df = GlobalFreightSchema.normalize(df_messy)
```

**The Output:**
Chisa cleanly parses `"1.5e3 lbs"` to `680.39 kg`, accurately converts `"cu_ft"` to Cubic Meters, and safely nullifies physical anomalies (like `-5 kg`), bare numbers, and vague inputs (`"20 pallets"`) to `NaN`—all automatically.

---

## 🧠 Smart Error Intelligence

Data pipelines shouldn't just crash; they should tell you *how* to fix them. If you enforce strict data rules (`on_error='raise'`), Chisa provides unparalleled Developer Experience (DX) for debugging massive DataFrames:

```text
NormalizationError: Normalization failed for field 'gross_weight' at index [2].
   ► Issue              : Unrecognized unit 'pallets'
   ► Expected Dimension : mass
   ► Raw Value Sample   : '20 pallets'
   ► Suggestion         : Fix the raw data, register the unit, or set Field(on_error='coerce').
```

---

## ⚡ Performance: The Vectorization Advantage

Standard unit libraries (like Pint) struggle with **heterogeneous strings** (mixed units in the same column), forcing developers to use slow `pandas.apply()` loops to parse row-by-row. Chisa bypasses this entirely using native NumPy vectorization and Pandas Boolean masking.

When stress-tested against 100,000 rows of heterogeneous data (e.g., a mix of `lbs` and `oz` targeting `kg`):
* *Traditional (Pint + Pandas Apply):* ~14.71 seconds
* *Chisa (Vectorized Schema):* **~0.046 seconds** *(>316x Faster)*

> *Transparency Note: You can reproduce this 99.6% reduction in latency using the `benchmarks/benchmark_vs_pint.py` script included in this repository.*

---

## 🪝 Pipeline Hooks (Inversion of Control)

Need to filter offline sensors before parsing, or trigger an alarm if a physical threshold is breached? Inject your own domain logic directly into the validation lifecycle.

```python
class ColdChainPipeline(cs.Schema):
    temp: u.Celsius = cs.Field(source="raw_temp", parse_string=True)

    @cs.pre_normalize
    def drop_calibration_pings(cls, raw_df):
        """Runs BEFORE Chisa parses the strings. Removes sensor test pings."""
        return raw_df[raw_df['status'] != 'CALIBRATION']

    @cs.post_normalize
    def enforce_spoilage_check(cls, clean_df):
        """Runs AFTER all temperatures (e.g., Fahrenheit) are standardized to Celsius."""
        if clean_df['temp'].max() > -20.0:
            raise ValueError("CRITICAL: Vaccine shipment spoiled! Temp exceeded -20°C.")
        return clean_df
```

---
## 🏎️ The Fluent API (Quick Inline Conversions)

For simple scripts, logging, or UI components where you don't need full declarative schemas, Chisa provides a highly readable, chainable Fluent API.

```python
import chisa as cs

# Simple scalar conversion
speed = cs.convert(120, 'km/h').to('m/s').resolve()
print(speed) # 33.333333333

# Powerful cosmetic formatting for logs
text = cs.convert(1000, 'm').to('cm').use(format='verbose', delim=True).resolve()
print(text) # "1,000 m = 100,000 cm"
```
---

## 📚 Examples & Tutorials

To help you integrate Chisa into your existing workflows, we provide a comprehensive suite of examples in the `examples/` directory.

### Interactive Crash Course (Google Colab)
The fastest way to learn Chisa is through our interactive notebooks. No local installation required!

| Tutorial | Description | Link |
| :--- | :--- | :--- |
| **01. Fundamentals** | Core concepts, Axiom Engine, and Type Safety. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rannd1nt/chisa/blob/main/examples/T01_Chisa_Fundamentals.ipynb) |
| **02. Workflow Demo** | Real-world engineering with Pandas & Matplotlib. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rannd1nt/chisa/blob/main/examples/T02_Chisa_RealWorld_Workflow.ipynb) |

### Python Scripts Reference
For detailed, standalone script implementations, explore our `examples/` directory:

* **Phase 1: Declarative Data Pipelines (Data Ingestion)**
    * `01_wearable_health_data.py`: Standardizing messy smartwatch exports (BPM, kcal vs cal, body temperature).
    * `02_food_manufacturing_scale.py`: Safely converting industrial recipe batches across cups, tablespoons, grams, and fluid ounces.
    * `03_multi_region_tariffs.py`: Parsing mixed currency and weight strings (lbs, oz, kg) in a single pass to calculate global shipping costs.
    * `04_energy_grid_audits.py`: Normalizing utility bill chaos (MMBtu, kWh, Joules) into a single unified Pandas cost report.

* **Phase 2: High-Performance Vectorization & Algebra**
    * `05_f1_telemetry_vectorization.py`: Array math on RPM, Speed, and Tire Pressure operating on millions of rows in milliseconds.
    * `06_structural_stress_testing.py`: Cross-unit algebra combining Kips, Newtons, and Pound-force over Square Meters for civil engineering loads.
    * `07_financial_billing_precision.py`: Understanding when to use `.mag` (fast Python floats for Math/ML) vs `.exact` (high-precision Decimals for strict financial audits).

* **Phase 3: The Axiom Engine (Domain-Driven Engineering)**
    * `08_gas_pipeline_thermodynamics.py`: Using Contextual Shifts to dynamically calculate industrial gas volume expansion based on real-time temperature and pressure (PV=nRT).
    * `09_end_to_end_esg_pipeline.py`: The Grand Unified Theory of Chisa. Synthesizing a custom dimension (Carbon Intensity), cleaning data into it via Schema, and guarding algorithms with `@require` and `@prepare`.

* **Phase 4: Real-World Ecosystem Integration**
    * `10_pandas_groupby_physics.py`: Integrating Chisa arrays directly with Pandas `GroupBy` to aggregate daily IoT power production into monthly summaries.
    * `11_scikit_learn_transformer.py`: Building a custom ML `BaseEstimator` to autonomously normalize heterogeneous unit arrays before training a Random Forest.
    * `12_handling_sensor_drift.py`: Using NumPy array masks and vectorization to neutralize factory machine calibration errors without slow `for` loops.
    * `13_dynamic_alert_thresholds.py`: Simulating an IoT streaming pipeline where safety limits (`@axiom.bound`) change dynamically based on the machine's operating context.
    * `14_cloud_compute_costs.py`: Utilizing extreme Metaclass algebra (`Currency / (RAM * Time)`) to synthesize and calculate abstract Server Compute billing rates ($ / GB-Hour).

---

## 🔬 The Engine: Explicit Dimensional Algebra

While Chisa's Schema is built for Data Engineering pipelines, underneath it lies a highly strict, Metaclass-driven Object-Oriented physics engine. If you are a Data Scientist, you can extract your clean data into Chisa Arrays for cross-dimensional mathematics with zero memory leaks.

```python
import numpy as np
import chisa as cs
from chisa import u

# Seamless cross-unit Metaclass Vectorized Synthesis (Mass * Acceleration = Force)
Mass = u.Kilogram(np.random.uniform(10, 100, 1_000_000))
Acceleration = (u.Meter / (u.Second ** 2))(np.random.uniform(0.5, 9.8, 1_000_000))

Force = Mass * Acceleration
Force_kN_array = Force.to(u.Newton * 1000).mag
```
> 📖 **Deep Dive:** For advanced features like Dynamic Contextual Scaling (Mach), Axiom Bound derivation, and Registry Introspection, please refer to our **[Advanced Physics Documentation](https://github.com/rannd1nt/chisa/blob/main/docs/advanced_physics.md)**.

---

## 📦 Installation
**Install via pip:**
```bash
pip install chisa
```
**Requirements:**
- Python 3.8+
- numpy >= 1.26.0
- pandas >= 2.0.0
 
---

## 🛠 Roadmap & TODOs
- **String Expression Parser:** Upgrading the registry to autonomously parse complex composite strings (e.g., `"kg * m / s^2"`).
- **Global Context Manager:** Introduce `chisa.conf()` to temporarily force data types or ignore boundary rules.
- **Polars Integration:** Expanding `Schema.normalize()` to support Polars DataFrames for ultra-fast Rust-based data processing.

---

## 🤝 Contributing
Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make to Chisa are **greatly appreciated**.

---

## License
Distributed under the MIT License. See the `LICENSE` file for more information.