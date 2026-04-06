"""Tests for lazy-loading guards and optional-dependency compatibility."""

import sys
import pytest
from unittest.mock import patch, MagicMock

import phaethon as ptn
import phaethon.units as u
import phaethon.core.schema as schema_mod
import phaethon.core.compat as compat_mod
from phaethon.core.schema import Schema, Field


def test_core_standalone_mode():
    """Schema definition and blueprint must work with all optional deps disabled."""
    with (
        patch("phaethon.core.compat.HAS_TORCH", False),
        patch("phaethon.core.compat.HAS_PANDAS", False),
        patch("phaethon.core.compat.HAS_POLARS", False),
        patch("phaethon.core.compat.HAS_RAPIDFUZZ", False),
    ):
        try:
            class StandaloneSchema(ptn.Schema):
                temperature: u.Kelvin = ptn.Field(source="temp")

            assert "temperature" in StandaloneSchema.__phaethon_fields__
            assert StandaloneSchema.__phaethon_fields__["temperature"].target_unit == u.Kelvin

            info = StandaloneSchema.blueprint()
            assert info["temperature"]["target"] == "Kelvin"
            assert info["temperature"]["type"] == "Physical Dimension"

        except Exception as exc:
            pytest.fail(f"Phaethon core raised an error in standalone mode: {exc}")


def test_astensor_requires_torch():
    """Schema.astensor() must raise ImportError when torch is not installed."""
    with patch.object(compat_mod, "HAS_TORCH", False):
        with pytest.raises(ImportError, match=r"Schema\.astensor\(\) requires PyTorch"):
            schema_mod.Schema.astensor("dummy_dataframe")


def test_astensor_requires_torch_runtime():
    """require_torch() must raise ImportError inside astensor when torch is absent."""
    class TestSchema(Schema):
        weight: u.Kilogram = Field(source="weight")

    mock_df = MagicMock()
    mock_df.columns = ["weight"]

    with patch.object(compat_mod, "HAS_TORCH", False):
        with pytest.raises(ImportError, match=r"Schema\.astensor\(\) requires PyTorch"):
            TestSchema.astensor(mock_df)


def test_normalize_requires_pandas_backend():
    """Schema.normalize() must raise ImportError when Pandas is removed at runtime."""
    class TestSchema(Schema):
        weight: u.Kilogram = Field(source="weight")

    mock_pd_df = MagicMock()

    with patch.dict(sys.modules, {"pandas": None}):
        with patch("phaethon.core.schema.is_pandas_df", return_value=True):
            with pytest.raises(ImportError):
                TestSchema.normalize(mock_pd_df)


def test_schema_execution_guards():
    """normalize() and astensor() must raise ImportError without their required backends."""
    class TargetSchema(ptn.Schema):
        weight: u.Kilogram = ptn.Field()

    mock_df = MagicMock()

    with patch("phaethon.core.compat.SCHEMA_COMPAT", False):
        with pytest.raises(ImportError, match=r"Schema\.normalize\(\) requires Pandas or Polars"):
            TargetSchema.normalize(mock_df)

    with patch("phaethon.core.compat.HAS_TORCH", False):
        with pytest.raises(ImportError, match=r"Schema\.astensor\(\) requires PyTorch"):
            TargetSchema.astensor(mock_df)


def test_pinns_lazy_proxy_guards():
    """Accessing phaethon.pinns attributes must raise ImportError when torch is absent."""
    if "phaethon.pinns" in sys.modules:
        del sys.modules["phaethon.pinns"]

    with patch("phaethon.core.compat.HAS_TORCH", False):
        import phaethon.pinns as pinns

        with pytest.raises(ImportError, match=r"requires PyTorch"):
            _ = pinns.grad

        with pytest.raises(ImportError, match=r"requires PyTorch"):
            _ = pinns.PTensor


def test_ml_lazy_proxy_guards():
    """Accessing phaethon.ml attributes must raise ImportError when sklearn is absent."""
    if "phaethon.ml" in sys.modules:
        del sys.modules["phaethon.ml"]

    with patch("phaethon.core.compat.HAS_SKLEARN", False):
        import phaethon.ml as ml

        with pytest.raises(ImportError, match=r"requires Scikit-Learn"):
            _ = ml.DimensionalEstimator

        with pytest.raises(ImportError, match=r"requires Scikit-Learn"):
            _ = ml.physics_train_test_split