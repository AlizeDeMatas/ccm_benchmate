<a id="__init__"></a>

# \_\_init\_\_

<a id="variant"></a>

# variant

<a id="variant.BaseVariant"></a>

## BaseVariant Objects

```python
class BaseVariant()
```

Base class for all variant types.

<a id="variant.BaseVariant.show_annotations"></a>

#### show\_annotations

```python
def show_annotations() -> Dict[str, Any]
```

Return annotation types.

<a id="variant.BaseVariant.query_annotation"></a>

#### query\_annotation

```python
def query_annotation(key: str) -> Any
```

Query a specific annotation.

<a id="variant.BaseVariant.add_annotation"></a>

#### add\_annotation

```python
def add_annotation(key: str, value: Any) -> None
```

Add or update an annotation.

<a id="variant.SequenceVariant"></a>

## SequenceVariant Objects

```python
class SequenceVariant(BaseVariant)
```

Class for SNV and Indel variants.

<a id="variant.SequenceVariant.__len__"></a>

#### \_\_len\_\_

```python
def __len__()
```

Return the length of the variant.

<a id="variant.SequenceVariant.__str__"></a>

#### \_\_str\_\_

```python
def __str__()
```

Return a string representation of the variant.

<a id="variant.SequenceVariant.__repr__"></a>

#### \_\_repr\_\_

```python
def __repr__()
```

Return a detailed string representation of the variant.

<a id="variant.StructuralVariant"></a>

## StructuralVariant Objects

```python
class StructuralVariant(BaseVariant)
```

Class for SV/CNV variants (INS, DEL, INV, DUP, BND, CNV).

<a id="variant.StructuralVariant.__len__"></a>

#### \_\_len\_\_

```python
def __len__()
```

Return the length of the variant.

<a id="variant.StructuralVariant.__str__"></a>

#### \_\_str\_\_

```python
def __str__()
```

Return a string representation of the variant.

<a id="variant.StructuralVariant.__repr__"></a>

#### \_\_repr\_\_

```python
def __repr__()
```

Return a detailed string representation of the variant.

<a id="variant.TandemRepeatVariant"></a>

## TandemRepeatVariant Objects

```python
class TandemRepeatVariant(BaseVariant)
```

Class for Tandem Repeat variants (SRWGS and LRWGS).

<a id="variant.TandemRepeatVariant.__len__"></a>

#### \_\_len\_\_

```python
def __len__()
```

Return the length of the variant.

<a id="variant.TandemRepeatVariant.__str__"></a>

#### \_\_str\_\_

```python
def __str__()
```

Return a string representation of the variant.

<a id="variant.TandemRepeatVariant.__repr__"></a>

#### \_\_repr\_\_

```python
def __repr__()
```

Return a detailed string representation of the variant.

<a id="utils"></a>

# utils

<a id="utils.infer_variant_type"></a>

#### infer\_variant\_type

```python
def infer_variant_type(ref_allele, alt_allele)
```

Infer the variant type based on reference and alternative alleles.

**Arguments**:

- `ref_allele` _str_ - Reference allele sequence
- `alt_allele` _str_ - Alternative allele sequence
  

**Returns**:

- `str` - Inferred variant type ('snv', 'deletion', 'insertion', 'indel', 'duplication', 'translocation')

<a id="utils.to_hgvs"></a>

#### to\_hgvs

```python
def to_hgvs(variant)
```

Convert genomic coordinates and variant details to HGVS notation, inferring variant type.

**Arguments**:

- `chromosome` _str_ - Chromosome name (e.g., '1', 'X', 'chr1')
- `position` _int_ - Genomic position of the variant
- `ref_allele` _str_ - Reference allele or sequence
- `alt_allele` _str_ - Alternative allele or sequence
  

**Returns**:

- `str` - HGVS notation for the variant

