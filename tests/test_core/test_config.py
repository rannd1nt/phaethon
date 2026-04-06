"""Tests for phaethon.config, phaethon.using, and the Fluent API."""

import numpy as np
import pandas as pd

import phaethon as ptn
import phaethon.units as u


def test_decimal_mark_hierarchy():
    """Verify 3-tier decimal mark resolution: field > context > global."""
    df = pd.DataFrame({
        "data_global": ["10,5"],
        "data_context": ["10-5"],
        "data_field": ["10|5"],
    })
    ptn.config(decimal_mark=",", default_on_error="coerce")

    class ConfigSchema(ptn.Schema):
        g: u.Meter = ptn.Field("data_global", source_unit=u.Meter, parse_string=False)
        c: u.Meter = ptn.Field("data_context", source_unit=u.Meter, parse_string=False)
        f: u.Meter = ptn.Field(
            "data_field", source_unit=u.Meter, decimal_mark="|", parse_string=False
        )

    result_global = ConfigSchema.normalize(df)
    assert result_global["g"].iloc[0] == 10.5
    assert result_global["f"].iloc[0] == 10.5

    with ptn.using(decimal_mark="-"):
        result_context = ConfigSchema.normalize(df)
        assert result_context["c"].iloc[0] == 10.5


def test_context_hierarchy_override():
    """Verify Mach conversion respects field > context > global priority for temperature."""
    df = pd.DataFrame({"raw_speed": ["1 mach"]})

    ptn.config(context={"temperature": u.Celsius(0)})

    class GlobalFlightSchema(ptn.Schema):
        speed_ms: u.MeterPerSecond = ptn.Field("raw_speed", parse_string=True)

    assert 331.0 < GlobalFlightSchema.normalize(df)["speed_ms"].iloc[0] < 332.0

    with ptn.using(context={"temperature": u.Celsius(50)}):
        assert 360.0 < GlobalFlightSchema.normalize(df)["speed_ms"].iloc[0] < 361.0

    class FieldFlightSchema(ptn.Schema):
        speed_ms: u.MeterPerSecond = ptn.Field(
            "raw_speed", parse_string=True, context={"temperature": u.Celsius(-50)}
        )

    with ptn.using(context={"temperature": u.Celsius(50)}):
        assert 299.0 < FieldFlightSchema.normalize(df)["speed_ms"].iloc[0] < 300.0


def test_fluent_api_currency_conversion():
    """Verify Fluent API and Schema handle multi-currency conversions correctly."""
    exchange_rates = {
        "eur_to_usd": 1.10,
        "usd_to_jpy": 150.0,
        "usd_to_idr": 16000.0,
    }
    df = pd.DataFrame({
        "raw_amount": ["100 EUR", "1500 JPY", "5 USD", "50000 IDR"]
    })
    expected = np.array([1760000.0, 160000.0, 80000.0, 50000.0])

    class ReportA(ptn.Schema):
        a: u.IndonesianRupiah = ptn.Field(
            "raw_amount", parse_string=True, context=exchange_rates
        )

    np.testing.assert_allclose(ReportA.normalize(df)["a"].values, expected)

    class ReportB(ptn.Schema):
        a: u.IndonesianRupiah = ptn.Field("raw_amount", parse_string=True)

    with ptn.using(context=exchange_rates):
        np.testing.assert_allclose(ReportB.normalize(df)["a"].values, expected)

    fluent_jpy = (
        ptn.convert(1500, "JPY")
        .to("IDR")
        .context(exchange_rates)
        .use(out="raw")
        .resolve()
    )
    assert np.isclose(fluent_jpy, 160000.0)

    fluent_derived = (
        ptn.convert(50, u.Euro / u.Gram)
        .to(u.IndonesianRupiah / u.Kilogram)
        .context(exchange_rates)
        .use(out="raw")
        .resolve()
    )
    assert np.isclose(fluent_derived, 880000000.0)

    idr_obj = u.Euro(100).to(u.IndonesianRupiah, context=exchange_rates)
    assert np.isclose(idr_obj.mag, 1760000.0)


def test_fluent_api_dtype_casting():
    """Verify Fluent API dtype coercion for scalars, lists, and ndarrays."""
    result_scalar = (
        ptn.convert(5.9, "m").to("cm").use(dtype="int32", out="raw").resolve()
    )
    assert isinstance(result_scalar, (int, np.integer))
    assert result_scalar == 590

    result_list = (
        ptn.convert([1, 2.5, 3.9], "m").to("cm").use(dtype="int32", out="raw").resolve()
    )
    assert isinstance(result_list, np.ndarray)
    assert result_list.dtype == np.dtype("int32")
    assert np.array_equal(result_list, [100, 250, 390])

    raw_arr = np.array([10.5, 20.7, 30.1], dtype=np.float64)
    result_arr = (
        ptn.convert(raw_arr, "kg").to("g").use(dtype="float16", out="raw").resolve()
    )
    assert isinstance(result_arr, np.ndarray)
    assert result_arr.dtype == np.float16
    assert result_arr[0] == 10500.0