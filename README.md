<div align="center">

<h1>Phaethon — Dimensional Data Pipeline & Semantic Data Engineering Framework</h1>

<p>
<img src="https://img.shields.io/badge/MADE_WITH-PYTHON-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/INTEGRATION-NUMPY-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/INTEGRATION-PANDAS-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
<img src="https://img.shields.io/badge/INTEGRATION-POLARS-blue?style=for-the-badge&logo=polars&logoColor=white" alt="Polars">
<img src="https://img.shields.io/badge/LICENSE-MIT-red?style=for-the-badge" alt="License">
</p>

<p>
<i>Enforce physical laws, translate semantic concepts, and normalize messy units before your data hits ML or production systems.</i>
</p>

</div>

**Phaethon** is a declarative schema validation and semantic data transformation tool designed for Data Engineers. It rescues your data pipelines from the nightmare of mixed units, bizarre abbreviations, typo-ridden categorical data, and impossible physical values.

While standard schema tools (like Pydantic or Pandera) only validate *data types* (e.g., ensuring a value is a `float`), Phaethon validates **physical reality and semantic intent**. Whether you are ingesting IoT sensor streams, parsing messy logistics CSVs, or processing multi-currency global transactions, Phaethon ensures your data obeys the laws of physics and domain logic before it enters your database.

---

## 🚀 The Nightmare vs. The Phaethon Way

Real-world data is rarely clean. A single dataset might contain `"1.5e3 lbs"`, `"  -5 kg  "`, missing values, and typos like `"20 pallets"`. Standard Pandas/Polars workflows force you to write fragile regex and manual `if-else` blocks. 

**Phaethon solves this declaratively.**

```python
import pandas as pd
import phaethon as ptn
from phaethon import u

class GlobalFreightSchema(ptn.Schema):
    gross_weight: u.Kilogram = ptn.Field(
        source="Weight_Log", 
        parse_string=True, 
        on_error='coerce', 
        round=2,
    )
    cargo_volume: u.CubicMeter = ptn.Field(
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
Phaethon cleanly parses `"1.5e3 lbs"` to `680.39 kg`, accurately converts `"cu_ft"` to Cubic Meters, and safely nullifies physical anomalies (like `-5 kg`), bare numbers, and vague inputs (`"20 pallets"`) to `NaN`—all automatically.

---

## 🤖 Semantic Intelligence & ML Feature Extraction

Stop writing endless `.map()` dictionaries to clean up categorical data. Phaethon introduces declarative **Ontologies** and **Semantic States** that use C++ string metrics (RapidFuzz) to autocorrect typos, classify continuous numbers into discrete categories, and synthesize entirely new ML features on the fly.

```python
# 1. Map dirty strings to clean Categories with Auto-Correction
class DeviceType(ptn.Ontology):
    SENSOR = ptn.Concept(aliases=["sn", "sensr", "sensor_node"])
    GATEWAY = ptn.Concept(aliases=["gw", "hub"])

# 2. Classify physical numbers into ML Logic, ignoring unit chaos!
class PowerStatus(ptn.SemanticState):
    LOW = ptn.Condition(u.Watt, max=10.0)
    NORMAL = ptn.Condition(u.Watt, min=10.01, max=50.0)
    HIGH = ptn.Condition(u.Watt, min=50.01)

class IoTEdgeSchema(ptn.Schema):
    device: DeviceType = ptn.Field("raw_dev", fuzzy_match=True, impute_by="UNKNOWN")
    
    # Extract features safely across domains
    voltage: u.Volt = ptn.Field("raw_v", min=0)
    current: u.Ampere = ptn.Field("raw_a")
    
    # Synthesize Cross-Column ML Features using Dimensional Algebra
    power: u.Watt = ptn.DerivedField(formula=ptn.col("voltage") * ptn.col("current"))
    
    # Classify the synthesized/raw power into a Semantic State
    status: PowerStatus = ptn.Field("raw_power", parse_string=True)

df_iot = pd.DataFrame({
    "raw_dev": ["Sensr", "Gate way", "Alien Tech"],
    "raw_v": [220, 230, 110],
    "raw_a": [1.5, 2.0, 1.2],
    "raw_power": ["5 W", "15000 mW", "0.06 kW"]
})

clean_iot_df = IoTEdgeSchema.normalize(df_iot)
```

---

## 💸 Global FinTech & Econo-Physics

Phaethon treats Currency as a highly volatile physical dimension. You can inject real-time exchange rates (context) seamlessly without altering the core pipeline. It inherently understands inverse routing (e.g., automatically flipping `usd_to_idr` to calculate `idr_to_usd`).

```python
class ECommerceReport(ptn.Schema):
    revenue_idr: u.IndonesianRupiah = ptn.Field("sales", parse_string=True)

df_sales = pd.DataFrame({
    "sales": ["100 EUR", "1500 JPY", "5 USD", "50000 IDR"]
})

# Inject Live FX Rates (Direct & Inverse quotes are handled automatically)
live_rates = {
    'eur_to_usd': 1.10,     
    'usd_to_jpy': 150.0,    
    'usd_to_idr': 16000.0   
}

with ptn.using(context=live_rates):
    clean_sales_df = ECommerceReport.normalize(df_sales)
```

---

## ⚡ Performance: Native Pandas & Polars Backends

Standard unit libraries struggle with **heterogeneous strings**, forcing slow `pandas.apply()` loops. Phaethon bypasses this using a backend-agnostic architecture natively detecting your DataFrame type.

Both the Pandas Vectorized Engine and the Polars Lazy Engine can process and validate **1,000,000 rows of highly unstructured, dirty physics strings in ~3 seconds**. 

*(Note: Polars currently relies on a `map_batches` NumPy bridge to evaluate Phaethon's strict Metaclass Object geometry, neutralizing its inherent Rust multi-threading speed. Achieving true zero-copy execution without hitting the Python GIL is our top priority for v0.4.0—see Roadmap).*

---

## ⚖️ Absolute Precision: 100% Parity with Pint

Phaethon doesn't just parse strings quickly; it calculates physical reality flawlessly. From quantum scales (`eV`) to astronomical masses (`M_jup`), the core engine retains absolute `float64` precision without underflow truncation.

We enforce **100% mathematical parity** against the industry-standard `Pint` library using brutal, property-based automated testing (`hypothesis`). 

* **Empirical Accuracy:** Phaethon achieves zero-deviation parity across hundreds of randomized, bidirectional cross-dimensional conversions.
* **Superior Vocabulary:** Phaethon natively parses **65+ specialized units** (e.g., historical mass, regional volumes, astrophysical constants) that standard libraries fail to recognize or fatally misinterpret due to string hyphenation bugs.

> *Transparency Note: You can audit and run the rigorous O(N) Hub-and-Spoke accuracy tests yourself via the `benchmarks/test_pint_parity.py` script included in this repository.*

---


## 🪝 Pipeline Hooks (Inversion of Control)

Need to filter offline sensors before parsing, or trigger an alarm if a physical threshold is breached? Inject your own domain logic directly into the validation lifecycle.

```python
class ColdChainPipeline(ptn.Schema):
    temp: u.Celsius = ptn.Field(source="raw_temp", parse_string=True)

    @ptn.pre_normalize
    def drop_calibration_pings(cls, raw_df):
        """Runs BEFORE Phaethon parses the strings. Removes sensor test pings."""
        return raw_df[raw_df['status'] != 'CALIBRATION']

    @ptn.post_normalize
    def enforce_spoilage_check(cls, clean_df):
        """Runs AFTER all temperatures (e.g., Fahrenheit) are standardized to Celsius."""
        if clean_df['temp'].max() > -20.0:
            raise ValueError("CRITICAL: Vaccine shipment spoiled! Temp exceeded -20°C.")
        return clean_df
```

---

## 🏎️ The Fluent API (Extremely Versatile Conversions)

 The Fluent API (`ptn.convert`) is not just for scalars. It intelligently digests raw floats, N-Dimensional NumPy Arrays, Python Lists, and even instantiated `BaseUnit` objects, returning perfectly typed outputs (`dtype`, `out`) for strict IDE intelligence.

```python
import numpy as np
import phaethon as ptn
from phaethon import u

# 1. High-Speed Vectorized Arrays (Returns np.ndarray)
arr_in = np.random.uniform(10, 100, 100_000)
arr_out = ptn.convert(arr_in, 'km/h').to('m/s').use(out='raw').resolve()

# 2. BaseUnit Object Iterables (Returns List[str])
obj_list = [u.Celsius(0), u.Celsius(100)]
str_list = ptn.convert(obj_list).to('F').use(out='verbose', delim=True).resolve()
# Output: ['0 °C = 32 °F', '100 °C = 212 °F']

# 3. High-Precision Audits (Returns Python Decimal)
exact_val = ptn.convert("1.5", "kg").to("g").use(dtype='decimal').resolve()
```

---

## 📚 Examples & Tutorials
> ⚠️ **Documentation Notice:** The interactive notebooks and Python scripts in the `examples/` directory are currently optimized for Phaethon **v0.2.3**. While the core engine fundamentals remain strictly identical, newer v0.3.0 architectural leaps are not yet reflected in these tutorials. A massive overhaul of all educational materials is scheduled for the upcoming **v0.4.0 (SciML Integration)** release.
To help you integrate Phaethon into your existing workflows, we provide a comprehensive suite of examples in the `examples/` directory.

### Interactive Crash Course (Google Colab)
The fastest way to learn Phaethon is through our interactive notebooks. No local installation required!

| Tutorial | Description | Link |
| :--- | :--- | :--- |
| **01. Fundamentals** | Core concepts, Axiom Engine, and Type Safety. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rannd1nt/phaethon/blob/main/examples/T01_Phaethon_Fundamentals.ipynb) |
| **02. Workflow Demo** | Real-world engineering with Pandas & Matplotlib. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rannd1nt/phaethon/blob/main/examples/T02_Phaethon_RealWorld_Workflow.ipynb) |

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
    * `09_end_to_end_esg_pipeline.py`: The Grand Unified Theory of Phaethon. Synthesizing a custom dimension (Carbon Intensity), cleaning data into it via Schema, and guarding algorithms with `@require` and `@prepare`.

* **Phase 4: Real-World Ecosystem Integration**
    * `10_pandas_groupby_physics.py`: Integrating Phaethon arrays directly with Pandas `GroupBy` to aggregate daily IoT power production into monthly summaries.
    * `11_scikit_learn_transformer.py`: Building a custom ML `BaseEstimator` to autonomously normalize heterogeneous unit arrays before training a Random Forest.
    * `12_handling_sensor_drift.py`: Using NumPy array masks and vectorization to neutralize factory machine calibration errors without slow `for` loops.
    * `13_dynamic_alert_thresholds.py`: Simulating an IoT streaming pipeline where safety limits (`@axiom.bound`) change dynamically based on the machine's operating context.
    * `14_cloud_compute_costs.py`: Utilizing extreme Metaclass algebra (`Currency / (RAM * Time)`) to synthesize and calculate abstract Server Compute billing rates ($ / GB-Hour).


---
## 🔬 The Engine: Explicit Dimensional Algebra

While Phaethon's Schema is built for Data Engineering pipelines, underneath it lies a highly strict, Metaclass-driven Object-Oriented physics engine. If you are a Data Scientist, you can extract your clean data into Phaethon Arrays for cross-dimensional mathematics with zero memory leaks.

```python
import numpy as np
import phaethon as ptn
from phaethon import u

# Seamless cross-unit Metaclass Vectorized Synthesis (Mass * Acceleration = Force)
Mass = u.Kilogram(np.random.uniform(10, 100, 1_000_000))
Acceleration = (u.Meter / (u.Second ** 2))(np.random.uniform(0.5, 9.8, 1_000_000))

Force = Mass * Acceleration
Force_kN_array = Force.to(u.Newton * 1000).mag
```
> 📖 **Deep Dive:** For advanced features like Dynamic Contextual Scaling (Mach), Axiom Bound derivation, and Registry Introspection, please refer to our **[Advanced Physics Documentation](https://github.com/rannd1nt/phaethon/blob/main/docs/advanced_physics.md)**.

---

## 📦 Installation
**Install via pip:**
```bash
pip install phaethon
```
**With Polars Backend Support:**
```bash
pip install phaethon[polars]
```

**Requirements:**
- Python 3.10+
- numpy >= 1.26.0
- pandas >= 2.0.0
- rapidfuzz >= 3.0.0
 
---

## 🛠 Roadmap & Future Horizons (v0.4.0+)

Phaethon is actively evolving to become the ultimate dimensional engine for Scientific Machine Learning (SciML) and high-performance Data Engineering. Our next major milestones include:

* **Pure Rust Parsing Core:** Rewriting the heavy string-extraction regex layer entirely in Rust via PyO3 to bypass Python's GIL and push parsing speeds to the hardware limit.
* **Zero-Copy Backend Integration:** Expanding our backend-agnostic architecture to natively support PyArrow memory layouts, achieving true zero-copy execution for Polars.
* **Physics-Informed Neural Networks (PINNs):** Developing the `phaethon.pinns` experimental module. Deep binding integration with PyTorch to allow neural networks to intrinsically understand physical dimensions, Buckingham Pi reductions, and autograd scaling constraints.

---

## 🤝 Contributing
Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make to Phaethon are **greatly appreciated**.

---

## License
Distributed under the MIT License. See the `LICENSE` file for more information.