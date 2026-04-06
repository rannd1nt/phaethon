"""
The Universal Unit Collection.
-----------------

This module provides access to all built-in dimensional units and base classes
in Phaethon. It aggregates 90 distinct physical, digital, cosmological, and 
financial dimensions into a single, cohesive interface for declarative modeling, 
Sci-ML, and scientific computing.

**Available Dimensional Domains:**

- **Mechanics & Kinematics**
   `acceleration`, `action`, `angular_acceleration`, `angular_momentum`, 
   `angular_velocity`, `force`, `force_per_length`, `jerk`, `length`, `mass`, 
   `moment_of_inertia`, `momentum`, `speed`, `stiffness`, `torque`

- **Thermodynamics & Energy**
   `energy`, `energy_content`, `energy_density`, `entropy`, `heat_flux_density`, 
   `heat_transfer_coefficient`, `power`, `specific_energy`, `specific_heat_capacity`, 
   `temperature`, `thermal_conductivity`, `stefan_boltzmann_constant`

- **Electromagnetism**
   `current_density`, `electric_charge`, `electric_current`, `electric_dipole_moment`, 
   `electric_field`, `electric_potential`, `electrical_capacitance`, 
   `electrical_inductance`, `electrical_permittivity`, `electrical_resistance`, 
   `magnetic_field_strength`, `magnetic_flux`, `magnetic_flux_density`, `specific_charge`

- **Fluids & Viscosity**
   `density`, `dynamic_viscosity`, `kinematic_viscosity`, `mass_flow_rate`, 
   `pressure`, `specific_volume`, `surface_tension`, `volume`, `volumetric_flow_rate`

- **Chemistry & Particles**
   `amount_of_substance`, `catalytic_activity`, `molar_heat_capacity`, 
   `molar_mass`, `molar_volume`, `molarity`, `number_density`

- **Geometry, Waves & Optics**
   `angle`, `area`, `cycle`, `frequency`, `illuminance`, `luminous_flux`, 
   `luminous_intensity`, `photon`, `photon_energy`, `solid_angle`, 
   `spatial_frequency`, `wavenumber`

- **Nuclear & Radiation Physics**
   `absorbed_dose`, `absorbed_dose_rate`, `biological_effect`, `decay`, 
   `equivalent_dose`, `linear_attenuation`, `radiation`, `radiation_exposure`, 
   `radioactivity`

- **Astrophysics & Cosmology**
   `expansion`, `expansion_rate`, `gravitational_parameter`, `spectral_flux_density`

- **Digital, Economics, Rates & Scalars**
   `baud_rate`, `count`, `currency`, `data`, `dimensionless`, `rate`, `symbol`, `time`

Core Concepts
-------------
**Phantom Units & Semantic Isolation**
    In standard SI, entities like `cycle`, `decay`, `radiation`, and `angle` are 
    considered dimensionless (1). Phaethon strict-tracks them as 'Phantom Units'. 
    This preserves physical DNA and prevents meaningless operations, raising a 
    `SemanticMismatchError` if you attempt to add Hertz (cycle/s) to Becquerel 
    (decay/s), despite them sharing the exact same SI core (1/s).

**Exclusive Domain Locks**
    Certain highly specialized domains (e.g., Cosmology, Radiation Dosimetry) are 
    strictly locked. Phaethon forbids casual `.to()` casting into these domains. 
    To cross into an exclusive domain, explicit algebraic synthesis is required 
    (e.g., SpecificEnergy * BiologicalEffect -> EquivalentDose).

**SI Extractor (.si)**
    The `.si` property acts as an escape hatch. It explicitly strips away all 
    Phantom Units and Domain Locks from an entity, gracefully downgrading it to 
    its pure, generic Blank Canvas (e.g., stripping the 'biological_effect' from 
    Sievert to yield generic Specific Energy).

**Base Unit Converter (~)**
    The bitwise NOT operator (`~`) acts as an absolute canonical converter. It 
    translates any derived or scaled unit directly to the primary Base Unit of 
    its dimension (e.g., converting a synthesized 'GravityPerSecond' explicitly 
    into 'MeterPerSecondCubed').

## Examples::

   import phaethon.units as u

   # 1. Standard physical dimensional synthesis
   speed = u.Meter(10) / u.Second(2)
   print(speed)
   # 5.0 m/s

   # 2. Polymorphic Type Checking
   isinstance(speed, u.SpeedUnit)
   # True

   # 3. Context-aware unit and financial conversion
   mach = u.Mach(10, context={'temperature': u.Celsius(2.35)})
   print(mach.to(u.KilometerPerHour))
   # 11977.9952 km/h

   revenue = u.Euro(100, context={"eur_to_usd": 1.10})
   print(revenue.to(u.USDollar))
   # 110.0 USD

   # 4. Dimension Branching via Phantom Synthesis
   E_spec = u.Joule(10) / u.Kilogram(1)
   dose = E_spec * u.BiologicalEffect(2)
   print(dose.dimension)
   # equivalent_dose

   # 5. Semantic Isolation (Phantom Collision)
   u.Hertz(50) + u.Becquerel(50)
   # SemanticMismatchError: Phantom Collision! Cannot add 'frequency' and 'radioactivity'.

   # 6. Escaping Domain Locks via SI Extractor (.si)
   raw_dose = u.Sievert(5).si 
   print(raw_dose.dimension)
   # specific_energy

   # 7. The Base Unit Converter (~)
   jerk_val = u.GravityPerSecond(9)
   print(~jerk_val)
   # 88.25985 m/s³

   # 8. Non-Linear Logarithmic Physics (Addition & Linear Drop)
   # 30 dBm (1W) + 30 dBm (1W) = 2W -> ~33.01 dBm
   total_signal = u.DecibelMilliwatt(30.0) + u.DecibelMilliwatt(30.0)
   print(total_signal)
   # 33.0103 dBm

   linear_power = ~total_signal
   print(linear_power)
   # 2 W
"""

from .core.units.acceleration import *
from .core.units.area import *
from .core.units.astrophysics import *
from .core.units.chemistry import *
from .core.units.currency import *
from .core.units.data import *
from .core.units.density import *
from .core.units.electromagnetism import *
from .core.units.energy import *
from .core.units.fluid import *
from .core.units.force import *
from .core.units.frequency import *
from .core.units.geometry import *
from .core.units.kinematics import *
from .core.units.length import *
from .core.units.mass import *
from .core.units.nuclear import *
from .core.units.photometry import *
from .core.units.power import *
from .core.units.pressure import *
from .core.units.quantum import *
from .core.units.scalar import *
from .core.units.speed import *
from .core.units.temperature import *
from .core.units.thermodynamics import *
from .core.units.time import *
from .core.units.viscosity import *
from .core.units.volume import *
from .core.units.waves import *

