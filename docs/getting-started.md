---
hide:
  - navigation
  - toc
seo_type: TechArticle
title: "Quickstart: Install & First Pipeline"
description: "Start building physics-constrained Python pipelines. Instantiate physical tensors, compute PyTorch PDE gradients, and normalize tabular data."
keywords: "physics-constrained python tutorial, getting started with Sci-ML, dimensional analysis tutorial, physics tensor python, pytorch PDE solver"
---

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../stylesheet/quickstart.css">

<div class="landing-wrapper">

  <nav aria-label="Main Navigation" class="landing-nav">
    <a href="/" class="nav-logo">
      Phaethon
    </a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="https://github.com/rannd1nt/phaethon" target="_blank" rel="noopener noreferrer">GitHub</a>
      <a href="https://github.com/rannd1nt/phaethon/releases" target="_blank" rel="noopener noreferrer">Release Notes</a>
      <a href="https://opensource.org/licenses/MIT" target="_blank" rel="noopener noreferrer">MIT License</a>
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
    <a href="https://opensource.org/licenses/MIT" target="_blank" rel="noopener noreferrer">License</a>
  </div>

  <section class="hero animate-up">
    <h1>Quickstart Guide</h1>
    <p class="hero-sub">
      Install the framework and discover the power of physics-constrained scientific computing.
    </p>
    <span class="sr-only">This tutorial covers Phaethon installation, instantiating units and tensors, building hybrid data engineering schemas, and executing native physical calculus in PyTorch.</span>
  </section>

  <section class="animate-up" style="padding-top: 0;">
    
    <h2 class="code-section-title">1. Installation</h2>
    <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 24px;">Phaethon is fully modular. You only install what you need.</p>
    
    <div class="install-grid">
      <div class="install-card scroll-reveal stagger-1">
        <h3 class="install-card-title" style="color: var(--text-primary);">Minimal Installation</h3>
        <div style="font-size: 13px; color: var(--text-tertiary); margin-bottom: 16px;">Includes Units & Dimensional Analysis and NumPy integration.</div>
        <code>pip install phaethon</code>
      </div>
      <div class="install-card scroll-reveal stagger-2" style="border-color: var(--border-hover); background: var(--purple-soft);">
        <h3 class="install-card-title" style="color: var(--text-accent);">Complete Ecosystem</h3>
        <div style="font-size: 13px; color: var(--text-tertiary); margin-bottom: 16px;">Installs everything: Pandas, Polars, RapidFuzz, Sci-ML, Torch, H5, and Arrow.</div>
        <code style="color: var(--text-accent); border-color: var(--border-hover);">pip install 'phaethon[all]'</code>
      </div>
    </div>

    <div class="modular-box scroll-reveal stagger-3">
      <h3>Targeted Bundles & Individual Packages</h3>
      <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-top: 6px;">
        If you are deploying to constrained environments (like edge devices or strict Docker containers), you can selectively install specific capability bundles:
      </p>
      <ul>
        <li><code>pip install 'phaethon[dataframe]'</code> <span>Pandas & RapidFuzz (Data pipelines)</span></li>
        <li><code>pip install 'phaethon[sciml]'</code> <span>Scikit-Learn & PyTorch (Machine Learning)</span></li>
        <li><code>pip install 'phaethon[io]'</code> <span>h5py & pyarrow (Polyglot Storage)</span></li>
      </ul>
      <p style="font-size: 12px; color: var(--text-tertiary); margin: 0; padding-top: 8px; border-top: 1px solid var(--border);">
        *You can also target specific engine backends directly: <code>[pandas]</code>, <code>[polars]</code>, <code>[sklearn]</code>, <code>[torch]</code>.
      </p>
    </div>

    <div class="scroll-reveal">
      <h2 class="code-section-title">2. Units & Dimensional Analysis</h2>
      <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 24px;">
        Phaethon understands the laws of physics natively. It synthesizes complex dimensions on the fly and allows seamless conversions while mathematically blocking impossible operations.
      </p>
    </div>
    
    <div class="code-block scroll-reveal stagger-1">
      <div class="code-header">
        <div class="code-dots"><div class="code-dot"></div><div class="code-dot"></div><div class="code-dot"></div></div>
        <span class="code-lang">python</span>
      </div>
      <div class="code-body" markdown="1">
```python
import phaethon.units as u

mass = u.Kilogram(1500)
acceleration = u.MeterPerSecondSquared(9.8)

# The engine dynamically synthesizes the correct physical dimension
force = mass * acceleration
print(force)
# 14700.0 N

# Seamlessly convert to other valid units within the same dimension
print(force.to(u.Kilonewton))
# 14.7 kN

# Mathematically blocking impossible physical states before they corrupt pipelines
impossible = mass + acceleration
# DimensionMismatchError: Cannot add 'mass' and 'acceleration'.
```
      </div>
    </div>

    <div class="scroll-reveal">
      <h2 class="code-section-title">3. Hybrid Data Engineering</h2>
      <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 24px;">
        Build strict schemas to clean messy sensor strings, interpolate dead zones, and enforce physical bounds using the underlying Rust/C++ engine.
      </p>
    </div>
    
    <div class="code-block scroll-reveal stagger-1">
      <div class="code-header">
        <div class="code-dots"><div class="code-dot"></div><div class="code-dot"></div><div class="code-dot"></div></div>
        <span class="code-lang">python</span>
      </div>
      <div class="code-body" markdown="1">
```python
import phaethon as ptn
import pandas as pd
import phaethon.units as u

class RocketSchema(ptn.Schema):
    # Parses raw strings, drops 'ERR' signals, and enforces Absolute Zero
    temperature: u.Celsius = ptn.Field(
        source="raw_temp", 
        parse_string=True, 
        min=-273.15, 
        on_error="clip"
    )

# Load real-world chaotic sensor outputs from disk
dirty_data = pd.read_csv("telemetry_export.csv")

# The Rust/C++ engine normalizes millions of rows in a single, extreme-throughput pass
clean_data = RocketSchema.normalize(dirty_data)
```
      </div>
    </div>

    <div class="scroll-reveal">
      <h2 class="code-section-title">4. The Dimension-Aware Dataset</h2>
      <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 24px;">
        Seamlessly transition cleaned DataFrames into a Phaethon Dataset. This unified columnar store holds both naked arrays and PyTorch autograd tensors simultaneously.
      </p>
    </div>

    <div class="code-block scroll-reveal stagger-1">
      <div class="code-header">
        <div class="code-dots"><div class="code-dot"></div><div class="code-dot"></div><div class="code-dot"></div></div>
        <span class="code-lang">python</span>
      </div>
      <div class="code-body" markdown="1">
```python
# Translate the DataFrame into a zero-overhead Phaethon Dataset
dataset = RocketSchema.astensor(clean_data, requires_grad=True)

# Extract a PyTorch-backed PTensor. 
# Its physical DNA and autograd state remain perfectly intact.
temp_tensor = dataset['temperature'].tensor
time_tensor = dataset['time'].tensor

print(temp_tensor.requires_grad)
# True
```
      </div>
    </div>

    <div class="scroll-reveal">
      <h2 class="code-section-title">5. Native Physical Calculus</h2>
      <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 24px;">
        Feed the extracted PyTorch tensors directly into Phaethon's calculus engine. Differentiating tensors automatically computes gradients and synthesizes the correct derivative units within the autograd graph.
      </p>
    </div>

    <div class="code-block scroll-reveal stagger-1" style="margin-bottom: 0;">
      <div class="code-header">
        <div class="code-dots"><div class="code-dot"></div><div class="code-dot"></div><div class="code-dot"></div></div>
        <span class="code-lang">python</span>
      </div>
      <div class="code-body" markdown="1">
```python
import phaethon.pinns as pnn

# Differentiating Temperature over Time (dT/dt)
cooling_rate = pnn.grad(outputs=temp_tensor, inputs=time_tensor)

# Phaethon automatically infers the derived physical unit!
print(cooling_rate.unit.symbol)
# °C/s

# Formulate Physics-Informed Neural Network (PINNs) loss functions securely
pde_loss = pnn.ResidualLoss()(cooling_rate, target=0.0)
pde_loss.backward()
```
      </div>
    </div>

    <div class="scroll-reveal">
      <h2 class="code-section-title" style="margin-top: 80px;">Where to go next?</h2>
      <p style="color: var(--text-secondary); font-size: 15px; margin-bottom: 24px;">
        Now that you understand the core lifecycle, dive deeper into the technical architecture or explore our real-world interactive examples.
      </p>
    </div>
    
    <nav aria-label="Next Steps" class="next-grid">
      
      <a href="../docs/" class="scroll-reveal stagger-1">
        <div class="next-card">
          <div class="next-icon">📖</div>
          <h3 class="next-title">Documentation Hub</h3>
          <p class="next-desc">Enter the main documentation hub and explore the full Phaethon ecosystem.</p>
        </div>
      </a>

      <a href="https://github.com/rannd1nt/phaethon/tree/main/examples" target="_blank" rel="noopener noreferrer" class="scroll-reveal stagger-2">
        <div class="next-card">
          <div class="next-icon">🚀</div>
          <h3 class="next-title">Interactive Examples</h3>
          <p class="next-desc">Browse our collection of real-world use cases, Jupyter Notebooks, and Google Colabs.</p>
        </div>
      </a>

    </nav>
  </section>
  
  <footer class="custom-footer">
    <span class="logo-small">Phaethon &copy; 2026. All rights reserved.</span>
    <div class="footer-links">
      <span style="color: var(--text-tertiary); font-size: 13px;">Designed for absolute dimensional integrity in Python.</span>
    </div>
  </footer>

  <button id="backToTopBtn" class="back-to-top-btn" aria-label="Back to top">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="18 15 12 9 6 15"></polyline>
    </svg>
  </button>

</div>

<script>
  document.addEventListener("DOMContentLoaded", function() {
    // 1. Scroll Animations (Intersection Observer)
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

    // 2. Back to Top Logic
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

    // 3. Mobile Hamburger Menu Logic
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu-overlay');
    
    if (menuBtn && mobileMenu) {
      menuBtn.addEventListener('click', () => {
        const isActive = menuBtn.classList.toggle('is-active');
        mobileMenu.classList.toggle('is-open');
        
        // Lock the background scrolling when menu is open
        if (isActive) {
          document.body.style.overflow = 'hidden';
        } else {
          document.body.style.overflow = '';
        }
      });
      
      // Close menu if a link is clicked
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