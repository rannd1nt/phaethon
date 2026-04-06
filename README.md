<div align="center">

<h1>Phaethon</h1>

<p>
<img src="https://img.shields.io/badge/MADE_WITH-PYTHON-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/FOUNDATION-NUMPY-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/INTEGRATION-PYTORCH-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
<img src="https://img.shields.io/badge/INTEGRATION-PANDAS-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
<img src="https://img.shields.io/badge/LICENSE-MIT-red?style=for-the-badge" alt="License">
</p>

<p>
<i>The End-to-End Physics-Constrained Scientific Computing & Sci-ML Framework.</i>
</p>

</div>

Phaethon is a Python framework that unifies strict dimensional tensor algebra, Scientific Machine Learning (Sci-ML), and declarative data engineering. It is designed to ensure mathematical and physical integrity from the data ingestion layer to the final neural prediction.

## 📖 Documentation
For complete tutorials, API references, and architectural concepts, visit the official documentation:

📌 **[phaethon.readthedocs.io](https://phaethon.readthedocs.io/)**

---

## ⚡ Core Ecosystem

Phaethon builds directly upon the **NumPy Array Protocol** to operate as a zero-overhead native proxy, extending physical safety to modern ML ecosystems.

1. **Metaclass-Driven Algebra:** Dynamic dimensional synthesis (e.g., `u.Meter / u.Second -> MeterPerSecond`). Inherently evaluates isomorphic firewalls, domain locks, and logarithmic math.
2. **Scientific Compute:** Physics-aware linear algebra (`ptn.linalg`) and strictly bounded stochastic tensor generation (`ptn.random`).
3. **Classic Sci-ML:** Equips Scikit-Learn with dimensional meta-estimators, axiom validators, and automated Buckingham Pi feature synthesis.
4. **Neural PDEs (PINNs):** Deep PyTorch integration. The `PTensor` allows gradients to flow safely through physical laws using native calculus (`pnn.grad`, `pnn.laplace`).
5. **Hybrid Data Engineering:** Normalizes raw CSVs/DataFrames and enforces physical limits at the ingestion layer using a Rust backend, bridging directly into PyTorch via `.phx` or `.parquet` formats.

---

## ⚛️ The Physics Engine: A Modern Alternative

Legacy unit libraries (like Pint or Astropy) rely on generic object wrappers and runtime string evaluation, resulting in high computational overhead and blind IDEs. Phaethon rebuilds dimensional analysis from the ground up using modern Python architecture:

* **Zero-Overhead NumPy Proxies (NEP 13/18):** `BaseUnit` does not strictly subclass `np.ndarray` to avoid the brittle inheritance trap. Instead, it acts as a duck-typed protocol proxy, intercepting operations at the NumPy C-API layer. This allows it to natively fuse physics into floats, massive `ndarrays`, and even `MaskedArrays` without Python-level bottlenecks.
* **Metaclass JIT Caching:** Physical dimensions are concrete Python classes. When dimensions interact algebraically, the `_PhaethonUnitMeta` dynamically synthesizes a new class blueprint in memory and caches it via LRU. Math operations operate at raw C-speed without string parsing.
* **Flawless Static Typing (DX):** Because every dimension is a real class, IDEs (Mypy/Pylance) can strictly type-check physics out of the box (e.g., `def calc(x: u.LengthUnit)` will statically reject `u.Kilogram`).

### Scientific Computing Example
Phaethon extends dimensional safety into advanced linear algebra and stochastic generation.

```python
import phaethon as ptn
import phaethon.units as u

# 1. Zero-overhead NumPy tensor creation
mass_matrix = ptn.array([[10.0, 2.0], [3.0, 5.0]], u.Kilogram)
force_vector = u.Newton([50.0, 25.0]) # or just instantiate directly

# 2. Native Linear Algebra - Automatically synthesizes Acceleration (m/s²)
acceleration = ptn.linalg.solve(mass_matrix, force_vector)

# 3. Logarithmic Algebra & Isomorphic Firewalls natively supported
signal = u.DecibelMilliwatt(30) + u.DecibelMilliwatt(30)
# Evaluates precisely to ~33.01 dBm via implicit linearization
```

---

## 🚀 End-to-End Example: Physics-Informed Neural Networks

The following workflow demonstrates Phaethon's end-to-end capability: parsing raw sensor data, extracting it into a dimension-aware dataset, and training a neural network to solve Burgers' Equation while mathematically guaranteeing dimensional integrity.

### Step 1: Ingesting Data (Schema)
Normalize chaotic inputs, apply boundary constraints, and extract data into PyTorch-ready tensors.

```python
import pandas as pd
import phaethon as ptn
import phaethon.units as u

# Declaratively enforce physical laws on incoming data
class SensorSchema(ptn.Schema):
    x_pos: u.Meter = ptn.Field("Position", parse_string=True)
    t_time: u.Second = ptn.Field("Time", min=0.0, on_error="clip")

# Load and normalize a raw DataFrame
messy_df = pd.read_csv("sensor_telemetry.csv")
clean_df = SensorSchema.normalize(messy_df)

# Bridge directly into PyTorch PTensors (Physics-Aware Tensors)
dataset = SensorSchema.astensor(clean_df, requires_grad=['x_pos', 't_time'])

x_sensor = dataset['x_pos'].tensor
t_sensor = dataset['t_time'].tensor
```

### Step 2: Neural Architecture (Assembly)
Standard PyTorch layers cannot digest physical metadata. Phaethon's `assemble` securely standardizes and strips the units, feeding pure features to the network before resurrecting the physics on the output.

```python
import torch.nn as nn
import phaethon.pinns as pnn

class ShockwaveNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 128), nn.SiLU(),
            nn.Linear(128, 128), nn.SiLU(),
            nn.Linear(128, 1)
        )
        
    def forward(self, x_raw, t_raw):
        # 1. Standardize inputs to base units safely
        x_std = x_raw.asunit(u.Meter)
        t_std = t_raw.asunit(u.Second)
        
        # 2. Assemble physical tensors into naked PyTorch features
        features = pnn.assemble(x_std, t_std, dim=-1)
        
        # 3. Forward Pass & Resurrect Physical Identity (Velocity)
        u_mag = self.net(features)
        return pnn.PTensor(u_mag, unit=u.MeterPerSecond), x_std, t_std
```

### Step 3: Native Calculus & Loss Evaluation
Train the network using native differential calculus. Phaethon automatically synthesizes derivative units, and the `ResidualLoss` strictly ensures dimensional balance on the PDE.

```python
model = ShockwaveNet()
pde_loss_fn = pnn.ResidualLoss()
nu = pnn.PTensor(0.01 / 3.14159, unit=u.SquareMeterPerSecond)

# Forward pass
u_pred, x_s, t_s = model(x_sensor, t_sensor)

# Native PyTorch Calculus (Automatically synthesizes derived units)
du_dt = pnn.grad(u_pred, t_s, create_graph=True)
du_dx = pnn.grad(u_pred, x_s, create_graph=True)
d2u_dx2 = pnn.laplace(u_pred, x_s)

# Formulate the PDE Residual (Burgers' Equation)
# If dimensions mismatch (e.g., subtracting Force from Acceleration), execution halts.
pde_residual = du_dt + (u_pred * du_dx) - (nu * d2u_dx2) 

# Compute Physics-Informed Penalty
loss = pde_loss_fn(pde_residual, target=0.0)
loss.backward()
```

---

## 📦 Installation & Modularity
Phaethon requires **Python >= 3.11** and is compiled via Maturin (Rust backend). Install only the scientific stack you need to avoid environment bloat:

```bash
# Core Physics Engine Only
pip install phaethon

# Data Engineering (Pandas + Rapidfuzz)
pip install 'phaethon[dataframe]'

# Neural PDEs & PINNs (PyTorch)
pip install 'phaethon[torch]'

# Classic Sci-ML (Scikit-learn)
pip install 'phaethon[sklearn]'

# The Complete Sci-ML Ecosystem
pip install 'phaethon[all]'
```

---

## 🤝 Contributing
Contributions from the open-source community are greatly appreciated. Whether you are adding a new physical domain, optimizing the Rust backend, or expanding the Scikit-Learn transformers, your help is welcome.

Please read our **[CONTRIBUTING.md](CONTRIBUTING.md)** to set up your development environment, install the `[dev]` dependencies, and run the test suite.

## 📜 License
Distributed under the MIT License. See the `LICENSE` file for more information.