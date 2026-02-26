# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-02-26

### Evolution: Unit-Safe Data Pipeline Schema
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

## [0.1.1] - 2026-02-24

### Core Engine & Type Safety (Hotfix)
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