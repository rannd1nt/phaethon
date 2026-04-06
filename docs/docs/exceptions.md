---
seo_type: TechArticle
title: "Exception Reference & Debugging"
description: "Troubleshoot the physics-constrained framework. Understand algebra errors for SI DNA mismatches and equation balance guards for PINN PDE residuals."
keywords: "debug physics informed neural networks, dimension mismatch error python, semantic missmatch error, troubleshoot dimensional algebra, physical algebra error python"
---

# Error Troubleshooting

Phaethon uses a strict hierarchy of exceptions to prevent "Silent Physics Failures." Every error is designed to provide pinpoint debugging context (Forensic Logging), ensuring that mathematical models and data pipelines remain strictly bound to reality.

All custom errors in the framework inherit from the base `PhaethonError` class.

---

## Dimensional & Algebraic Errors

These errors occur when the fundamental laws of physics are violated during mathematical operations or explicit conversions (`.to()`, `.asunit()`). **These are absolute laws and cannot be bypassed** using `phaethon.using()` or global configurations.

### `PhysicalAlgebraError`
Raised when a mathematical operation (`+`, `-`, `==`, `<`, etc.) involves incompatible physical dimensions. Unlike standard dimension errors, this exception maps the exact physical DNA of both operands for quick debugging.

* **Trigger**: Attempting to add `Mass` and `Length`, or comparing `Joule` to `Pascal`.
* **Context**: In physics, addition, subtraction, and comparisons require strict dimensional homogeneity. Phaethon outputs the left and right operands' dimensions or their synthesized anonymous DNA.
* **Output Example**:
  ```text
  PhysicalAlgebraError: Mathematical operation 'sub' failed due to incompatible physical dimensions.
    Left operand  : acceleration [m/s²]
    Right operand : Unregistered DNA [m/(s·m²)]
  ```

### `DimensionMismatchError`
Raised when attempting an explicit casting or conversion across fundamentally incompatible physical dimensions.

* **Trigger**: Calling `.to('pascal')` on a tensor containing Energy (Joules).
* **Context**: The `.to()` and `.asunit()` methods strictly check the dimensional DNA of the tensors. If they do not match, the execution is instantly halted, detailing the expected vs. received dimensions.

### `SemanticMismatchError`
Raised when two units share the exact same SI dimensional DNA, but possess conflicting physical semantics. 

* **Trigger 1 (Phantom Collisions)**: Attempting to convert or add `Hertz` (Cycle) to `Becquerel` (Decay). Both are mathematically `1/Second`, but they represent entirely different physical phenomena.
* **Trigger 2 (Exclusive Domain Locks)**: Attempting to explicitly cast `Joule/kg` directly to `Sievert` (Equivalent Dose). Domain locks require explicit algebraic synthesis, not direct casting.

### `AmbiguousUnitError`
Raised when an input string alias overlaps across multiple dimensions, and the engine lacks the context to resolve it.

* **Trigger**: Instantiating a tensor or calling `.to()` using a completely ambiguous string. For example, `'m'` is registered as an alias for both `Meter` (Length) and `Minute` (Time).
* **Mechanism**: If you run `ptn.convert(1, 'm').to('m')`, it will crash because both sides are ambiguous. However, `ptn.convert(2, 'm').to('km')` succeeds! Why? Because `'km'` is exclusively owned by the Length dimension, giving Phaethon the context it needs to instantly resolve the source `'m'` as `Meter`.
* **Fix**: Provide a contextually clear target unit, or use a more specific alias (e.g., `'meter'` or `'min'`).

---

## SciML & PINNs Errors

These errors are exclusive to the `phaethon.pinns` module, safeguarding Physics-Informed Neural Networks against architecturally broken learning flows.



### `EquationBalanceError`
Raised when a physics-informed loss function receives mismatched dimensions between the computed residual and the target state.

* **Trigger**: Passing an Acceleration tensor to `ResidualLoss` but setting the target as a Velocity tensor.
* **Context**: This prevents the Neural Network from successfully minimizing a mathematically valid but physically nonsensical Partial Differential Equation (PDE).
* **Output Example**:
  ```text
  EquationBalanceError: The PDE residual and target state do not share the same physical dimension.
    Residual : acceleration [m/s²]
    Target   : speed [m/s]
  ```

---

## Pipeline & Guardrail Errors

These errors are related to data ingestion, boundary limits, and schema normalization.

### `AxiomViolationError`
Raised when a scalar value, tensor, or NumPy array violates the strict physical boundaries defined by the `@axiom.bound` decorator (e.g., predicting a negative Absolute Temperature or negative Mass).

* **Mechanism**: In general evaluation, this halts execution. In Neural Networks, `AxiomLoss` safely catches this to generate penalty gradients without crashing the training loop.
* **Fix**: If you are ingesting noisy sensor data that frequently dips below physical limits, do not disable the strictness globally. Instead, change the Error Policy to coerce the bad data into `NaN` using `on_error="coerce"` inside a Schema Field or via the [`phaethon.using()`](physics/config.md/#contextual-overrides) context manager. 

### `NormalizationError`
The ultimate debugging tool for `Schema.normalize()`. It provides a detailed, pinpoint report when tabular string parsing fails.

* **Output Context**: It tells you the exact **Field name**, the problematic **Row Indices** (e.g., `[14, 28, 105]`), the **Expected Dimension**, and provides a **Raw Sample** of the unparseable string.
* **Fix**: Clean the upstream data, register a new alias, or set `Field(on_error='coerce')`.

### `UnitNotFoundError`
Raised when a requested unit symbol or alias is completely unrecognized by the global UnitRegistry.

* **Fix**: Check loaded units via [`phaethon.unitsin()`](utilities.md/#phaethonunitsin), or register the missing unit using the `@ptn.axiom.derive` decorator. You can also add aliases for existing symbols using [`phaethon.config()`](physics/config.md#global-configuration) or [`phaethon.using()`](physics/config.md/#contextual-overrides)

### `ConversionError`
Raised when a conversion calculation fails procedurally within the Fluent API (e.g., attempting to resolve an unbound pipeline without setting a `.to()` target).