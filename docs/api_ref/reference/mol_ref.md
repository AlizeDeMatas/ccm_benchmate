---
layout: default
title: Molecule reference
parent: API Reference
nav_order: 7
---

<a id="molecule"></a>

# molecule

<a id="molecule.Molecule"></a>

## Molecule Objects

```python
class Molecule()
```

Molecule class to represent chemical structures using SMILES or InChI. this will include methods for different property
calculations and structure comparisons using usearch molecules.

<a id="molecule.Molecule.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name, smiles, fingerprint_dim=2048, radius=2)
```

**Arguments**:

- `name`: 
- `smiles`: 
- `fingerprint_dim`: 
- `radius`: 

<a id="molecule.Molecule.search"></a>

#### search

```python
def search(library, n=10, metric="tanimoto", using="ecfp4")
```

Search for similar molecules in a given library using a specified fingerprinting method.

**Arguments**:

- `library`: The dataset to search within.
- `n`: Number of similar molecules to return.
- `metric`: Similarity metric to use (default is "tanimoto").
- `using`: Fingerprint type to use (default is "ecfp4").

**Returns**:

A list of similar molecules from the library.

<a id="utils"></a>

# utils

<a id="utils.generate_molecule_dataset"></a>

#### generate\_molecule\_dataset

```python
def generate_molecule_dataset(smiles_files,
                              library_dir,
                              shapes=[shape_maccs, shape_ecfp4, shape_fcfp4],
                              extractor=None,
                              processes=10)
```

generates a usearch-molecules dataset from a list of molecules and associated fingerprints

along with indicies

**Arguments**:

- `molecules`: list of molecule objects
- `path`: where to write the dataset

<a id="utils.tanimoto"></a>

#### tanimoto

```python
def tanimoto(a, b)
```

computes the tanimoto distance between two boolean numpy arrays

**Arguments**:

- `a`: fingerprint a
- `b`: fingerprint b

**Returns**:

tanimito similarity

