"""
Quantum Mechanics and Photometry Extensions Module.
"""
from ..base import BaseUnit
from .. import axioms as _axiom
from .energy import Joule, Electronvolt
from .scalar import Photon
from .time import Second

class PhotonEnergyUnit(BaseUnit):
    """Measures the energy of a single discrete quantum of light."""
    dimension = "photon_energy"

@_axiom.derive(Joule / Photon)
class JoulePerPhoton(PhotonEnergyUnit):
    __base_unit__ = True
    symbol = "J/γ"
    aliases = ["joule_per_photon"]

@_axiom.derive(Electronvolt / Photon)
class ElectronVoltPerPhoton(PhotonEnergyUnit):
    symbol = "eV/γ"
    aliases = ["ev_per_photon", "electronvolt_per_photon"]

@_axiom.bound(abstract=True)
class ActionUnit(BaseUnit):
    __exclusive_domain__ = True
    dimension = "action"

@_axiom.derive(Joule * Second)
class JouleSecond(ActionUnit):
    __base_unit__ = True
    symbol = "J·s"