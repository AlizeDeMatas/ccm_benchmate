# Variant Module

This module defines classes for representing and annotating different types of genetic variants, including SNVs, indels, structural variants, and tandem repeats.
This module is not meant for you to store your variant for a whole genome or exome sequencing. Currenlt there is no support for 
storing large number of variants (in the order of 100s of millions, which would be about 40-50 WGS samples). That support might come in the future. 

If you have a smaller subset of variants that is the result of a filtered vcf file you might be able to use this to represent them and
store them in the knowledegbase database. 

---

## Classes

### `BaseVariant`

**Description:**  
Base class for all variant types. Stores core attributes such as chromosome, position, filter status, ID, and annotations.

**Public Methods & Usage:**
```python
from ccm_benchmate.variant.variant import BaseVariant

# Create a base variant
variant = BaseVariant(chrom="1", pos=12345, filter="PASS")

# Add an annotation
variant.add_annotation("impact", "HIGH")

# Query an annotation
impact = variant.query_annotation("impact")
```

---

### `SequenceVariant`

**Description:**  
Represents SNV and indel variants. Extends `BaseVariant` with reference/alternate alleles and sample/callset-specific fields.

**Public Methods & Usage:**
```python
from ccm_benchmate.variant.variant import SequenceVariant

# Create a sequence variant
seq_var = SequenceVariant(
    chrom="1", pos=12345, ref="A", alt="T", qual=99.0, gt="0/1", dp=30
)

# Add and query annotations (inherited)
seq_var.add_annotation("gene", "BRCA1")
gene = seq_var.query_annotation("gene")
```

---

### `StructuralVariant`

**Description:**  
Represents structural variants (e.g., INS, DEL, INV, DUP, BND, CNV). Extends `BaseVariant` with SV-specific fields.

**Public Methods & Usage:**
```python
from ccm_benchmate.variant.variant import StructuralVariant

# Create a structural variant
sv = StructuralVariant(
    chrom="2", pos=20000, svtype="DEL", end=20500, svlen=500, gt="1/1"
)

# Annotate and query
sv.add_annotation("clinical_significance", "pathogenic")
significance = sv.query_annotation("clinical_significance")
```

---

### `TandemRepeatVariant`

**Description:**  
Represents tandem repeat variants, including repeat motif, allele length, and sample-specific metrics.

**Public Methods & Usage:**
```python
from ccm_benchmate.variant.variant import TandemRepeatVariant

# Create a tandem repeat variant
tr = TandemRepeatVariant(
    chrom="3", pos=30000, end=30020, motif="CAG", al=10, gt="0/1"
)

# Annotate and query
tr.add_annotation("repeat_expansion", True)
is_expanded = tr.query_annotation("repeat_expansion")
```

---

**Note:**  
All classes support flexible annotation via `add_annotation` and `query_annotation`.  
Refer to class docstrings for detailed parameter descriptions.