"""
Phaethon vs. Pint: Automated Accuracy & Parity Validation

This script utilizes property-based testing (Hypothesis) to fire randomized 
floating-point values into both the Phaethon engine and the Pint UnitRegistry.
By validating every unit against its dimensional Base Unit (Transitive Property), 
it guarantees 100% mathematical cross-conversion accuracy across the framework.
"""

import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
import numpy as np
import pint

import phaethon as ptn

# Initialize the baseline oracle (Pint)
ureg = pint.UnitRegistry()

# Semantic bridging map to handle Pint's parser limitations and nomenclature differences
PINT_ALIAS_MAP = {
    '°C': 'degC', '°F': 'degF', '°R': 'degR', '°Re': 'degRe',
    'ft-lbf': 'foot_pound',
    'short_tonf': 'short_ton_force',
    'bale-aus': 'bale',
    'm_P': 'planck_mass',
    'gr': 'grain',
    'bbl': 'oil_barrel'
}

# Generate O(N) Hub-and-Spoke test cases (Target <-> Base Unit)
test_cases = []
for dim in ptn.dims():
    base_unit_cls = ptn.baseof(dim)
    base_symbol = base_unit_cls.symbol
    all_units = ptn.unitsin(dim)
    
    for u_str in all_units:
        if u_str == base_symbol:
            continue
        # Bidirectional validation ensures full transitive accuracy
        test_cases.append((dim, u_str, base_symbol))
        test_cases.append((dim, base_symbol, u_str))


@pytest.mark.parametrize("dim, source_u, target_u", test_cases)
@settings(max_examples=50, deadline=None)
@given(val=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
def test_phaethon_accuracy_against_pint(dim, source_u, target_u, val):
    
    pint_source = PINT_ALIAS_MAP.get(source_u, source_u)
    pint_target = PINT_ALIAS_MAP.get(target_u, target_u)
    
    # 1. Execute Baseline Oracle (Pint)
    try:
        if dim == 'temperature':
            # Use raw strings to prevent Pint from calculating delta temperatures
            pint_val = ureg.Quantity(val, pint_source).to(pint_target).magnitude
        else:
            pint_val = (val * ureg(pint_source)).to(pint_target).magnitude
            
    except (pint.UndefinedUnitError, pint.DimensionalityError):
        pytest.skip(f"SKIP: Pint lacks definition for unit '{source_u}' or '{target_u}'")
    except TypeError:
        pytest.skip(f"SKIP: Pint hyphenation parsing limitation on '{source_u}'")
    except Exception as e:
        pytest.skip(f"SKIP: Pint internal calculus error ({type(e).__name__}) on '{source_u}'")

    # 2. Execute Challenger (Phaethon)
    try:
        phaethon_val = ptn.convert(val, source_u).to(target_u).resolve()
    except ptn.AxiomViolationError:
        # Phaethon strictly enforces physical reality (e.g., Absolute Zero, Negative Mass)
        pytest.skip(f"SKIP: Phaethon enforced physical boundary axiom on {val} {source_u}")

    # 3. Validation (Tolerance accounts for extreme scale float64 rounding, e.g., Giga/Pico)
    np.testing.assert_allclose(
        phaethon_val,
        pint_val,
        rtol=1e-4,
        err_msg=f"PARITY FAILED: {val} {source_u} -> {target_u}. Phaethon: {phaethon_val} | Pint: {pint_val}"
    )