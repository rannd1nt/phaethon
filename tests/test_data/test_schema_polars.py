"""Tests for Schema normalization and Semantics with Polars."""

import math
import pytest

import phaethon as ptn
import phaethon.units as u
from tests.helpers import IoTEdgeSchema

try:
    import polars as pl
    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False


@pytest.mark.skipif(not HAS_POLARS, reason="Polars not installed")
def test_string_parsing_coerce_and_raise():
    """Verify Rust string parser with coerce and raise error policies (Polars)."""
    from phaethon.exceptions import AxiomViolationError

    df = pl.DataFrame({
        "brutal_mass": ["1.500,75 kw", "5.000,50", "10,5 kuintal", "-5 kw", "hancur lebur"]
    })

    ptn.config(
        decimal_mark=",",
        thousands_sep=".",
        default_on_error="coerce",
        aliases={"q": ["kw", "kuintal"]},
    )

    class CoerceSchema(ptn.Schema):
        mass_kg: u.Kilogram = ptn.Field(
            "brutal_mass", source_unit=u.Kilogram, parse_string=True
        )

    result_coerce = CoerceSchema.normalize(df)
    assert result_coerce["mass_kg"][0] == 150075.0
    val = result_coerce["mass_kg"][3]
    assert val is None or math.isnan(val)

    ptn.config(decimal_mark=",", thousands_sep=",", default_on_error="raise")

    class RaiseSchema(ptn.Schema):
        mass_kg: u.Kilogram = ptn.Field(
            "brutal_mass", source_unit=u.Kilogram, parse_string=True
        )

    df_axiom = df.slice(3, 1)
    with pytest.raises(AxiomViolationError):
        RaiseSchema.normalize(df_axiom)


@pytest.mark.skipif(not HAS_POLARS, reason="Polars not installed")
def test_semantics_edge_cases():
    """Verify fuzzy Ontology and SemanticState handle noisy/invalid data correctly (Polars)."""
    import polars as pl

    data = {
        "raw_dev": ["Sensr", "Gate way", "Alien Tech", None],
        "raw_power": ["5 W", "15000 mW", "0.06 kW", "5 kg"],
    }
    result = IoTEdgeSchema.normalize(pl.DataFrame(data))
    assert result["device"][2] == "UNREGISTERED"
    assert result["status"][1] == "NORMAL"
    assert result["status"][3] is None