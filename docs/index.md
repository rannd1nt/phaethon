---
hide:
  - navigation
  - toc
seo_type: SoftwareApplication
title: Phaethon Framework
description: "The End-to-End Physics-Constrained Scientific Computing & Sci-ML Framework. Native Rust pipelines, dimensional tensors, and neural PDEs."
keywords: "physics-constrained scientific computing, Sci-ML python framework, physics informed neural networks, dimensional analysis python, pytorch physics tensor, python units"
---


</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="stylesheet/landing.css">

<div class="landing-wrapper">

  <nav class="landing-nav" aria-label="Main Navigation">
    <a href="/" class="nav-logo">
      Phaethon
    </a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="https://github.com/rannd1nt/phaethon" target="_blank" rel="noopener noreferrer">GitHub</a>
      <a href="https://github.com/rannd1nt/phaethon/releases" target="_blank" rel="noopener noreferrer">Release Notes</a>
      <a href="https://github.com/rannd1nt/phaethon/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">License</a>
    </div>
    
    <button class="mobile-menu-btn" aria-label="Toggle Mobile Menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12" class="line-mid"></line>
        <line x1="3" y1="6" x2="21" y2="6" class="line-top"></line>
        <line x1="3" y1="18" x2="21" y2="18" class="line-bot"></line>
      </svg>
    </button>
  </nav>

  <div class="mobile-menu-overlay">
    <a href="/">Home</a>
    <a href="https://github.com/rannd1nt/phaethon" target="_blank" rel="noopener noreferrer">GitHub</a>
    <a href="https://github.com/rannd1nt/phaethon/releases" target="_blank" rel="noopener noreferrer">Release Notes</a>
    <a href="https://github.com/rannd1nt/phaethon/blob/main/LICENSE" target="_blank" rel="noopener noreferrer">License</a>
  </div>

  <section class="hero animate-up" aria-labelledby="hero-title">
    <span class="sr-only">Phaethon: The End-to-End Scientific Computing & Sci-ML Stack. Enforcing absolute mathematical integrity from raw sensor streams to complex PDE simulations.</span>

    <div class="hero-glow"></div>
    <div class="hero-badge">
      <div class="badge-dot"></div>
      Physics-Constrained Scientific Computing
    </div>
    
    <h1 id="hero-title">Compute reality.<br><em>Data to AI.</em></h1>
    <p class="hero-sub">
      The unified SciML stack. Phaethon bridges the gap between chaotic physical data and advanced AI through native-speed tabular pipelines, dimensional tensor mechanics, and physics-constrained deep learning.
    </p>
    <div class="hero-actions">
      <a href="getting-started/" class="btn-primary">Get Started</a>
      <a href="docs/" class="btn-secondary">Read the Docs →</a>
    </div>
  </section>

  <hr class="divider">

  <section id="architecture" class="scroll-reveal" aria-labelledby="arch-title">
    <span class="sr-only">Core Architecture Modules: Units & Tensors, Hybrid Data Engineering, Polyglot I/O, and Sci-ML with PyTorch PINNs.</span>
    <div class="section-label">Architecture</div>
    <h2 id="arch-title" class="section-title">Built for the <em>entire</em><br>scientific stack.</h2>
    <p class="section-desc">
      Five deeply integrated modules executing absolute physical integrity from data ingestion to differential calculus.
    </p>

    <div class="arch-grid">
      <div class="arch-card scroll-reveal stagger-1">
        <div class="arch-icon">
          <svg role="img" aria-label="Units and Dimensional Analysis Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
        </div>
        <div class="arch-tag">phaethon.units</div>
        <h3 class="arch-title">Dimensional Tensor Algebra</h3>
        <div class="arch-desc">
          Metaclass-driven physics engine across 90+ domains. Enforces mathematical integrity via Isomorphic Firewalls and Domain Locks. Features Isomorphic Firewalls, Semantic Domain Locks, real-time logarithmic scale evaluation, and deep NumPy protocol integration for zero-overhead vectorized tensor mechanics.
        </div>
      </div>
      <div class="arch-card scroll-reveal stagger-2">
        <div class="arch-icon">
          <svg role="img" aria-label="Hybrid Data Engineering Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
        </div>
        <div class="arch-tag">phaethon.Schema</div>
        <h3 class="arch-title">Hybrid Data Engineering</h3>
        <div class="arch-desc">
          Declarative pipelines for Pandas and Polars. Leverages a Rust backend for extreme-speed physical string parsing and C++ RapidFuzz for fuzzy ontologies. Executes vectorized imputation, anomaly clipping, and strict Axiom boundary enforcement.
        </div>
        <div class="arch-pip"><div class="arch-pip-dot"></div>[dataframe] or [polars]</div>
      </div>
      <div class="arch-card scroll-reveal stagger-3">
        <div class="arch-icon">
          <svg role="img" aria-label="Polyglot Storage Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="12" x2="2" y2="12"></line><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="6" y1="16" x2="6.01" y2="16"></line><line x1="10" y1="16" x2="10.01" y2="16"></line></svg>
        </div>
        <div class="arch-tag">phaethon.Dataset</div>
        <h3 class="arch-title">Polyglot I/O Storage</h3>
        <div class="arch-desc">
          A dimension-aware columnar store unifying discrete semantics and continuous physics tensors. Secures data via .phx cryptographic archives, with native PyArrow (.parquet) and HDF5 (.h5) integrations for scientific interoperability.
        </div>
        <div class="arch-pip"><div class="arch-pip-dot"></div>[h5], [arrow] or [io]</div>
      </div>
      <div class="arch-card scroll-reveal stagger-4">
        <div class="arch-icon">
          <svg role="img" aria-label="Scientific Machine Learning Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>
        </div>
        <div class="arch-tag">phaethon.ml + phaethon.pinns</div>
        <h3 class="arch-title">Classical & Deep Sci-ML</h3>
        <div class="arch-desc">
          An end-to-end SciML engine. Wraps Scikit-Learn with physics-aware meta-estimators and automated Buckingham Pi feature synthesis. Deep PyTorch integration unlocks physical autograd (PTensor), native PDE calculus, and Fourier Neural Operators.
        </div>
        <div class="arch-pip"><div class="arch-pip-dot"></div>[sklearn], [torch] or [sciml]</div>
      </div>
    </div>
  </section>

  <hr class="divider">

  <section class="scroll-reveal">
    <div class="split-section">
      <div>
        <div class="section-label">phaethon.units</div>
        <h2 class="section-title">Dimensional algebra<br>that <em>thinks.</em></h2>
        <p class="section-desc">
          Intercepts complex mathematics at runtime. Isolates semantic anomalies, computes matrices, and tracks SI units to prevent silent physics failures.
        </p>
      </div>
      <div class="pill-list">
        <div class="pill-item scroll-reveal stagger-1">
          <div class="pill-icon">
            <svg role="img" aria-label="Isomorphic Firewalls Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Isomorphic Firewalls</h3>
            <div class="pill-item-desc">Actively tracks Phantom Units to isolate mathematically identical but conceptually distinct dimensions (e.g., Frequency vs. Radioactivity).</div>
          </div>
        </div>
        <div class="pill-item scroll-reveal stagger-2">
          <div class="pill-icon">
            <svg role="img" aria-label="Semantic Domain Locks Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Semantic Domain Locks</h3>
            <div class="pill-item-desc">Rejects illegal casting between specialized domains (e.g., Energy vs. Torque) requiring explicit algebraic synthesis to proceed.</div>
          </div>
        </div>
        <div class="pill-item scroll-reveal stagger-3">
          <div class="pill-icon">
            <svg role="img" aria-label="Logarithmic Scale Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Real-Time Logarithmic Scaling</h3>
            <div class="pill-item-desc">Natively evaluates non-linear arithmetic (e.g., Decibels, pH), implicitly linearizing values to prevent mathematical impossibilities.</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <hr class="divider">

  <section class="scroll-reveal">
    <div class="split-section">
      <div>
        <div class="section-label">phaethon.pinns & phaethon.ml</div>
        <h2 class="section-title">Neural networks that<br><em>obey physics.</em></h2>
        <p class="section-desc">
          Bridge the gap between data-driven Deep Learning and fundamental reality with dimension-aware operators and physics-informed losses.
        </p>
      </div>
      <div class="pill-list">
        <div class="pill-item scroll-reveal stagger-1">
          <div class="pill-icon">
             <svg role="img" aria-label="Autograd PTensor Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20a6 6 0 0 0-12 0"></path><circle cx="12" cy="10" r="4"></circle><circle cx="12" cy="12" r="10"></circle></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Physics-Aware Autograd (PTensor)</h3>
            <div class="pill-item-desc">Tensors retain dimensional identity through complex matrix operations, SVDs, and gradient descent inside PyTorch's computational graph.</div>
          </div>
        </div>
        <div class="pill-item scroll-reveal stagger-2">
          <div class="pill-icon">
            <svg role="img" aria-label="Neural Operators Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Neural Operators & Calculus</h3>
            <div class="pill-item-desc">Built-in Spectral Convolutions for FNOs and native differential calculus (grad, curl, laplace) to solve coupled Partial Differential Equations.</div>
          </div>
        </div>
        <div class="pill-item scroll-reveal stagger-3">
          <div class="pill-icon">
            <svg role="img" aria-label="Axiom-Bounded ML Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><circle cx="12" cy="12" r="4"></circle></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Axiom-Bounded Predictions</h3>
            <div class="pill-item-desc">Scikit-Learn meta-estimators and Physics-Informed Loss Tribunals violently penalize networks that mathematically extrapolate into impossible bounds.</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <hr class="divider">

  <section class="scroll-reveal">
    <div class="split-section reverse">
      <div>
        <div class="section-label">phaethon.Schema</div>
        <h2 class="section-title">Data pipelines<br>at <em>machine speed.</em></h2>
        <p class="section-desc">
          Normalizes millions of irregular records with exceptional throughput by circumventing Python's standard string handling bottlenecks.
        </p>
      </div>
      <div class="pill-list">
        <div class="pill-item scroll-reveal stagger-1">
          <div class="pill-icon">
            <svg role="img" aria-label="Rust Parsing Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Rust-Powered Extraction</h3>
            <div class="pill-item-desc">A dedicated Rust engine slices through chaotic, mixed-type physical text, bypassing Python overhead for extreme parsing speeds.</div>
          </div>
        </div>
        <div class="pill-item scroll-reveal stagger-2">
          <div class="pill-icon">
            <svg role="img" aria-label="Vectorized Data Healing Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </div>
          <div>
            <h3 class="pill-item-title">Vectorized Data Healing</h3>
            <div class="pill-item-desc">Leverages the C/C++ backends of Pandas and Polars for zero-copy imputation, time-series interpolation, and anomaly clipping.</div>
          </div>
        </div>
        <div class="pill-item scroll-reveal stagger-3">
          <div class="pill-icon">
            <svg role="img" aria-label="Fuzzy Integration Icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
          </div>
          <div>
            <h3 class="pill-item-title">C++ RapidFuzz Ontologies</h3>
            <div class="pill-item-desc">Utilizes high-speed Levenshtein distance matching to clean typographical errors and map real-world categories into strict ontologies.</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <hr class="divider">

  <section class="scroll-reveal">
    <div class="section-label">Installation</div>
    <h2 class="section-title">Start with what<br>you <em>need.</em></h2>
    <p class="section-desc">
      Phaethon is fully modular. Install only the engine components relevant to your scientific workload without bloating your environment.
    </p>

    <div class="extras-grid">
      <div class="extra-card scroll-reveal stagger-1">
        <div class="extra-label" style="color:var(--text-accent)">Physics Engine</div>
        <h3 class="extra-title">Dimensional Algebra</h3>
        <div style="font-size:13px; color:var(--text-secondary); line-height:1.65">
          90+ domains, domain locks, native .phx storage, global contexts, and NumPy tensor wrappers. Zero extra dependencies.
        </div>
        <div class="extra-cmd"><code>pip install phaethon</code></div>
      </div>
      <div class="extra-card scroll-reveal stagger-2">
        <div class="extra-label" style="color:var(--text-accent)">Data Engineering</div>
        <h3 class="extra-title">Schema + Tabular</h3>
        <div style="font-size:13px; color:var(--text-secondary); line-height:1.65">
          Hybrid Rust/C++ pipeline engine for extreme-scale physical string parsing and validation.
        </div>
        <div class="extra-cmd"><code>pip install 'phaethon[dataframe]'</code></div>
        <div class="extra-cmd" style="margin-top:6px"><code>pip install 'phaethon[polars]'</code></div>
      </div>
      <div class="extra-card scroll-reveal stagger-3">
        <div class="extra-label" style="color:var(--text-accent)">Sci-ML Bridge</div>
        <h3 class="extra-title">Scikit-Learn Integration</h3>
        <div style="font-size:13px; color:var(--text-secondary); line-height:1.65">
          Buckingham Pi automated feature synthesis and strictly bounded classical estimators.
        </div>
        <div class="extra-cmd"><code>pip install 'phaethon[sklearn]'</code></div>
      </div>
      <div class="extra-card scroll-reveal stagger-4">
        <div class="extra-label" style="color:var(--text-accent)">Deep Learning</div>
        <h3 class="extra-title">PINNs + PyTorch</h3>
        <div style="font-size:13px; color:var(--text-secondary); line-height:1.65">
          PTensor autograd, native physical calculus, and spectral layers for PDE solvers.
        </div>
        <div class="extra-cmd"><code>pip install 'phaethon[torch]'</code></div>
      </div>
      <div class="extra-card scroll-reveal stagger-5">
        <div class="extra-label" style="color:var(--text-accent)">I/O Storage</div>
        <h3 class="extra-title">HDF5 & Parquet</h3>
        <div style="font-size:13px; color:var(--text-secondary); line-height:1.65">
          Adds external dependencies (h5py, pyarrow) to the columnar store for language interoperability.
        </div>
        <div class="extra-cmd"><code>pip install 'phaethon[io]'</code></div>
      </div>
      <div class="extra-card scroll-reveal stagger-6">
        <div class="extra-label" style="color:var(--text-accent)">Enterprise Bundle</div>
        <h3 class="extra-title">Full Sci-ML Stack</h3>
        <div style="font-size:13px; color:var(--text-secondary); line-height:1.65">
          Installs the complete scientific ecosystem in a single, unified command.
        </div>
        <div class="extra-cmd"><code>pip install 'phaethon[sciml]'</code></div>
      </div>
    </div>
  </section>

  <div class="custom-footer">
    <span class="logo-small">Phaethon &copy; 2026. All rights reserved.</span>
    <div class="footer-links">
      <span style="color: var(--text-tertiary); font-size: 13px;">Designed for absolute dimensional integrity in Python.</span>
    </div>
  </div>

  <button id="backToTopBtn" class="back-to-top-btn" aria-label="Back to top">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="18 15 12 9 6 15"></polyline>
    </svg>
  </button>

</div>

<script>
  document.addEventListener("DOMContentLoaded", function() {
    const observerOptions = { root: null, rootMargin: '0px', threshold: 0.15 };
    const observer = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target); 
        }
      });
    }, observerOptions);

    document.querySelectorAll('.scroll-reveal').forEach((el) => {
      observer.observe(el);
    });

    const bttBtn = document.getElementById('backToTopBtn');
    window.addEventListener('scroll', () => {
      if (window.scrollY > 400) {
        bttBtn.classList.add('show');
      } else {
        bttBtn.classList.remove('show');
      }
    });

    bttBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    const menuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu-overlay');
    
    if (menuBtn && mobileMenu) {
      menuBtn.addEventListener('click', () => {
        const isActive = menuBtn.classList.toggle('is-active');
        mobileMenu.classList.toggle('is-open');
        
        if (isActive) {
          document.body.style.overflow = 'hidden';
        } else {
          document.body.style.overflow = '';
        }
      });
      
      mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          menuBtn.classList.remove('is-active');
          mobileMenu.classList.remove('is-open');
          document.body.style.overflow = '';
        });
      });
    }
  });
</script>