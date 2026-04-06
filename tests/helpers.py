"""Shared test fixtures: custom units, ontologies, and semantic states."""

import phaethon as ptn
import phaethon.units as u


# ---------------------------------------------------------------------------
# Custom physical units
# ---------------------------------------------------------------------------

class Quintal(u.MassUnit):
    """One quintal equals 100 kg."""
    symbol = "q"
    base_multiplier = 100.0
    __axiom_min__ = 0.0


class Engagement(u.BaseUnit):
    dimension = "social_engagement"


class View(Engagement):
    symbol = "views"
    aliases = ["view", "v"]
    base_multiplier = 1.0


class KiloView(Engagement):
    symbol = "k_views"
    aliases = ["k views", "ribu views"]
    base_multiplier = 1000.0


# ---------------------------------------------------------------------------
# Ontologies
# ---------------------------------------------------------------------------

class DeviceType(ptn.Ontology):
    SENSOR = ptn.Concept(aliases=["sn", "sensr", "sensor_node"])
    GATEWAY = ptn.Concept(aliases=["gw", "gate way", "hub"])


class ProductType(ptn.Ontology):
    laptop = ptn.Concept()
    smartphone = ptn.Concept()
    tablet = ptn.Concept(aliases=["ipad", "tab"])


# ---------------------------------------------------------------------------
# Semantic states
# ---------------------------------------------------------------------------

class PowerStatus(ptn.SemanticState):
    LOW = ptn.Condition(u.Watt, max=10.0)
    NORMAL = ptn.Condition(u.Watt, min=10.01, max=50.0)
    HIGH = ptn.Condition(u.Watt, min=50.01)


# ---------------------------------------------------------------------------
# Shared schemas
# ---------------------------------------------------------------------------

class IoTEdgeSchema(ptn.Schema):
    device: DeviceType = ptn.Field(
        "raw_dev", fuzzy_match=True, confidence=0.80, impute_by="UNREGISTERED"
    )
    status: PowerStatus = ptn.Field("raw_power", parse_string=True)