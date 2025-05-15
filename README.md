
# CCM Demo Package

A Python package for computational biology and drug discovery, providing tools for working with biological sequences, structures, and molecular interactions.

## Module Structure

### 📁 apis/
Gateway to biological databases:
- Unified access to PDB, UniProt, NCBI
- Download structures from PDB/AlphaFold DB 
- Query protein/gene information
- Upload/download sequence data

### 📁 binders/
Molecular binding analysis tools:
- Classes:
  - `MoleculeBinder`: Small molecule binding analysis
  - `PeptideBinder`: Early stage peptide binding (experimental)
- Features:
  - Pocket detection using fpocket
  - Molecule generation via Pocket2Mol
  - Chemical similarity search (ECFP4, FCFP4, MACCS fingerprints)
  - Structure coordinate calculations
  - RDKit integration

### 📁 container_runner/
Container orchestration:
- Unified interface for Singularity/Docker 
- Job submission to SLURM clusters
- Mount point and volume management
- Container execution monitoring
- Error handling and logging

### 📁 genome/
Genomic data management:
- Database creation from sequence files
- Gene/transcript/exon queries
- Sequence extraction tools
- Integration with sequence module

### 📁 knowledge_base/
Biological data organization:
- Structured storage for biological data
- Data format standardization
- Query interfaces and caching
- Version tracking

### 📁 literature/
Research paper processing:
- Publication searches (PubMed/arXiv)
- Text and metadata extraction 
- Reference management
- Content parsing

### 📁 ranges/
Genomic interval tools:
- Range operations and arithmetic
- Overlap detection
- Coordinate system handling
- BED file processing

### 📁 sequence/
Biological sequence handlers:
- Sequence data structures
- Multiple sequence alignment
- BLAST integration
- FASTA file operations

### 📁 structure/
Protein structure tools:
- PDB file operations
- Structure property calculations
- Structure alignment
- Format conversions

## Requirements

### Dependencies
- Python 3.8+
- BioPython
- RDKit
- PyTorch
- Pandas/NumPy

### External Tools
- Singularity/Docker
- MMseqs2 
- fpocket
- SLURM (optional)

## Development Status

- Container management, sequence, and structure modules are stable
- Binders module is partially implemented
- Other modules under active development

## License

[License details pending]

---
Developed by the Centre for Computational Medicine