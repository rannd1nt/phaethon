"""Tests for physics_train_test_split and BuckinghamTransformer."""

import numpy as np
import pytest

import phaethon.units as u

try:
    import phaethon.ml as pml
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@pytest.mark.skipif(not HAS_SKLEARN, reason="Scikit-Learn not installed")
def test_train_test_split_and_buckingham():
    """Verify physics-preserving train/test split and SVD Buckingham Pi synthesis."""
    X_raw = np.arange(10, dtype=float)
    y_raw = np.arange(10, 20, dtype=float)

    X_phys = u.Meter(X_raw)
    y_phys = u.Joule(y_raw)

    result = pml.physics_train_test_split(X_phys, y_phys, test_size=0.2, random_state=42)
    assert len(result) == 4
    X_train, X_test, y_train, y_test = result

    assert isinstance(X_train, u.BaseUnit)
    assert X_train.dimension == "length"
    assert len(X_train.mag) == 8

    assert isinstance(y_test, u.BaseUnit)
    assert y_test.dimension == "energy"
    assert len(y_test.mag) == 2

    v = u.MeterPerSecond(np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
    d = u.Meter(np.array([0.1, 0.1, 0.1, 0.1, 0.1]))
    rho = u.KilogramPerCubicMeter(np.array([1000.0] * 5))
    mu = u.PascalSecond(np.array([0.001] * 5))

    pi_transformer = pml.BuckinghamTransformer()
    X_dimless = pi_transformer.fit_transform([v, d, rho, mu])

    assert isinstance(X_dimless, np.ndarray)
    assert not hasattr(X_dimless, "dimension")
    assert X_dimless.shape[0] == 5
    assert X_dimless.shape[1] == 1

    impossible_transformer = pml.BuckinghamTransformer()
    with pytest.raises(ValueError, match="empty null space"):
        impossible_transformer.fit_transform([u.Meter([1.0]), u.Second([1.0])])