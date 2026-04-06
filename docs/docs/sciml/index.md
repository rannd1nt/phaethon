---
seo_type: TechArticle
title: "Classic Sci-ML: Scikit-Learn Bridge"
description: "Phaethon's classic Sci-ML bridge. Equip Scikit-Learn with Dimensional estimators, axiom validators, SVD transformers, and physics-aware metrics."
keywords: "physics-aware machine learning, scikit-learn physics integration, physics-constrained regression python, dimensionless feature synthesis"
---

# Classic SciML

The `phaethon.ml` module provides deep integration with Scikit-Learn, bridging classical machine learning with strict dimensional algebra. 

While Neural PDEs handle infinite-dimensional spaces, Classic SciML equips traditional, heavily optimized tabular algorithms (like Random Forests, XGBoost, and Support Vector Machines) with physics-aware meta-estimators, automated Buckingham Pi feature engineering, and dimensionally safe evaluation metrics.

!!! info "Dependency Note"
    The Classic SciML module strictly requires the Scikit-Learn backend.
    Install via: `pip install 'phaethon[sklearn]'`

---

## Classic SciML Architecture

<div class="grid cards" markdown>

-   **[Meta-Estimators & Workflows](estimators.md)**
    
    ---
    
    The `DimensionalEstimator` and `AxiomValidator`. Wrappers that safely strip and resurrect physical dimensions, alongside physics-aware train-test splitting.

-   **[Physics-Aware Transformers](transformers.md)**
    
    ---
    
    Secure scaling pipelines (`DimensionalTransformer`) and automated SVD null-space extraction (`BuckinghamTransformer`) to synthesize pure dimensionless features on-the-fly.

-   **[Physics-Aware Metrics](metrics.md)**
    
    ---
    
    Dimensionally strict evaluation engines for MAE, MSE, and R-Squared. Accurately validate models and automatically synthesize complex error dimensions (e.g., converting Distance errors into Area).

</div>