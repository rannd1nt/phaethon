"""Global pytest configuration: auto-use fixtures."""

import pytest
import phaethon as ptn

@pytest.fixture(autouse=True)
def reset_phaethon_config():
    """Reset global Phaethon configuration before and after every test."""
    defaults = dict(
        decimal_mark=".",
        thousands_sep=",",
        default_on_error="raise",
        aliases={},
        context={},
    )
    ptn.config(**defaults)
    yield
    ptn.config(**defaults)