---
seo_type: TechArticle
title: "Physics Engine: Module Overview"
description: "The core of Phaethon's scientific computing framework. Metaclass-driven unit tensors, Isomorphic Firewalls, dimensional algebra, and stochastic tensors."
keywords: "physics engine Python, dimensional algebra scientific computing, physical tensor overview, Isomorphic Firewalls, phaethon.linalg, phaethon.random, phaethon.axiom"
---

# The Physics Engine

The mathematical heart of Phaethon. A metaclass-driven physics engine backed by an independent dimensional registry for tracking physical signatures. NumPy's C-API is leveraged separately for zero-overhead array vectorization and broadcasting.

---

## Core Infrastructure

<div class="grid cards" markdown>

-   **[Units & Tensors](units.md)**
    
    ---
    
    Instantiating physical unit tensors, NumPy physics tensors, and traversing physical properties.

-   **[Dimensional Algebra](algebra.md)**
    
    ---
    
    Dynamic synthesis of new dimensions, Isomorphic Firewalls, Domain Locks, and Logarithmic math.

-   **[Scientific Compute](compute.md)**
    
    ---
    
    Physics-aware Linear Algebra and bounded stochastic tensor generation.

</div>

## Control & Customization

<div class="grid cards" markdown>

-   **[Config & Guardrails](config.md)**
    
    ---
    
    Setting strictness levels, floating-point tolerances, on-error actions, and environmental context.

-   **[Custom Units](custom.md)**
    
    ---
    
    Extending the registry with new dimensions, or adding new units to an existing dimension.

-   **[Fluent API](fluent.md)**
    
    ---
    
    High-speed, chainable conversion pipelines.

</div>