---
seo_type: TechArticle
title: "Documentation Hub: Architecture"
description: "Official docs for the physics-constrained Sci-ML framework. Explore the Physics Engine, Neural PDEs with PINNs, Classic Sci-ML, and Data Engineering."
keywords: "physics-constrained scientific computing docs, Sci-ML framework reference, physics engine python, PINNs documentation, physical data engineering"
---

# Phaethon Documentation Hub

Welcome to the official documentation for **Phaethon**, the End-to-End Physics-Constrained Scientific Computing & Sci-ML Stack.

Standard machine learning ecosystems treat data as mathematically blind, naked floating-point numbers. Phaethon bridges the gap between data-driven AI and fundamental physical reality. It provides a unified ecosystem that integrates native-speed tabular ingestion, rigorous dimensional tensor mechanics, and physics-constrained (informed) neural networks (PINNs) into a single, cohesive Python framework.

Whether you are cleaning chaotic sensor data or training Fourier Neural Operators for complex PDEs, Phaethon ensures absolute mathematical integrity from the ground up.

---

## The Architecture

Phaethon is built upon four deeply integrated pillars. Select a module below to explore its API and theoretical foundations:

### [Dimensional Tensor Algebra](physics/index.md)
The mathematical heart of the framework. A metaclass-driven physics engine operating across 90+ physical domains. It features Isomorphic Firewalls, Semantic Domain Locks, real-time logarithmic scale evaluation, and zero-overhead NumPy array wrapping.

### [Hybrid Data Engineering](data/index.md)
Declarative data pipelines designed for machine speed. Leverages a dedicated Rust backend for extreme-speed physical string parsing and C++ RapidFuzz for fuzzy ontologies. Integrates seamlessly with Pandas and Polars to execute vectorized imputation, clipping, and physical validation.

### [Classical Sci-ML](sciml/index.md)
The Scikit-Learn bridge. Equips classical machine learning algorithms with physics-aware Meta-Estimators. Features the `BuckinghamTransformer` for automated, SVD-powered dimensionless feature synthesis, and evaluates models using dimensionally strict metrics.

### [Neural PDEs & PINNs](pinns/index.md)
The deep learning frontier. Deep PyTorch integration that unlocks `PTensor` (Physics-Aware Autograd). Equip your models with native physical calculus (gradients, Laplacians, divergence, curl), Spectral Convolutions for FNOs, and absolute Physics-Informed Loss Tribunals.

---

## Installation & Modularity

Phaethon is intentionally modular. It supports Python `3.11` to `3.14`. You can install the base physics engine, or opt-in to specific scientific stacks to avoid bloating your environment.

```bash
# 1. Base Physics Engine (Zero extra dependencies)
pip install phaethon

# 2. Data Engineering (Rust parser + Pandas/Polars + RapidFuzz)
pip install 'phaethon[dataframe]'
pip install 'phaethon[polars]'

# 3. Classical Machine Learning (Scikit-Learn)
pip install 'phaethon[sklearn]'

# 4. Deep Learning & PINNs (PyTorch)
pip install 'phaethon[torch]'

# 5. Polyglot I/O Storage (HDF5 & PyArrow Parquet)
pip install 'phaethon[io]'

# 6. The Complete Enterprise Bundle
pip install 'phaethon[all]'
```

---

## Open Source & Contributing

Phaethon is an actively evolving open-source project released under the **MIT License**. Built for the global scientific community, we highly encourage scientists, data engineers, and developers to contribute!

Whether you are fixing a typo, adding a new physical domain, or optimizing the Rust backend, your help is massively appreciated.

* **Source Code & Contribution Guide:** Read our comprehensive [CONTRIBUTING.md](https://github.com/rannd1nt/phaethon/blob/main/CONTRIBUTING.md) on GitHub to set up your local environment.
* **Issue Tracker:** [Report a Bug or Request a Feature](https://github.com/rannd1nt/phaethon/issues)