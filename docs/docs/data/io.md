---
seo_type: TechArticle
title: "Polyglot I/O: PHX, H5 & Parquet"
description: "Dimension-aware columnar storage for scientific computing. Save physics tensors securely to cryptographic archives, Parquet, and HDF5 formats."
keywords: "save physics tensor python, hdf5 dimensional data python, parquet physics serialization, cryptographic dataset python, load physical arrays"
---

# Polyglot I/O & Dataset

Phaethon acts as the ultimate bridge between declarative Data Engineering (Pandas/Polars) and Scientific Machine Learning (PyTorch). 

At the center of this bridge is the `ptn.Dataset`—a zero-overhead, dimension-aware columnar store. Coupled with the `phaethon` Universal I/O Gateway, it allows you to securely serialize and load complex physical tensors across different languages and frameworks using `.phx`, `.parquet`, and `.h5` formats.

---

## The Dimension-Aware Dataset

The `Dataset` class is a unified data structure that holds continuous physics (`PTensor` or `BaseUnit`) and naked numeric arrays side-by-side. 

### Instantiating Datasets

You can explicitly map names to arrays using dictionaries or kwargs, but Phaethon also features an intelligent **Auto-Mapping** capability that inspects your local variables and names the columns automatically.

```python
import phaethon as ptn
import phaethon.units as u

vel = u.MeterPerSecond([10.5, 20.1, 30.0])
temp = u.Celsius([25.0, 26.5, 28.0])
status_codes = [0, 1, 0] # Naked array

# Explicit Initialization
ds_explicit = ptn.Dataset({"velocity": vel, "temperature": temp})

# Auto-Mapping Initialization (Extracts variable names automatically!)
ds = ptn.Dataset(vel, temp, status=status_codes)

print(list(ds.keys()))
# Output: ['vel', 'temp', 'status']
```

---

## The Series Proxy

When you access a column in a `Dataset` (e.g., `ds['vel']`), Phaethon returns an internal `Series` proxy. This proxy allows you to extract the data in the exact format your pipeline requires, completely avoiding unnecessary memory copies.

### Series Extraction Properties

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.raw</span>
    <span class="p-sep">—</span>
    <span class="p-type">np.ndarray</span>
  </div>
  <div class="p-desc">Returns the naked, strictly numerical NumPy array. All physical constraints and autograd states are stripped away.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.array</span>
    <span class="p-sep">—</span>
    <span class="p-type">BaseUnit | np.ndarray</span>
  </div>
  <div class="p-desc">Resolves the column as a NumPy-backed physical <code>BaseUnit</code> (e.g., <code>u.Meter</code>). Returns a raw array if the column has no physics.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.tensor</span>
    <span class="p-sep">—</span>
    <span class="p-type">PTensor | torch.Tensor</span>
  </div>
  <div class="p-desc">Resolves the column as a PyTorch-backed tensor, preserving physical dimensions and autograd configurations for Deep Learning.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">.value</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Dynamically resolves to the state encoded in the dataset metadata. If the dataset was ingested from a Neural Network, it returns a Torch tensor; otherwise, a NumPy array.</div>
</div>

**Extraction in Action:**

```python
# Extract for high-performance C-math
raw_math = ds['vel'].raw * 2.0

# Extract for dimensional tracking
physics_math = ds['vel'].array * u.Second(5)

# Extract for backpropagation in PyTorch
torch_math = ds['vel'].tensor
```

---

## Dataset Interoperability

Phaethon `Dataset` objects can be seamlessly exported back into traditional Data Engineering frameworks or mass-extracted into PyTorch.

### Exporting to DataFrames

You can convert the entire dataset back to Pandas or Polars.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">raw</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool</span>
  </div>
  <div class="p-desc">If <code>True</code> (Default), strips all physics and returns naked float arrays to ensure optimal C-engine compatibility in Pandas/Polars. If <code>False</code>, passes the Python <code>BaseUnit</code> objects directly (may cause Pandas to fallback to <code>dtype=object</code>).</div>
</div>

```python
# Exporting strictly naked numbers for external tools
df_pandas_fast = ds.to_pandas(raw=True)
df_polars_fast = ds.to_polars(raw=True)

# Exporting physics objects (Slower, but preserves domains)
df_physics = ds.to_pandas(raw=False)
```

### Mass Tensor Extraction

Instead of extracting PyTorch tensors column by column, you can extract the entire dataset as a dictionary of tensors.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">requires_grad</span>
    <span class="p-sep">—</span>
    <span class="p-type">bool | None</span>
  </div>
  <div class="p-desc">If explicitly set, forcefully overwrites the autograd state for all physical tensors in the dictionary. If <code>None</code>, respects the pre-existing dataset metadata.</div>
</div>

```python
# Extract all tensors, forcing them to track gradients
tensor_dict = ds.tensors(requires_grad=True)

print(tensor_dict['vel'].requires_grad)
# Output: True
```

---

## Indexing & Diagnostics

### Subsetting with .iloc

Phaethon supports strict 2D integer-location indexing, returning a dynamically scoped `Dataset` or `Series` depending on the slice.

```python
# Slice rows (Returns a new Dataset)
subset_ds = ds.iloc[0:2]

# Slice rows and select a specific column (Returns a Series proxy)
col_series = ds.iloc[:, 1]

# Select a single specific cell (Returns the physical value)
single_val = ds.iloc[0, 1]
```

### Inspecting Dataset Metadata

Use `.info()` to print a comprehensive structural and physical schema, including cryptographic hashes.

```python
ds.info()
```

**Output:**
```text
-------------------------------------------------------------------------
| Key       | Dimension          | Engine   | Shape        | SHA-256    |
-------------------------------------------------------------------------
| vel       | velocity           | numpy    | (3,)         | None       |
| temp      | temperature        | numpy    | (3,)         | None       |
| status    | dimensionless      | numpy    | (3,)         | None       |
-------------------------------------------------------------------------
```

*SHA-256 checksums are computed and stored only when a Dataset is persisted via `ptn.save()`. 
Freshly instantiated Datasets will display `None` until saved.*
---

## Universal I/O Gateway

The Phaethon I/O Gateway handles the safe serialization and deserialization of your models. It supports three formats:

1. **`.phx` (Phaethon Archive)**: The native format. A secure, compressed ZIP archive containing binary `.npy` arrays and a cryptographic `metadata.json` ensuring physical integrity.
2. **`.parquet`**: For cross-language Data Engineering interoperability.
3. **`.h5` / `.hdf5`**: For massive, chunked scientific data arrays.

!!! info "Optional Dependencies"
    While `.phx` serialization is native, exporting to external formats requires specific backend libraries.
    If you encounter an `ImportError`, you can install them via:
    
    * **For Parquet**: `pip install 'phaethon[io]'` (installs `pyarrow`)
    * **For HDF5**: `pip install 'phaethon[io]'` (installs `h5py`)

### Saving Data (`phaethon.save`)

Universally serializes Datasets to disk. If no format is provided, it intelligently infers it from the file extension.

**Arguments:**

<div class="param-box">
  <div class="param-header">
    <span class="p-name">filepath</span>
    <span class="p-sep">—</span>
    <span class="p-type">str | Path</span>
  </div>
  <div class="p-desc">The destination path.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">data</span>
    <span class="p-sep">—</span>
    <span class="p-type">Dataset | DataFrame</span>
  </div>
  <div class="p-desc">The <code>Dataset</code> to serialize. Note: If saving to Parquet, you can also pass a raw Pandas/Polars DataFrame directly.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">format</span>
    <span class="p-sep">—</span>
    <span class="p-type">str</span>
  </div>
  <div class="p-desc">Explicit format override: <code>'auto'</code>, <code>'phx'</code>, <code>'parquet'</code>, or <code>'h5'</code>.</div>
</div>

<div class="param-box">
  <div class="param-header">
    <span class="p-name">**kwargs</span>
    <span class="p-sep">—</span>
    <span class="p-type">Any</span>
  </div>
  <div class="p-desc">Pass-through formatting arguments specifically for Parquet (e.g., <code>compression='snappy'</code>) or HDF5 (e.g., <code>chunks=True</code>).</div>
</div>

**Serialization Examples:**

```python
import phaethon as ptn

# 1. Native Secure Archive (Preserves SHA-256 and Physical Units)
ptn.save("telemetry.phx", ds)

# 2. Big Data Parquet (With Snappy compression via PyArrow)
ptn.save("telemetry.parquet", ds, compression="snappy")

# 3. Scientific HDF5 (Chunked, with GZIP compression)
ptn.save("telemetry.h5", ds, chunks=True, compression="gzip")
```

### Loading Data (`phaethon.load`)

Loads Parquet, HDF5, and PHX archives safely back into memory. Regardless of the input format, Phaethon guarantees strict type safety by exclusively returning a unified `ptn.Dataset`.

**Security Feature:** When loading `.phx` files, Phaethon cross-references the binary arrays against their stored SHA-256 signatures. If the file has been tampered with or corrupted, it will throw a security breach error.

**Loading Examples:**

```python
import phaethon as ptn

# Load Native
loaded_ds = ptn.load("telemetry.phx")

# Load HDF5 (Instantly restored as a Phaethon Dataset)
h5_ds = ptn.load("telemetry.h5")

print(h5_ds['vel'].dimension)
# Output: 'velocity'
```

### Safe Inspection (`phaethon.peek`)

If you are dealing with massive datasets (e.g., 50GB `.phx` files), loading them entirely into memory just to check their contents will cause Out-Of-Memory (OOM) crashes.

The `ptn.peek()` function parses the internal JSON metadata of a `.phx` archive *without* loading the arrays, returning a lightweight dictionary summary.

```python
import phaethon as ptn

meta_summary = ptn.peek("massive_simulation.phx")

print(meta_summary["Contents"])
# Output:
# {
#   'vel': 'Physics [velocity] (m/s) | Shape: [1000000] | SHA-256 Validated',
#   'temp': 'Physics [temperature] (K) | Shape: [1000000] | SHA-256 Validated'
# }
```