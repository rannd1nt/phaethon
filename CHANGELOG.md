# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-03-13

This release marks a major architectural leap, consolidating high-performance data engineering with physical, financial, and semantic intelligence. Version 0.3.0 introduces native Polars support via Rust-backed expressions, a multi-tier configuration hierarchy, massive dimensional expansions, and a complete overhaul of Developer Experience (DX) utilizing Python 3.10+ declarative standards.

### High-Performance Backends
* **feat(polars):** Introduced native support for `polars.DataFrame` as an **optional dependency** (installable via `[polars]` or `[all]`). Phaethon now implements a backend-agnostic protocol that detects Polars objects and executes normalization using high-speed Polars Expressions (`pl.Expr`).
* **feat(engine):** Developed a vectorized NumPy bridge via `map_batches` for Polars, allowing complex physical axiom validation to run at near-native speeds while maintaining 100% mathematical parity with the Pandas engine.
* **feat(engine):** Implemented a "NaN Sweeper" and "Struct Wrapper" logic for the Polars backend to ensure that regex-rejected strings and axiom violations are correctly neutralized to `null` values, matching the behavior of the established Pandas engine.

### Dimensional Core & Tensor Algebra
* **feat(api):** Overhauled the **Fluent Data Engineering API** (`ptn.convert().to().use().context().resolve()`). This chainable, lazily-evaluated builder pattern now fully supports lists of Phaethon objects, N-dimensional NumPy tensors, mixed-unit iterables, and raw scalars natively without Python loop overheads on vectorized operations.
* **feat(api):** Implemented strict calculation engine interception via `.use(dtype=...)`. The pipeline automatically handles safe upcasting to high-precision `Decimal` (bypassing native Python float degradation via string casting) and strict downcasting to `float64` for raw performance *before* dimensional algebra is executed.
* **feat(api):** Upgraded OOP Conversion Interface. The `BaseUnit.to()` method now accepts localized, on-the-fly context injections (`obj.to(Target, context={...})`). This allows safe, isolated financial conversions without mutating the underlying object's state or relying on global configs.
* **feat(tensor):** Integrated native NumPy proxying directly into `BaseUnit`. Instances wrapping NumPy arrays now natively support array slicing (`__getitem__`), properties (`shape`, `ndim`, `T`), and shape manipulation (`reshape`, `flatten`) while preserving their physical unit wrappers.
* **feat(vmath):** Added native vectorized statistical methods to `BaseUnit` (`sum`, `mean`, `max`, `min`). Reductions along specific axes now correctly return structurally instantiated physical tensors rather than naked `float64` arrays.
* **feat(algebra):** Engineered **Syntactic Sugar for Cross-Entity Operations** and **Dimensionless Collapse**. The physics engine seamlessly executes mathematics between Instances and naked Classes implicitly. Furthermore, operations that mathematically cancel out (e.g., `u.Meter / u.Meter`) now intelligently collapse into a dimensionless `BaseUnit` object rather than a primitive `float`, preserving strict OOP API contracts.
* **feat(algebra):** Introduced **Class-Level Hierarchy Comparisons** (`<`, `>`, `<=`, `>=`). Developers can inherently sort and validate unit hierarchies without instantiating them (e.g., `u.Gigabyte > u.Megabyte` natively evaluates to `True`).
* **feat(algebra):** Engineered **Dynamic Context Inheritance for Derived Units**. Metaclass-synthesized units (e.g., `Euro / Gram`) now dynamically evaluate their base multipliers at runtime. This guarantees that complex econo-physics units instantly react to real-time `context` injections without suffering from static multiplier lock-in.
* **feat(operators):** Implemented advanced physics dunder methods. The engine now fully supports Matrix Multiplication / Dot Products (`@`) for dimensional synthesis, Floor Division (`//`) for discrete quantization, Modulo (`%`) for phase/cycle resets, and vector manipulations (`-`, `+`, `abs`, `round`).
* **fix(engine):** Overhauled the `_normalize_types` mathematical router. Eliminated forced `Decimal` casting ("The Decimal Dictatorship"). The engine now dynamically preserves native `float64` for maximum computational speed, only escalating to high-precision `Decimal` mathematics when explicitly requested by the user.
* **fix(security):** Eradicated Global Mutable State in the dimensional registry. The `_DIMENSIONAL_DNA` is now strictly encapsulated within a private singleton (`_PhysicsGenome`) utilizing Python name mangling (`__dna`), preventing accidental global namespace pollution or malicious mutation of physical axioms.

### Semantic Intelligence & Machine Learning
* **feat(semantics):** Introduced the Declarative Semantic Transformation API (`ptn.Ontology`, `ptn.Concept`, `ptn.SemanticState`, `ptn.Condition`). Users can now map discrete raw strings to canonical concepts, or classify continuous physical vectors into discrete logical states strictly bounded by dimensional physics (e.g., mapping `u.Celsius` ranges into "Cold", "Warm", "Hot").
* **feat(semantics):** Integrated RapidFuzz (now promoted to a **mandatory core dependency**) for Vectorized Semantic Matching. Added `fuzzy_match=True` and `confidence` thresholds to `ptn.Field`, enabling the engine to automatically auto-correct typos in categorical/ontology data using C++ string metrics.
* **feat(schema):** Introduced `ptn.DerivedField` and `ptn.col()`. Users can now synthesize new Machine Learning features (e.g., computing Power from Voltage and Current) safely across dimensional bounds via a custom Abstract Syntax Tree (AST) evaluator.
* **feat(schema):** Implemented `Schema.blueprint()`. Generates a strict, JSON-serializable `TypedDict` structural blueprint of the schema, perfect for automated Data Catalogs and enterprise Data Governance.

### Tiered Configuration & Industrial Quality
* **feat(config):** Engineered a 3-Tier Configuration Hierarchy for managing engine state (Global -> Block -> Field). This allows for thread-safe localization (decimal marks/thousands separators) and dynamic alias management without global state pollution.
* **feat(schema):** Added Physics-Aware Boundaries (`min`, `max`) to `ptn.Field`. The engine now automatically performs cross-unit conversion before evaluating boundary constraints (e.g., rejecting "120 lbs" against a "50 kg" limit).
* **feat(schema):** Introduced Dimensional Imputation (`impute_by`) and Statistical Anomaly Rejection (`outlier_std`). Users can rescue `NaN` values using statistical methods ("mean", "median", "mode") or physically identify and neutralize data points exceeding a specified Standard Deviation (Z-Score).
* **feat(engine):** Expanded `on_error='clip'` Behavior. The pipeline now correctly forces invalid numbers to strictly attach to the nearest mathematical bound defined by either the user's Schema `min`/`max` or the unit's intrinsic `@axiom.bound` limit across both Pandas and Polars backends.
* **feat(engine):** Introduced **"God Mode" (`ignore_axiom_bound=True`)**. Developers can now strategically override and bypass all intrinsic physical laws (e.g., allowing temperatures below Absolute Zero) for experimental testing and simulation logic, deployable via Field, Block (`using`), or Global Config.

### Majestic Developer Experience (DX) & Typing Overhaul
* **feat(dx):** Engineered **"Type-State" Generic Overloads** for the Fluent API. The `_ConversionBuilder` is now a true `Generic[_T_Out]`. Deployed 5 precise `@overload` signatures for `convert()` and **16 massive overloads** for `.use()` to completely eradicate `Any` types. IDEs now perfectly predict the exact structural return type of `.resolve()` (locking to `Decimal`, `list[BaseUnit]`, `list[float]`, `str`, or `np.ndarray`). Also refactored `.use()` parameters: renamed `mode` to `dtype` and `format` to `out` for a more native Data Science feel.
* **feat(dx):** Implemented the **IDE Tooltip Hack (`__init__` routing)**. Docstrings for highly complex declarative classes (`ptn.Field`, `ptn.Concept`, `ptn.Condition`) have been surgically routed to their `__init__` methods. Strict IDEs (VS Code/Pylance) will now reliably render comprehensive parameter tooltips during instantiation.
* **fix(dx):** Eliminated **Union Method Pollution**. By surgically separating scalar, iterable, and array type-hints at the `convert()` entry point, strict IDEs (Pylance/Mypy) no longer hallucinate NumPy array methods on simple floating-point scalars.
* **refactor(typing):** Upgraded minimum requirement to **Python 3.10+**. The entire codebase has been refactored to utilize PEP 604 (`|` operator) and native types, discarding legacy `typing` modules for an incredibly clean, "Majestic" code structure.
* **refactor(typing):** Enforced absolute boundary separation between Metaclass (Blueprint) and Instance operations. Purged `Any` fallbacks in `_PhaethonUnitMeta` return types. Strict IDEs now structurally recognize dynamically synthesized units as formal Classes (semantic highlighting), fully activating constructor autocompletion.
* **refactor(typing):** Formalized unified type aliases (`ConvertibleInput`, `ContextDict`, `ErrorAction`, `ImputeMethod`, etc) across the physics engine. This provides crystal-clear signature documentation for scalar, NumPy array, and unit instance inputs.
* **feat(typing):** Added PEP 561 `py.typed` compliance. IDEs (VS Code, PyCharm) and strict Type Checkers (Mypy, Pylance) now fully recognize Phaethon's complex `@overload` signatures, `TypeVar` generics, and `Protocol` bindings.
* **fix(typing):** Resolved strict type hinting for core properties (`.mag`, `.exact`) using explicit unions (`float | np.ndarray | Decimal`), successfully activating full IDE intelligence and autocomplete for NumPy array methods.
* **feat(dx):** Implemented **Dynamic Metaclass Docstrings**. Dynamically synthesized classes (e.g., `Meter / Second`) now automatically generate rich `__doc__` attributes detailing their algebraic origin, symbol, and base multiplier, enhancing object inspection in Jupyter Notebooks.
* **feat(dx):** Implemented **Ellipsis (`...`) Auto-Mapping** for declarative schemas. Using `ptn.Field(...)` or `ptn.Concept(...)` automatically infers the target DataFrame column or Ontology alias from the variable name itself, strictly enforcing the DRY (Don't Repeat Yourself) principle.
* **refactor(dx):** Applied strict framework namespace conventions. Transitioned internal classes to protected (`_`) and injected Framework Magic Attributes (`__phaethon_fields__`) to ensure absolute zero collision with user-defined database columns or variables.
* **refactor(vmath):** Overhauled `phaethon.core.vmath` API. Mathematical routers are now elegantly shadowed (`abs`, `max`, `min`, `pow`) using `builtins` internally, providing a purely intuitive, native Python experience without infinite recursion risks.

### Domain Expansions: FinTech, Electromagnetism, & Photometry
* **feat(engine):** Massive expansion of the `_DIMENSIONAL_DNA` registry. The engine now dynamically resolves complex signatures across Kinematics, Thermodynamics, Fluid Dynamics, Computing (`data_rate`), and **Econo-physics** (e.g., dynamically resolving `Currency / Energy` into `'price_per_energy'`).
* **feat(currency):** Deployed the `currency` dimension module supporting major Fiat and Cryptocurrencies. Engineered a **Smart FX Resolver** via `CtxProxy` that automatically detects and mathematically routes both Direct (e.g., `eur_to_usd`) and Inverse (e.g., `usd_to_idr`) exchange rate quotes dynamically at runtime, entirely bypassing floating-point drift.
* **feat(electromagnetism):** Added comprehensive electrical dimensions:
  * `electric_charge` (Coulomb, AmpereHour)
  * `electric_current` (Ampere)
  * `electric_potential` (Volt)
  * `electrical_capacitance` (Farad)
  * `electrical_resistance` (Ohm)
* **feat(photometry):** Added optics and lighting dimensions:
  * `luminous_flux` (Lumen)
  * `illuminance` (Lux)
  * `luminous_intensity` (Candela)

---

## [0.2.3] - 2026-03-01

### The Quantum Precision Patch & Enterprise DX
- **fix(engine):** Removed the default `prec=9` truncation from the core `_PhaethonEngine`. The physics engine now retains absolute native `float64` precision during internal calculations. This resolves an underflow bug where microscopic quantum values (e.g., `eV` to Joules) or astronomical scales were incorrectly truncated to `0.0`.
- **fix(mass):** Corrected the symbol for Planck Mass from the standard proton notation (`m_p`) to the correct scientific notation (`m_P`).
- **fix(mass):** Removed `"gr"` from the `Gram` alias registry to prevent semantic collisions with `Grain`.
- **feat(typing):** Upgraded `registry.py` with strict `Type['BaseUnit']` forward references and `@overload` typing for methods like `unitsin()`. This unlocks full IDE autocomplete (IntelliSense) for dynamically resolved unit classes, massively improving Developer Experience (DX).
- **test(benchmarks):** Introduced `test_pint_parity.py` to the public repository. Utilizing property-based testing (`hypothesis`), Phaethon has empirically achieved 100% mathematical parity against the `Pint` library across 300+ randomized extreme-value conversions, whilst successfully parsing 65+ specialized units that Pint natively fails to process.

---

## [0.2.2] - 2026-02-28

### The Rebrand Hotfix & Documentation Overhaul
- **refactor(core):** Completely purged all legacy "Chisa" zombie references from the internal codebase, class names (e.g., `PhaethonEngine`), docstrings, and print statements.
- **docs(readme):** Updated the main `README.md` and `advanced_physics.md` to fully reflect the new Phaethon namespace and `ptn` import alias conventions.
- **docs(examples):** Renamed and refactored all Google Colab interactive notebooks and Python scripts in the `examples/` directory to utilize the new architecture.
- **ci(actions):** Introduced fully automated PyPI Trusted Publishing (OIDC) via GitHub Actions (`publish.yml`).

---

## [0.2.1] - 2026-02-27

### The Namespace Takeover
- **chore(rebrand):** The package has been globally renamed to `phaethon` on PyPI. The legacy `chisa` package has been deprecated. All current and future development, including the vectorization engine and declarative schemas, will exclusively continue under the Phaethon namespace.
- **feat(alias):** Established `ptn` as the official, standardized import alias (e.g., `import phaethon as ptn`). This explicitly prevents namespace collisions and ensures rapid, phonetic developer typing without overlapping with existing tools like PyTorch (`pt`) or Matplotlib (`plt`).

### Core Engine Continuity
- **refactor(migration):** Successfully migrated 100% of the core Axiom Engine, Metaclass Algebra, and Vectorization logic from the v0.2.0 build into the new Phaethon core. All DataFrame normalization speeds (~0.046 seconds per 100k rows) remain perfectly intact.

---

## [0.2.0] - 2026-02-26

### (Legacy Chisa) Evolution: Unit-Safe Data Pipeline Schema
Chisa has officially evolved its primary identity from a "Physics Modelling Framework" to a **"Unit-Safe Data Pipeline Schema"**. The focus is now heavily geared towards Data Engineering, rescuing tabular data pipelines from the nightmare of mixed units, bizarre abbreviations, and impossible physical values.

###  Major Feature: Declarative Data Schemas
- **feat(schema):** Introduced `chisa.Schema` and `chisa.Field` for strict, declarative data normalization. 
  - Allows Data Engineers to ingest messy, heterogeneous Pandas DataFrames and convert them into clean, dimensionally-validated datasets natively.
- **feat(integration):** Officially elevated **Pandas** (`pandas>=2.0.0`) to a core dependency alongside NumPy, unlocking native vectorized Boolean masking and high-speed schema execution.
- **feat(schema):** Added smart metadata management with `keep_unmapped=True` and `drop_raw=True` to seamlessly drop dirty columns while preserving vital pipeline tracking IDs.
- **feat(schema):** Implemented Lifecycle Hooks (`@cs.pre_normalize` and `@cs.post_normalize`) allowing developers to inject custom domain logic directly into the validation flow.
- **feat(parsing):** Massively expanded unit `aliases` across all dimensions to supercharge the `parse_string=True` method, allowing Chisa to autonomously capture and standardize highly irregular textual data.

### Smart Error Intelligence
- **feat(exceptions):** Introduced `NormalizationError`. Data pipelines no longer just crash silently. When `on_error='raise'` is triggered, Chisa now provides unparalleled Developer Experience (DX) by printing pinpoint debugging context:
  - Exact index of the failure.
  - Expected physical dimension vs. received anomaly.
  - Snippet of the raw dirty string.
  - Actionable suggestions to fix the data or adjust schema rules.

### The Axiom Engine: Metaclass Algebra & Self-Learning Registry
- **feat(metaclass):** Introduced direct Object-Oriented Metaclass Algebra. Users can now synthesize physical laws by directly dividing classes (e.g., `@axiom.derive(u.Kilogram / u.KilowattHour)`). 
- **feat(registry):** Implemented a "Self-Learning" DNA injection mechanism. The `UnitRegistry` now dynamically listens to `__init_subclass__` and autonomously registers new dimensional signatures and custom aliases at runtime.
  - *Impact:* Custom dimensions (like ESG Carbon Metrics) synthesized in scripts are instantly recognized by `Schema.normalize()`, allowing seamless parsing of custom text like `"1000 kgCO2/kWh"`.

### Fluent API Flexibility
- **fix(fluent):** Patched a logic trap in the `convert()` engine's internal `_compute()` method. The Fluent API can now seamlessly handle all four permutations of input targets without crashing: String-to-String (`'km' -> 'm'`), Class-to-String (`u.Kilometer -> 'm'`), String-to-Class (`'km' -> u.Meter`), and Class-to-Class (`u.Kilometer -> u.Meter`).

### Documentation Overhaul
- **docs(readme):** Completely restructured the documentation architecture. 
  - The main `README.md` is now strictly focused on Data Engineering (Schemas, Pipeline Hooks, Vectorization, and Pandas integration).
  - Deep-dive scientific computing features (`@axiom` decorators, `vmath`, `C`, and metaclass architecture) have been cleanly migrated to `docs/advanced_physics.md`.
- **docs(examples):** Completely overhauled the `examples/` directory with 14 brutal, real-world Data Engineering scripts (e.g., Cloud Compute Billing, ESG Carbon Tracking, Sensor Drift Neutralization).
- **docs(notebooks):** Re-architected the interactive Google Colab notebooks. `T01` covers core fundamentals/Schemas, while `T02` provides a masterclass on cleaning a dirty IoT Pandas pipeline, complete with Matplotlib visualization demonstrating the catastrophic impact of unhandled data anomalies.

---

## [0.1.1] - 2026-02-24

### (Legacy Chisa) Core Engine & Type Safety (Hotfix)
- **fix(core):** Standardized native Python `float` (C-level `float64`) as the absolute default for all scalar outputs. 
  - Resolves an inconsistency where scalars could be auto-casted to integers or Decimals, preventing unexpected `TypeError` crashes when integrating with external ML libraries (e.g., SciPy, Scikit-Learn).
- **fix(fluent):** Removed the redundant `exact` format option from the Fluent API's `.use(format=...)` method.
  - Decimal extraction is now strictly explicitly opt-in. Users must initialize with a `Decimal` object (e.g., `Meter(Decimal('10'))`) or use `.use(mode='decimal')` to trigger audit-level precision.

### Documentation & Ecosystem
- **docs(examples):** Added a comprehensive suite of 15 standalone Python scripts in the `examples/` directory demonstrating the full capability of the Axiom Engine, Custom Domains, and Error Handling.
- **docs(notebooks):** Introduced interactive Jupyter Notebooks (`T01_Chisa_Fundamentals.ipynb` and `T02_Chisa_RealWorld_Workflow.ipynb`) with direct Google Colab integration for seamless onboarding.
- **feat(integration):** Validated and documented zero-bottleneck integration patterns with the broader Data Science ecosystem, including **Pandas**, **Matplotlib**, **SciPy**, **SymPy**, and **Scikit-Learn**.

---

## [0.1.0] - 2026-02-23

### (Legacy Chisa) Initial Release
Welcome to the first public release of **Chisa**, the logic-driven dimensional algebra and strict physics modeling framework for Python. This inaugural release establishes the foundational Axiom Engine, the Fluent API, native NumPy vectorization, and a robust exception hierarchy.

### Supported Physical Dimensions
Out of the box, Chisa v0.1.0 natively supports and validates 12 core physical dimensions:
`Length`, `Mass`, `Pressure`, `Time`, `Speed`, `Temperature`, `Data`, `Volume`, `Force`, `Energy`, `Power`, and `Area`.

### Initial Features

#### Core Physics Engine (OOP)
- **feat(core):** Introduced `BaseUnit` as the foundational inheritance root for the entire Chisa ecosystem.
    - Provides the standard interface for dimensional algebra, scalar conversions, NumPy vectorization, and fluent formatting.
- **feat(core):** Implemented a highly scalable, multi-tiered OOP architecture for domain-driven physics modeling:
    - **Hierarchy:** `BaseUnit` -> `DimensionUnit` (e.g., `PressureUnit`) -> `ContextUnit` (e.g., `GaugePressureUnit`) -> `Concrete Unit` (e.g., `PSIG`).
    - Empowers developers to build custom units by inheriting base physics laws and injecting behavior via `@axiom` class decorators.
- **feat(core):** Added `.mag` property for mathematical extraction.
    - Strips high-precision Decimals down to standard Python `float` for cross-dimensional physics calculations and ML pipelines.
    - Safely bypasses strings to leave `numpy.ndarray` intact.
- **feat(core):** Added `.exact` property for strict auditing.
    - Preserves absolute precision by returning `decimal.Decimal` for scalars.
    - Throws intentional `TypeError` if mixed with standard floats to prevent precision drift.
- **feat(units):** Added `.flex()` method specifically for `TimeUnit` to handle flexible, context-dependent chronological conversions (e.g., variable days in months/years).

#### The Axiom Ruleset (Metaprogramming)
- **feat(axiom):** Added `@axiom.derive` for dimensional synthesis (e.g., `Watts = Joules / Seconds`).
- **feat(axiom):** Added `@axiom.scale` and `@axiom.shift` for dynamic magnitude manipulation based on runtime context.
- **feat(axiom):** Added `@axiom.bound` to enforce absolute physical limits (e.g., preventing absolute pressure from dropping below a perfect vacuum of 0 Pa).
- **feat(axiom):** Added `@axiom.require` function decorator for strict dimensional argument guarding.
- **feat(axiom):** Added `@axiom.prepare` function decorator to seamlessly intercept, convert, and extract `.mag` from injected unit objects before math execution.

#### The Fluent API
- **feat(fluent):** Introduced `convert()` entry point for highly readable method chaining.
- **feat(fluent):** Added `.to()` for target unit resolution.
- **feat(fluent):** Added `.use()` for configuring calculation constraints (supports `decimal`/`float64` engine modes and UI formatting like `raw`, `verbose`, `tag`).
- **feat(fluent):** Added `.context()` to dynamically inject environmental variables into the Axiom Engine.
- **feat(fluent):** Added `.resolve()` as the chain terminator to strictly execute the transformation pipeline and return the final value.

#### Error Handling & Guardrails
- **feat(exceptions):** Implemented a granular, highly descriptive exception hierarchy inheriting from base `ChisaError`.
    - `DimensionMismatchError`: Intercepts invalid cross-dimensional math operations (e.g., Mass + Length).
    - `AxiomViolationError`: Triggered when physical limits defined by `@axiom.bound` are breached.
    - `ConversionError`: Catches general algorithmic conversion failures.
    - `AmbiguousUnitError`: Prevents context-less conversion of multi-meaning symbols (e.g., 'm' for meter vs. minute).
    - `UnitNotFoundError`: Raised when unregistered or invalid unit aliases are queried.

#### Developer Experience (DX) & Registry
- **feat(registry):** Implemented snappy, NumPy-style root helper methods for registry introspection:
    - `chisa.dimof()`: Resolves the dimension of string aliases, Classes, or Instances.
    - `chisa.dims()`: Lists all active dimensions.
    - `chisa.unitsin()`: Discovers all unit symbols (supports `ascls=True` for Class objects).
    - `chisa.baseof()`: Identifies the absolute computational baseline class for a dimension.
- **feat(utils):** Introduced `CtxProxy` (aliased as `C`) for declarative, lazy-evaluated context variable injection.
- **feat(utils):** Added `chisa.vmath`, a universal math wrapper supporting both scalars and NumPy arrays natively.
- **feat(utils):** Included `chisa.const` housing high-precision physical constants (e.g., `SPEED_OF_LIGHT`, `STEFAN_BOLTZMANN`, `STANDARD_ATMOSPHERE_PA`).

#### Ecosystem & Integrations
- **feat(integration):** Native **NumPy** integration.
    - Added `numpy>=1.26.0` as a strict dependency.
    - Integrated C-struct array bypassing to process millions of data points at native float64 speeds.