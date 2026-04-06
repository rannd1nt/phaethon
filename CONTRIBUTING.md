# Contributing to Phaethon

First of all, thank you for your interest in Phaethon! 

Phaethon is a fast-moving, architecture-heavy framework bridging Physics, Data Engineering, and Deep Learning. Whether you're adding a new physical domain, optimizing the Rust parser, or fixing a bug, your help is massively appreciated!

---

## 🛠️ 1. Setting up your Development Environment

Phaethon's core is partially written in Rust to guarantee extreme parsing speeds. Therefore, compiling the project locally requires a Rust toolchain.

### A. Prerequisites
1. **Python 3.11+**
2. **Rust & Cargo:** You must have Rust installed.
   * **Linux / macOS / WSL (Recommended):** Run `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
   * **Windows Native:** It is highly recommended to use **WSL (Windows Subsystem for Linux)** for a smoother development experience. If you must develop on native Windows, download and install `rustup-init.exe` from [rustup.rs](https://rustup.rs/) and ensure you have the MSVC build tools installed.

### B. Cloning & Virtual Environment
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/rannd1nt/phaethon.git
cd phaethon

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### C. Installing Phaethon (Targeted Dependencies)
Because Phaethon spans multiple disciplines, you do not need to install every dependency if you are only working on a specific module. We use `maturin` to compile the Rust backend.

Choose the installation command that fits the module you are working on. Note that appending `dev` will automatically install `pytest` and `hypothesis` for testing.

* **Core Physics Engine Only** (NumPy only):
  ```bash
  pip install -e '.[dev]'
  ```
* **Data Engineering Module** (Pandas, Polars, RapidFuzz):
  ```bash
  pip install -e '.[dataframe,polars,dev]'
  ```
* **Classic Machine Learning** (Scikit-Learn):
  ```bash
  pip install -e '.[sklearn,dev]'
  ```
* **Neural PDEs & PINNs** (PyTorch):
  ```bash
  pip install -e '.[torch,dev]'
  ```
* **The "I want it all" Bundle** (Installs everything):
  ```bash
  pip install -e '.[all,dev]'
  ```

---

## 🧪 2. Running the Test Suite

We strictly enforce mathematical and physical integrity. Before submitting a Pull Request, you must ensure that all core axioms and tensor mechanics remain intact.

Phaethon's `pytest` configuration is set up to automatically target the `tests/` directory.

```bash
# Run the entire test suite
pytest

# Run tests with verbose output
pytest -v

# Run tests for a specific module (e.g., PINNs)
pytest tests/test_pinns/
```

*(Note: The `benchmarks/` directory contains external parity tests against legacy libraries like Pint. You only need to run `pytest benchmarks/` if you are specifically modifying base conversion logic).*

---

## 🤝 3. Submitting a Pull Request (PR)

1. Create a new branch for your feature: `git checkout -b feature/my-new-domain`
2. Write your code and ensure you add corresponding tests in the `tests/` folder.
3. Run `pytest` to verify nothing is broken.
4. Push to your fork and submit a Pull Request to our `main` branch.
5. Our GitHub Actions CI will automatically test your code across multiple operating systems.

If you are unsure about an architectural decision (e.g., whether to use `@axiom.derive` or inherit from `BaseUnit`), feel free to open an **Issue** first to discuss it with the maintainers! Let's compute reality together.