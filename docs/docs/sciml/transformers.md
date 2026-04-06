---
seo_type: TechArticle
title: "Physics Transformers & Pi Groups"
description: "Dimensionless feature synthesis for Sci-ML. Extract Buckingham Pi groups via SVD null-space, and scale datasets while preserving physical units."
keywords: "buckingham pi theorem machine learning, synthesize dimensionless features python, svd dimensional analysis, physics-preserving scaler scikit-learn"
---

# Physics-Aware Transformers

In classical machine learning workflows, data preprocessing (scaling, selecting, and engineering features) is mathematically critical for algorithms like Support Vector Machines (SVM) or Neural Networks to converge. However, standard Scikit-Learn transformers destroy physical units, leaving you with raw arrays that are impossible to trace back to reality.

Phaethon bridges this gap. It provides **Meta-Transformers** that safely unequip physical armor for scaling, perfectly restore it upon inversion, and even synthesize completely new dimensionless features using the laws of physics.

---

## The Dimensional Transformer

Machine Learning algorithms often require features to be scaled (e.g., standardizing values to have a mean of 0 and a variance of 1 using `StandardScaler`). 

The `DimensionalTransformer` wraps standard Scikit-Learn scalers. During `transform()`, it safely evaluates your data into dimensionless raw arrays for safe algorithm consumption. Most importantly, it guarantees the exact restoration of the original physical units when you call `inverse_transform()`.

### API Reference

```python
phaethon.ml.DimensionalTransformer(transformer)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">transformer</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseEstimator</span>
  </div>
  <div class="p-desc">The underlying Scikit-Learn scaling algorithm (e.g., <code>StandardScaler</code>, <code>MinMaxScaler</code>, <code>RobustScaler</code>).</div>
</div>

### Example: Safe Standardization & Inversion

```python
from sklearn.preprocessing import StandardScaler
import phaethon.ml as pml
import phaethon.units as u

# Initialize the Physics-Aware Scaler
scaler = pml.DimensionalTransformer(StandardScaler())

# Input data: A temperature array
temperatures = u.Kelvin([[300.0], [310.0], [320.0]])

# 1. Fit and Transform
# The output is mathematically dimensionless for safe ML consumption
X_scaled = scaler.fit_transform(temperatures)

print(type(X_scaled).__name__)
# Output: ndarray

# 2. Inverse Transform
# Phaethon flawlessly resurrects the exact physical unit (Kelvin)!
X_restored = scaler.inverse_transform(X_scaled)

print(X_restored)
# Output: <Kelvin Array: [[300.] [310.] [320.]]>
```

---

## Dimensional Feature Selector

In industrial datasets, you often have a mix of valid physical sensor readings (Temperature, Pressure) and non-physical metadata (e.g., Sensor IDs, dimensionless error codes, raw string arrays). Feeding non-physical metadata into a predictive physics model can cause severe overfitting.

The `DimensionalFeatureSelector` scans your dataset pipeline and forcefully drops any feature that lacks a valid physical dimension.

### API Reference

```python
phaethon.ml.DimensionalFeatureSelector(strict_physics=True)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">strict_physics</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If True, explicitly drops dimensionless and anonymous features, only allowing formally registered physical dimensions to pass. If False, allows them to pass through. Defaults to True.</div>
</div>

### Example: Filtering a Pipeline

```python
import phaethon.ml as pml
import phaethon.units as u
import numpy as np

selector = pml.DimensionalFeatureSelector(strict_physics=True)

# A mixed pipeline sequence:
# 1. Valid Physics (Speed)
# 2. Valid Physics (Length)
# 3. Non-Physical Noise (Raw ID array)
X_mixed = [
    u.MeterPerSecond([10, 20]), 
    u.Meter([5, 10]), 
    np.array([991, 992]) 
]

# The selector filters the sequence
X_clean = selector.fit_transform(X_mixed)

print(len(X_clean))
# Output: 2

print(X_clean[0].dimension)
# Output: 'speed'
```

---

## Buckingham Transformer



This is the crown jewel of Phaethon's Classic SciML. 

The Buckingham Pi Theorem states that any physical equation can be rewritten in terms of dimensionless groups (Pi groups). In Machine Learning, training a model on dimensionless groups (like Reynolds Number or Mach Number) instead of raw variables (like velocity and density) drastically improves the model's accuracy, convergence speed, and scale-invariance.

The `BuckinghamTransformer` evaluates a sequence of physical variables, extracts their dimensional signatures, and utilizes **Singular Value Decomposition (SVD)** to mathematically synthesize highly predictive, purely dimensionless groups on-the-fly.

### API Reference

```python
phaethon.ml.BuckinghamTransformer(tolerance=1e-5)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">tolerance</span>
    <span class="p-sep">—</span>
    <span class="p-type">float</span>
  </div>
  <div class="p-desc">The singular value threshold for determining the rank of the dimensional matrix during SVD. Defaults to 1e-5.</div>
</div>

### Example: Discovering the Reynolds Number

In this example, we provide four fundamental fluid properties. The transformer will discover their dimensional null-space and synthesize a dimensionless array (which happens to be the Reynolds Number equation) ready for an XGBoost or Random Forest model.

```python
import phaethon.ml as pml
import phaethon.units as u

# Initialize the automated feature engineer
pi_extractor = pml.BuckinghamTransformer()

# 1. Provide raw physical variables from your dataset
velocity = u.MeterPerSecond([10.0, 15.0])
diameter = u.Meter([0.5, 0.5])
density = u.KilogramPerCubicMeter([1000.0, 1000.0])
viscosity = u.PascalSecond([0.001, 0.001])

# We pass them as a sequence of features
X_features = [velocity, diameter, density, viscosity]

# 2. Extract and Transform
# The engine synthesizes the Pi groups and collapses them into raw arrays
dimensionless_groups = pi_extractor.fit_transform(X_features)

print(type(dimensionless_groups).__name__)
# Output: ndarray

print(dimensionless_groups.shape)
# Output: (2, 1) - 2 samples, 1 synthesized dimensionless feature!

# If you inspect the raw values, you will see it perfectly calculated:
# (Velocity * Diameter * Density) / Viscosity
print(dimensionless_groups)
# Output: [[5000000.] [7500000.]]
```

### The "Void Collapse" Guardrail

If you provide variables that **cannot** mathematically cancel each other out (e.g., you provide Velocity, Length, and Density, but forget to provide Viscosity to cancel the Mass dimension), the SVD engine will detect that the dimensional matrix lacks a valid null space.

Phaethon will instantly halt execution and raise an `AxiomViolationError`, preventing your pipeline from generating hallucinated, non-physical features.