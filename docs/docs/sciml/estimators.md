---
seo_type: TechArticle
title: "Meta-Estimators & Validations"
description: "Physics-constrained regression. Dimensional estimators provide auto-inference for Scikit-Learn, while validators clip impossible AI predictions."
keywords: "physics-constrained machine learning, scikit-learn dimensional analysis, prevent impossible predictions AI, physics bounds validation"
---

# Meta-Estimators & Workflows

Classical machine learning algorithms in Scikit-Learn (like Random Forest, XGBoost, or Support Vector Machines) are heavily optimized using C/Cython backends. Because of this low-level optimization, they strictly require raw numerical arrays and will crash if fed custom Python objects like physical units.



Phaethon solves this bridging problem through **Meta-Estimators**. These wrappers act as a secure translation bridge: they automatically strip physical units before feeding data into the C/Cython algorithms, and flawlessly resurrect the exact physical dimensions on the outgoing predictions.

---

## Physics-Aware Splitting

Before training a model, data must be split into training and testing sets. If you use the standard `sklearn.model_selection.train_test_split` on Phaethon physical arrays, Scikit-Learn will forcefully degrade your custom units into raw, mathematically blind NumPy arrays.

Phaethon intercepts this process using `physics_train_test_split`.

### API Reference

```python
phaethon.ml.physics_train_test_split(*arrays, **options)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">*arrays</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit | ndarray | list</span>
  </div>
  <div class="p-desc">The physical arrays or matrices to be split.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">**options</span>
    <span class="p-sep">—</span>
    <span class="p-type">kwargs</span>
  </div>
  <div class="p-desc">Standard Scikit-Learn options (e.g., <code>test_size</code>, <code>random_state</code>, <code>shuffle</code>).</div>
</div>

### Example: Preserving Dimensionality

```python
import phaethon as ptn
import phaethon.ml as pml
import phaethon.units as u

# Generate synthetic physical data
X_temperature = u.Kelvin([300.0, 310.0, 320.0, 330.0])
y_pressure = u.Pascal([101325, 102000, 103000, 104000])

# Safely split while preserving physics
X_train, X_test, y_train, y_test = pml.physics_train_test_split(
    X_temperature, y_pressure, test_size=0.5, random_state=42
)

# The resulting splits remain valid Phaethon units!
print(repr(X_test))
# Output: <Kelvin Array: [310. 330.] K>
```

---

## The Dimensional Estimator

The `DimensionalEstimator` is a Scikit-Learn `MetaEstimatorMixin`. It wraps any standard regressor or classifier, automatically infers the physical dimensions of the training data, and structurally restores the exact physical units to the final predictions.

### API Reference

```python
phaethon.ml.DimensionalEstimator(estimator, enforce_target_unit=None)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">estimator</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseEstimator</span>
  </div>
  <div class="p-desc">The core Scikit-Learn machine learning algorithm to be utilized (e.g., <code>RandomForestRegressor</code>, <code>Ridge</code>).</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">enforce_target_unit</span>
    <span class="p-sep">—</span>
    <span class="p-type">type[BaseUnit] | None</span>
  </div>
  <div class="p-desc">An explicit physical unit to strictly enforce on the target variable. If <code>None</code>, the estimator performs Zero-Config Auto-Inference, learning the unit dynamically from the training data.</div>
</div>

### Example 1: Zero-Config Auto-Inference

If you do not specify a target unit, the estimator will memorize the physical dimension of `y` during the `.fit()` phase and apply it during `.predict()`.

```python
from sklearn.linear_model import LinearRegression
import phaethon.ml as pml
import phaethon.units as u
import numpy as np

# Training features (e.g., Area in Square Meters)
# We use a purely linear relationship for clear demonstration
X_train = u.Meter(np.array([[10.0], [20.0], [30.0]]))

# Target variable (e.g., Force in Newtons)
# Notice the perfect linear correlation: Force = 5 * Area
y_train = u.Newton([50.0, 100.0, 150.0])

# Initialize the Physics-Aware Estimator
model = pml.DimensionalEstimator(LinearRegression())

# The model learns that predictions must be in Newtons
model.fit(X_train, y_train)

# Predict new values perfectly
X_test = u.Meter(np.array([[15.0], [25.0]]))
predictions = model.predict(X_test)

print(predictions.dimension)
# Output: 'force'

print(predictions.format(prec=1))
# Output: [75.0, 125.0] N
```

### Example 2: Strict Target Enforcement

In production environments, you may want to guarantee that a pipeline strictly outputs a specific physical unit, regardless of upstream data noise. You can enforce this using the `enforce_target_unit` parameter. 

If upstream data violates this contract, the engine halts execution before contaminating the model.

```python
from sklearn.tree import DecisionTreeRegressor
import phaethon.ml as pml
import phaethon.units as u
import numpy as np

# We strictly mandate that this model MUST predict Energy in Joules
strict_model = pml.DimensionalEstimator(
    DecisionTreeRegressor(), 
    enforce_target_unit=u.Joule
)

X_train = np.array([[1], [2]])

# If a developer accidentally passes Watts (Power) instead of Joules (Energy)...
y_wrong_train = u.Watt([100.0, 200.0])

# Phaethon instantly blocks the training phase!
try:
    strict_model.fit(X_train, y_wrong_train)
except Exception as e:
    print(type(e).__name__)
    # Output: DimensionMismatchError
```

---

## The Axiom Validator

Even with a `DimensionalEstimator`, standard Machine Learning models (like Linear Regression) can mathematically extrapolate into impossible territories—such as predicting a negative mass or an absolute temperature below 0 Kelvin.

The `AxiomValidator` is a powerful meta-estimator that wraps your `DimensionalEstimator`. It intercepts outgoing predictions and forces them to comply with the absolute laws of physics defined in Phaethon's unit registry (via the `@axiom.bound` decorator). It forcefully clips impossible magnitudes to the nearest valid physical boundary.

### API Reference

```python
phaethon.ml.AxiomValidator(estimator)
```

<div class="param-box">
  <div class="param-header">
    <span class="p-name">estimator</span>
    <span class="p-sep">—</span>
    <span class="p-type">DimensionalEstimator</span>
  </div>
  <div class="p-desc">The fitted or unfitted <code>DimensionalEstimator</code> to be validated. It must be an estimator that returns Phaethon BaseUnits.</div>
</div>

### Example: Preventing Impossible Physics

```python
from sklearn.linear_model import LinearRegression
import phaethon.ml as pml
import phaethon.units as u
import numpy as np

# A dataset showing a declining temperature trend
X_time = np.array([[1], [2], [3], [4]])
y_temp = u.Kelvin([300.0, 200.0, 100.0, 0.0])

# Wrap a standard Linear Regression model
base_model = pml.DimensionalEstimator(LinearRegression())

# Wrap it AGAIN with the AxiomValidator for physical safety
safe_model = pml.AxiomValidator(base_model)

safe_model.fit(X_time, y_temp)

# Time step 5 mathematically predicts -100 Kelvin!
X_future = np.array([[5]])

# The AxiomValidator intercepts the impossible prediction 
# and clips it to 0.0 Kelvin (Absolute Zero).
safe_predictions = safe_model.predict(X_future)

print(safe_predictions)
# Output: <Kelvin Array: [0.] K>
```