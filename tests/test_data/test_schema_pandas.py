"""Tests for Schema normalization, Semantics, and DerivedField with Pandas."""

import numpy as np
import pandas as pd
import pytest

import phaethon as ptn
import phaethon.units as u
from tests.helpers import DeviceType, IoTEdgeSchema, ProductType, View


def test_outlier_detection():
    """Verify outlier_std coerces statistical anomalies to NaN."""
    np.random.seed(42)
    data = list(np.random.normal(60.0, 5.0, 100)) + [5000.0]
    df = pd.DataFrame({"weight": data})

    class OutlierSchema(ptn.Schema):
        w: u.Kilogram = ptn.Field(
            "weight", source_unit=u.Kilogram, outlier_std=3.0, on_error="coerce"
        )

    result = OutlierSchema.normalize(df)
    assert pd.isna(result["w"].iloc[100])
    assert not pd.isna(result["w"].iloc[0])


def test_imputation_strategies():
    """Verify mean, ffill, and constant imputation strategies."""
    df = pd.DataFrame({
        "col_mean": [10.0, 20.0, np.nan],
        "col_ffill": [5.0, np.nan, np.nan],
        "col_const": [100.0, np.nan, 200.0],
    })

    class ImputeSchema(ptn.Schema):
        c1: u.Meter = ptn.Field("col_mean", source_unit=u.Meter, impute_by="mean")
        c2: u.Meter = ptn.Field("col_ffill", source_unit=u.Meter, impute_by="ffill")
        c3: u.Meter = ptn.Field("col_const", source_unit=u.Meter, impute_by="50 m")

    result = ImputeSchema.normalize(df)
    assert result["c1"].iloc[2] == 15.0
    assert result["c2"].iloc[1] == 5.0
    assert result["c3"].iloc[1] == 50.0


def test_string_parsing_coerce_and_raise():
    """Verify Rust string parser with coerce and raise error policies."""
    from phaethon.exceptions import AxiomViolationError

    df = pd.DataFrame({
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
    assert result_coerce["mass_kg"].iloc[0] == 150075.0
    assert pd.isna(result_coerce["mass_kg"].iloc[3])

    ptn.config(decimal_mark=",", thousands_sep=",", default_on_error="raise")

    class RaiseSchema(ptn.Schema):
        mass_kg: u.Kilogram = ptn.Field(
            "brutal_mass", source_unit=u.Kilogram, parse_string=True
        )

    df_axiom = df.iloc[[3]].copy()
    with pytest.raises(AxiomViolationError):
        RaiseSchema.normalize(df_axiom)


def test_local_alias_in_bounds():
    """Verify local aliases work correctly in Field bounds and impute_by parameters."""
    ptn.config(aliases={"q": ["kuintal"]})

    class CargoSchema(ptn.Schema):
        weight: u.Kilogram = ptn.Field(
            "raw_weight",
            parse_string=True,
            min="10 kuintal",
            impute_by="5 kuintal",
            on_error="coerce",
        )

    df = pd.DataFrame({"raw_weight": ["15 kuintal", "5 kuintal", pd.NA]})
    result = CargoSchema.normalize(df)
    assert result["weight"].iloc[0] == 1500.0
    assert result["weight"].iloc[1] == 500.0
    assert result["weight"].iloc[2] == 500.0


def test_lifecycle_hooks():
    """Verify @pre_normalize and @post_normalize hooks execute in correct order."""
    all_traffic = [10000.0, 999999.0, -5000.0]
    df_raw = pd.DataFrame({
        "raw_traffic": [f"{v} views" for v in all_traffic],
        "meta_status": ["  UNPROCESSED  "] * 3,
    })
    df_raw.loc[0, "raw_traffic"] = "15.5 ribu views"  # tests the 'ribu views' alias

    class TrafficSchema(ptn.Schema):
        traffic: View = ptn.Field(
            "raw_traffic",
            parse_string=True,
            outlier_std=3.0,
            impute_by="median",
            on_error="coerce",
            round=0,
        )

        @ptn.pre_normalize
        def strip_metadata(cls, df):
            df["meta_status"] = df["meta_status"].str.strip()
            return df

        @ptn.post_normalize
        def compute_viral_flag(cls, df):
            df["is_viral"] = df["traffic"] > 13000
            df["meta_status"] = "CLEANED"
            return df

    df_clean = TrafficSchema.normalize(df_raw, keep_unmapped=True)
    assert df_clean["traffic"].iloc[0] == 15500
    assert df_clean["meta_status"].iloc[0] == "CLEANED"
    assert "is_viral" in df_clean.columns


def test_semantics_edge_cases():
    """Verify fuzzy Ontology and SemanticState handle noisy/invalid data correctly."""
    data = {
        "raw_dev": ["Sensr", "Gate way", "Alien Tech", None],
        "raw_power": ["5 W", "15000 mW", "0.06 kW", "5 kg"],
    }
    result = IoTEdgeSchema.normalize(pd.DataFrame(data))
    assert result["device"].iloc[2] == "UNREGISTERED"
    assert result["status"].iloc[1] == "NORMAL"
    assert pd.isna(result["status"].iloc[3])


def test_derived_field_synthesis():
    """Verify DerivedField computes cross-column dimensional algebra correctly."""

    class EVBatterySchema(ptn.Schema):
        volts: u.Volt = ptn.Field("raw_v", parse_string=True)
        amps: u.Ampere = ptn.Field("raw_a", parse_string=True)
        power_output: u.Watt = ptn.DerivedField(
            formula=ptn.col("volts") * ptn.col("amps")
        )

    data = {
        "raw_v": ["12 V", "240 V", "400 V"],
        "raw_a": ["50 A", "10 A", "150 A"],
    }
    result = EVBatterySchema.normalize(pd.DataFrame(data))
    assert result["power_output"].iloc[-1] == 60000.0


def test_schema_blueprint_and_options():
    """Verify DeviceType.options() and Schema.blueprint() return correct metadata."""
    ui_options = DeviceType.options()
    assert "SENSOR" in ui_options
    assert "sn" in ui_options["SENSOR"]

    class DocSchema(ptn.Schema):
        dev: DeviceType = ptn.Field("r", fuzzy_match=True)
        v: u.Volt = ptn.Field("v", min=0, max=240)
        p: u.Watt = ptn.DerivedField(formula=ptn.col("v") * 2)

    schema_docs = DocSchema.blueprint()
    assert schema_docs["dev"]["type"] == "Ontology"
    assert schema_docs["v"]["bounds"] == "0 to 240"


def test_ellipsis_field_mapping():
    """Verify ellipsis (...) auto-maps Field source to the attribute name."""

    class InventorySchema(ptn.Schema):
        voltage: u.Volt = ptn.Field(..., parse_string=True, min=0)
        kategori: ProductType = ptn.Field(...)
        power: u.Watt = ptn.DerivedField(formula=ptn.col("voltage") * 2)

    df = pd.DataFrame({
        "voltage": ["220 V", "110 v"],
        "kategori": ["laptop", "ipad"],
    })
    clean_df = InventorySchema.normalize(df)
    assert clean_df["voltage"].iloc[0] == 220.0
    assert clean_df["kategori"].iloc[1] == "tablet"