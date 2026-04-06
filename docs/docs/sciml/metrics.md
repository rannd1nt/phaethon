---
seo_type: TechArticle
title: "Physics-Aware Metrics: MAE, MSE, R²"
description: "Strict physics metrics for Sci-ML evaluation. Absolute error preserves units, squared error synthesizes derived dimensions, and R² remains dimensionless."
keywords: "physics-aware machine learning metrics, mean squared error physical dimensions, calculate R2 with units, strict evaluation metrics python"
---

# Physics-Aware Metrics

Evaluating a machine learning model involves calculating the mathematical distance between its predictions (`y_pred`) and the ground truth (`y_true`). 

Standard Scikit-Learn metrics (`mean_squared_error`, `mean_absolute_error`) are mathematically blind. If you accidentally evaluate a model predicting Speed (m/s) against a ground truth of Acceleration (m/s²), standard metrics will silently subtract the raw arrays and return a floating-point score. The model will appear to have converged, but the entire evaluation is physically invalid.

Phaethon intercepts this evaluation phase. It forensically inspects the physical DNA of the predictions and targets, computes the error using optimized Cython backends, and synthesizes the final error metric into a perfectly dimensioned `BaseUnit`.

---

## The Evaluation Guardrail

Every metric in the `phaethon.ml` module routes its inputs through a strict validation engine before reaching Scikit-Learn. 

If the dimensions of `y_true` and `y_pred` do not perfectly align, Phaethon halts the evaluation and throws a `PhysicalAlgebraError`, logging the exact SI DNA of the mismatched operands to prevent silent evaluation failures.

```text
PhysicalAlgebraError: Metric Evaluation (y_true vs y_pred) failed due to incompatible physical dimensions.
  Left operand  : speed [m/s]
  Right operand : acceleration [m/s²]
```

---

## Mean Absolute Error (MAE)



The Mean Absolute Error calculates the average absolute distance between the predictions and the targets. Because it is an absolute difference, the resulting error metric retains the exact physical dimension of the target variable.

### API Reference

```python
phaethon.ml.physics_mean_absolute_error(
    y_true, 
    y_pred, 
    **kwargs
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">y_true</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">The ground truth (correct) target values.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">y_pred</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit | ndarray</span>
  </div>
  <div class="p-desc">The estimated target values returned by your estimator.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">**kwargs</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Additional arguments passed natively to <code>sklearn.metrics.mean_absolute_error</code> (e.g., <code>sample_weight</code>).</div>
</div>

### Example: Temperature Error

```python
import phaethon.ml as pml
import phaethon.units as u

# Ground truth temperature data
y_true = u.Kelvin([300.0, 310.0, 320.0])

# Model predictions
y_pred = u.Kelvin([305.0, 310.0, 315.0])

# Calculate the MAE
error = pml.physics_mean_absolute_error(y_true, y_pred)

print(error.dimension)
# Output: 'temperature'

print(repr(error))
# Output: <Kelvin: 3.3333 K>
```

---

## Mean Squared Error (MSE / RMSE)

Evaluating the squared error introduces a fascinating dynamic in dimensional algebra. When you square a physical difference, the dimension itself must be squared. If you calculate the MSE of a Distance prediction, the resulting error is physically measured in Area.

Phaethon natively handles this dimensional synthesis. It dynamically computes the squared dimension for MSE, or preserves the original dimension if you opt for the Root Mean Squared Error (RMSE).

### API Reference

```python
phaethon.ml.physics_mean_squared_error(
    y_true,
    y_pred,
    squared=True, 
    **kwargs
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">y_true</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">The ground truth target values.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">y_pred</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit | ndarray</span>
  </div>
  <div class="p-desc">The predicted target values.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">squared</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If True, returns MSE (synthesizes squared dimensions). If False, returns RMSE (preserves the original dimension). Defaults to True.</div>
</div>

### Example: Dimensional Synthesis

```python
import phaethon.ml as pml
import phaethon.units as u

y_true = u.Meter([10.0, 20.0])
y_pred = u.Meter([12.0, 18.0])

# 1. Mean Squared Error (Squared = True)
# Phaethon squares the unit: Meter -> Area
mse = pml.physics_mean_squared_error(y_true, y_pred, squared=True)

print(mse.dimension)
# Output: 'area'
print(repr(mse))
# Output: <Derived_Meter_pow_2: 4.0 m²>

# 2. Root Mean Squared Error (Squared = False)
# Phaethon preserves the linear unit: Meter -> Meter
rmse = pml.physics_mean_squared_error(y_true, y_pred, squared=False)

print(rmse.dimension)
# Output: 'length'
print(repr(rmse))
# Output: <Meter: 2.0 m>
```

---

## R-Squared (Coefficient of Determination)

The R-Squared score represents the proportion of the variance in the dependent variable that is predictable from the independent variable. 

Because it is a ratio of variances (Variance of Error / Variance of Target), the physical dimensions mathematically cancel each other out. Therefore, Phaethon correctly returns the R-Squared score as a strict, dimensionless Python `float`.

### API Reference

```python
phaethon.ml.physics_r2_score(
    y_true, 
    y_pred, 
    **kwargs
)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">y_true</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit</span>
  </div>
  <div class="p-desc">The ground truth target values.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">y_pred</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit | ndarray</span>
  </div>
  <div class="p-desc">The predicted target values.</div>
</div>

### Example: Dimensionless Ratios

```python
import phaethon.ml as pml
import phaethon.units as u

y_true = u.Joule([3.0, -0.5, 2.0, 7.0])
y_pred = u.Joule([2.5, 0.0, 2.0, 8.0])

# Calculate the R-Squared Score
score = pml.physics_r2_score(y_true, y_pred)

# The result is a raw, dimensionless float
print(type(score).__name__)
# Output: float

print(round(score, 3))
# Output: 0.949
```