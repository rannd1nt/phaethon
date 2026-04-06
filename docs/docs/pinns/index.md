---
seo_type: TechArticle
title: "PINNs Overview: Tensors & Calculus"
description: "Physics-constrained neural networks in Phaethon. Deep PyTorch integration featuring physics-aware autograd, native PDE calculus, FNOs, and loss tribunals."
keywords: "physics-informed neural networks python, solve PDE with physical units, pytorch physics constrained, PINNs framework python, fourier neural operator"
---

# Neural PDEs & PINNs

The `phaethon.pinns` module provides deep integration with PyTorch, equipping artificial neural networks with absolute dimensional safety. 

By bridging data-driven deep learning with fundamental physical laws, Phaethon introduces physics-aware autograd tensors, native calculus engines for Partial Differential Equations (PDEs), and advanced dimensional synthesis for operator learning.

!!! info "Dependency Note"
    The PINNs module strictly requires the PyTorch backend.
    Install via: `pip install 'phaethon[torch]'`

---

## PINNs Architecture

<div class="grid cards" markdown>

-   **[Physics Tensors & Ops](tensors.md)**
    
    ---
    
    The `PTensor` class. PyTorch tensors that dynamically track physical DNA and safely assemble heterogeneous data for neural ingestion.

-   **[Differential Calculus](calculus.md)**
    
    ---
    
    Native autograd engines (`grad`, `laplace`, `div`, `curl`) that automatically synthesize physical units during differentiation.

-   **[Fourier Neural Operators](fno.md)**
    
    ---
    
    Spectral layers (1D Convolutions) and Buckingham Pi SVD projections for discovering dimensionless groups on-the-fly.

-   **[Physics Losses](losses.md)**
    
    ---
    
    Strictly enforced PDE residuals and Axiom tribunals that penalize networks for mathematically valid but physically impossible predictions.

</div>