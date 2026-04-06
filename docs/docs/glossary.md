---
seo_type: TechArticle
title: "Glossary: Scientific Computing Terms"
description: "Official definitions for Phaethon's physics and Sci-ML concepts: Isomorphic Firewalls, Phantom Units, Dimensional Collapse, PTensor, and Context Proxies."
keywords: "physics-constrained scientific computing terminology, isomorphic firewall definition, what is a phantom unit, dimensional collapse physics, PINNs terminology"
---

# Glossary of Terms

Phaethon introduces several exclusive concepts and architectural paradigms to bridge strict dimensional algebra, hybrid data engineering, and high-performance machine learning. This glossary defines the core terminology used throughout the framework.

---

### Axiom
A strict mathematical or physical law applied to a dimension or unit via decorators (`@axiom`). Axioms govern absolute minimum/maximum boundaries (e.g., Absolute Zero), contextual environmental scaling, or logarithmic behaviors.

### Axiom Violation
An error triggered when a physical law or constraint is breached. This can occur during direct instantiation (e.g., attempting to create a negative mass), during a mathematical operation that forces a value outside of its boundaries, or during tabular data ingestion.

### AxiomValidator
A physics-enforcement meta-estimator in Classic SciML. It wraps trained dimensional estimators and intercepts their outgoing predictions. If the algorithm mathematically extrapolates into impossible physical territories (like predicting negative absolute temperature), it forcefully clips the magnitude to the nearest valid physical boundary.

### Base Converter / Linearizer (`~`)
The absolute canonical scale converter triggered by the bitwise NOT operator (`~`). It unrolls derived multipliers, physical constants, or logarithmic shells directly into their primary SI Base Unit, while strictly **preserving** their semantic domain. It is the primary tool for instantly linearizing logarithmic physics.
```python
# Preserves the semantic domain (Torque) while normalizing the scale
torque = u.NewtonMeter(100)
torque = u.NewtonMeter(100)
print(~torque) # 100.0 N·m
```

### BaseUnit
The foundational core class from which all physical dimensions and unit classes inherit. It acts as a highly optimized NumPy proxy, handling C-API interception, memory layout, and the universal properties (like `.mag` and `.dimension`) for all physical tensors.

### BuckinghamTransformer
An automated feature engineering transformer powered by the Buckingham Pi Theorem. It evaluates physical variables and utilizes Singular Value Decomposition (SVD) to discover their dimensional null space, mathematically synthesizing highly predictive, dimensionless groups (e.g., Reynolds Number) on-the-fly for machine learning.

### Collocation Points
Randomized points scattered across a continuous spatial and temporal domain used in Physics-Informed Neural Networks (PINNs). At each point, the neural network evaluates the PDE residuals, allowing it to learn fluid or thermodynamic dynamics without requiring explicitly labeled training data.

### Concept
A discrete vocabulary entity defined within an `Ontology`. It contains a list of explicit or auto-generated aliases used by the C++ RapidFuzz engine to clean and map dirty string categories into a single, canonical label.

### Condition
A bounding rule within a `SemanticState` that maps a specific physical magnitude range to a discrete category. Conditions strictly enforce a `target_unit` to ensure raw data is mathematically converted before evaluation.

### Core Extractor / De-Phantomizer (`.si`)
The semantic escape hatch. Unlike the Base Converter, the Core Extractor explicitly attacks the **DNA** of a unit. It strips away all Phantom Units and shatters Exclusive Domain Locks, downgrading the entity to its pure, generic SI blank canvas.

### CtxProxy (`C`)
A deferred mathematical expression used within contextual axioms (like `@axiom.shift` or `@axiom.scale`). It allows a unit class to dynamically read from the runtime environment (via `phaethon.using`) only at the exact moment of instantiation.

### Dataset
A unified, zero-overhead columnar data structure bridging Data Engineering and Deep Learning. It holds continuous physics (`PTensor` or `BaseUnit`) and discrete semantic arrays side-by-side, allowing instant extraction into NumPy or PyTorch backends.

### Derive (`@axiom.derive`)
A class decorator used to declare and register a new concrete unit by synthesizing it from a mathematical formula of existing units. It automatically calculates the exact SI `base_multiplier` and dimensional DNA.
```python
@ptn.axiom.derive(u.Joule / u.Second)
class Watt(PowerUnit):
    symbol = "W"
```

### DerivedField
A schema component that synthesizes entirely new machine learning features during data ingestion using cross-column dimensional algebra. It builds deferred Abstract Syntax Trees (AST) evaluated securely via Pandas/Polars vectorized math.

### Differential Calculus Engine
Phaethon's physics-aware wrapper around PyTorch's `autograd`. It computes derivatives (like gradients, Laplacians, divergence, and curl) across the continuous domain while automatically inferring and synthesizing the derived physical units (e.g., Position over Time automatically yields Velocity).

### Dimensional Class
An abstract, intermediate class inheriting directly from `BaseUnit` (e.g., `EquivalentDoseUnit`, `PressureUnit`). It represents a specific physical dimension, hosts boundary constraints (`@axiom.bound`), and houses domain-specific methods (like `.wrap()` for angles). By convention, they are named with the `Unit` suffix.

### Dimensional Collapse
A mathematical phenomenon where an algebraic operation perfectly cancels out all physical dimensions, resulting in a pure, dimensionless scalar object (multiplier = 1.0).

### DimensionalEstimator
A Scikit-Learn meta-estimator that wraps classical machine learning algorithms. It automatically infers training dimensions, safely strips physical units for high-speed C/Cython computation, and flawlessly resurrects the exact physical units on the final predictions.

### DimensionalFeatureSelector
A transformer that scans a dataset pipeline and forcefully drops any feature that lacks a valid physical dimension (e.g., naked arrays or raw string IDs), protecting machine learning models from overfitting on non-physical, spurious metadata.

### Dimensional Inversion
The mathematical inversion of a physical unit's dimensional signature (e.g., transforming Time to Frequency). Phaethon automatically executes this inversion when transforming tensors into the spectral domain via Fast Fourier Transform (`pnn.fft`).

### Dimensional Synthesis (Dynamic Synthesis)
The core algebraic engine capability. When mathematical operations occur between different units, Phaethon dynamically combines their signatures. If the result matches a known concept, it casts to it. If unregistered, it synthesizes an anonymous physical class on-the-fly to preserve the DNA.

### DimensionalTransformer
A meta-transformer that wraps standard Scikit-Learn scalers (like `StandardScaler`). It safely standardizes physical tensors into dimensionless arrays for algorithmic consumption, and guarantees exact dimensional restoration upon inverse transformation.

### Equation Balance Guardrail
A strict fail-safe within `ResidualLoss` that forensically inspects the SI DNA of both the PDE residual and the target state. If the dimensions do not match perfectly, training is immediately halted to prevent the neural network from minimizing a physically nonsensical equation.

### Exclusive Domain Lock
A strict quarantine mechanism (`__exclusive_domain__ = True`) placed on highly specialized dimensional classes. It prevents direct casting or interaction between boundaries that share identical mathematical SI foundations but imply drastically different physical behaviors (e.g., Macroscopic Energy vs. Torque).

### Field
The workhorse of the Phaethon `Schema`. It defines the extraction logic, physical boundaries, error handling policies (`coerce`, `clip`, `raise`), and imputation strategies for a single tabular column.

### Hybrid Tabular Schema
A declarative data engineering engine utilizing a dual-engine architecture. It integrates seamlessly with Pandas and Polars, routing string extraction through a dedicated Rust parser to normalize messy tabular data into strict physical dimensions at extreme speeds.

### Isomorphic Firewall
A security architecture that isolates parallel dimensional branches sharing the exact same pure SI baseline. By utilizing Phantom Units, the firewall prevents mathematically identical but conceptually distinct dimensions (like Frequency and Radioactivity, both `1/Second`) from merging or colliding.

### Logarithmic / Non-Linear Algebra
The engine's native capability to handle non-linear unit scales (like Decibels or pH). Phaethon inherently intercepts standard mathematical operators, implicitly drops inputs to their linear counterparts for addition/subtraction, and strictly blocks illegal operations (like exponentiation or modulo) on logarithmic units.

### Loss Tribunals
Physics-informed loss functions (`AxiomLoss` and `ResidualLoss`) in the `phaethon.pinns` module. They allow mathematically invalid or impossible predictions to pass through the forward pass, only to translate the physical violations into massive penalty gradients during backpropagation, teaching the AI to respect natural laws.

### Meta-Estimators & Meta-Transformers
Architectural wrappers in Classic SciML designed to bridge dimensionally blind C/Cython backends (like Scikit-Learn) with Phaethon's dimensional algebra. They safely strip units before computation and resurrect them afterward without data leakage.

### Metaclass-Driven Engine
The underlying architectural design of Phaethon. Instead of standard static classes, physical dimensions are executable objects. The Metaclass (`_PhaethonUnitMeta`) evaluates algebraic operations at runtime, dynamically creating and caching new derived classes to track mathematical signatures without overhead.

### Neural Assembly
The final gateway function (`pnn.assemble`) before physical data enters a standard PyTorch `nn.Module`. It enforces standardization via `.asunit()`, safely strips physics metadata, and concatenates heterogeneous `PTensor` objects into a single raw computational feature block.

### Ontology
A categorical mapping mechanism for fuzzy semantics. It utilizes the C++ RapidFuzz library to calculate Levenshtein distances, cleaning and mapping dirty string categories (typos, variations) into strictly defined canonical `Concepts`.

### Phaethon Archive (`.phx`)
The native secure serialization format for Phaethon Datasets. It is a compressed ZIP archive containing binary `.npy` arrays alongside a cryptographic `metadata.json`. When loaded, the engine validates SHA-256 signatures to guarantee the data has not been corrupted or maliciously tampered with.

### Phantom Collision
A `SemanticMismatchError` triggered when the Isomorphic Firewall is breached. It occurs when two units share identical SI DNA but attempt an illegal interaction across their differing Phantom Units (e.g., attempting to add `Hertz` and `Becquerel` directly).

### Phantom Unit
A non-dimensional entity (mathematically equal to `1`) used by Phaethon to track concepts that standard SI considers dimensionless, such as repeating cycles, radioactive decays, radiation counts, or discrete particles. They act as the structural pillars for Isomorphic Firewalls.

### PTensor
Phaethon Tensor. A strict subclass of `torch.Tensor` injected with physical DNA. It natively evaluates dimensional algebra, maintains physical integrity during matrix operations, and automatically tracks physical units through the computational graph during backpropagation.

### SemanticState
A dynamic physics-to-category classifier. It intercepts continuous physical tabular data (e.g., 150°C), evaluates its magnitude against strict physical `Conditions`, and translates it into a discrete string category (e.g., "OVERHEATING"). During `.astensor()`, these states are automatically factorized into PyTorch integer tensors for `nn.Embedding`.

### Series Proxy
An internal accessor within a Phaethon `Dataset` (e.g., `ds['velocity']`). It allows zero-overhead data extraction into specific formats, dynamically resolving the data into naked NumPy arrays (`.raw`), BaseUnits (`.array`), or autograd-enabled PyTorch tensors (`.tensor`).

### Void Collapse Guardrail
A strict fail-safe within the `BuckinghamTransformer`. If the provided physical variables cannot mathematically cancel each other out (i.e., an empty dimensional null space), the engine halts execution and raises an `AxiomViolationError` to prevent the generation of hallucinated, non-physical features.

### Zero-Config Auto-Inference
The capability of Phaethon's Meta-Estimators (in Classic SciML) to dynamically read, memorize, and enforce the physical dimensions of training data during the `.fit()` phase, requiring no manual dimensional configuration from the developer.

### Zero-Linear Dilemma
The mathematical impossibility of evaluating `log(0)` (which equals negative infinity). In Phaethon, this occurs when subtracting identical logarithmic units. The framework handles this via strict error policies (`raise`, `coerce`, or `clip`) dictated by the runtime configuration.