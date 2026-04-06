"""Tests for DimensionalEstimator, AxiomValidator, and physics-aware metrics."""

import numpy as np
import pytest

import phaethon.units as u

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    import phaethon.ml as pml
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@pytest.mark.skipif(not HAS_SKLEARN, reason="Scikit-Learn not installed")
def test_dimensional_estimator_pipeline():
    """End-to-end: DimensionalTransformer → DimensionalEstimator → metrics."""
    X_raw = np.array([[300.0], [310.0], [320.0], [330.0], [340.0]])
    y_raw = X_raw * 2.5 + 50.0

    X_train = u.Kelvin(X_raw)
    y_train = u.Pascal(y_raw)

    scaler = pml.DimensionalTransformer(StandardScaler())
    X_scaled = scaler.fit_transform(X_train)
    assert isinstance(X_scaled, np.ndarray)
    assert not hasattr(X_scaled, "dimension")

    X_restored = scaler.inverse_transform(X_scaled)
    assert X_restored.dimension == "temperature"
    assert np.allclose(X_restored.mag, X_raw)

    model = pml.DimensionalEstimator(LinearRegression())
    model.fit(X_scaled, y_train)

    X_test_raw = np.array([[350.0]])
    X_test_scaled = scaler.transform(u.Kelvin(X_test_raw))
    y_pred = model.predict(X_test_scaled)
    assert y_pred.dimension == "pressure"
    assert np.isclose(y_pred.mag[0, 0], 350.0 * 2.5 + 50.0)

    y_true_eval = u.Pascal(np.array([100.0, 200.0]))
    y_pred_eval = u.Pascal(np.array([90.0, 210.0]))

    mae = pml.physics_mean_absolute_error(y_true_eval, y_pred_eval)
    assert mae.dimension == "pressure"
    assert mae.mag == 10.0

    mse = pml.physics_mean_squared_error(y_true_eval, y_pred_eval, squared=True)
    assert mse.dimension != "pressure"
    assert mse.mag == 100.0

    r2 = pml.physics_r2_score(y_true_eval, y_pred_eval)
    assert isinstance(r2, float)


@pytest.mark.skipif(not HAS_SKLEARN, reason="Scikit-Learn not installed")
def test_estimator_and_metrics_api():
    """Unit test for DimensionalTransformer, DimensionalEstimator, MAE, MSE, RMSE, R²."""
    X_raw = np.array([[10.0], [20.0], [30.0]])
    X_phys = u.Meter(X_raw)

    scaler = pml.DimensionalTransformer(MinMaxScaler())
    X_scaled = scaler.fit_transform(X_phys)
    assert not hasattr(X_scaled, "dimension")

    X_inv = scaler.inverse_transform(X_scaled)
    assert X_inv.dimension == "length"
    assert np.allclose(X_inv.mag, X_raw)

    y_phys = u.Joule(np.array([100.0, 200.0, 300.0]))
    model = pml.DimensionalEstimator(LinearRegression())
    model.fit(X_phys, y_phys)
    y_pred = model.predict(u.Meter([[40.0]]))
    assert y_pred.dimension == "energy"
    assert np.isclose(y_pred.mag[0], 400.0)

    y_true = u.Newton(np.array([10.0, 20.0, 30.0]))
    y_pred_metric = u.Newton(np.array([12.0, 18.0, 30.0]))

    mae = pml.physics_mean_absolute_error(y_true, y_pred_metric)
    assert mae.dimension == "force"
    assert np.isclose(mae.mag, 1.333333)

    mse = pml.physics_mean_squared_error(y_true, y_pred_metric, squared=True)
    assert mse.dimension != "force"
    assert np.isclose(mse.mag, 2.666666)

    rmse = pml.physics_mean_squared_error(y_true, y_pred_metric, squared=False)
    assert rmse.dimension == "force"
    assert np.isclose(rmse.mag, np.sqrt(2.666666))

    r2 = pml.physics_r2_score(y_true, y_pred_metric)
    assert isinstance(r2, float)