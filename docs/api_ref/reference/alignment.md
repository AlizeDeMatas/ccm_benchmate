---
layout: default
title: Alignment module reference
parent: API Reference
nav_order: 8
---

<a id="mmseqs"></a>

# mmseqs

<a id="mmseqs.MMSeqs"></a>

## MMSeqs Objects

```python
class MMSeqs()
```

Corrected MMseqs2 wrapper:
- Always creates query DB via `createdb`
- Supports single and paired alignment (`pairaln`)
- GPU with padded DB
- Flexible extra args

<a id="mmseqs.MMSeqs.create_database"></a>

#### create\_database

```python
def create_database(
        fasta_path: str,
        db_path: str,
        gpu_padded: bool = False,
        extra_args: Optional[Union[List[str], Dict[str, str]]] = None) -> str
```

Create target database (optionally padded for GPU).

<a id="mmseqs.MMSeqs.pad_db"></a>

#### pad\_db

```python
def pad_db(old_db, new_db, **kwargs)
```

create a padded db from an exising one

:param old_db: old db to pad
:param new_db: new db path
:return the path of the new db if all goes well


<a id="mmseqs.MMSeqs.search"></a>

#### search

```python
def search(query: Union[str, List[str]],
           target_db: str,
           output_a3m: str,
           output_tsv: str,
           use_gpu: bool = False,
           sensitivity: float = 5.7,
           max_seqs: int = 1000,
           evalue: float = 1e-3,
           extra_search_args: Optional[Union[List[str], Dict[str,
                                                             str]]] = None,
           extra_result2msa_args: Optional[Union[List[str], Dict[str,
                                                                 str]]] = None,
           tmp_dir: Optional[str] = None)
```

Full pipeline: query → search/pairaln → A3M + TSV

# blast

<a id="blast.Blast"></a>

## Blast Objects

```python
class Blast()
```

<a id="blast.Blast.__init__"></a>

#### \_\_init\_\_

```python
def __init__(path=None, dbtype="n")
```

initiate a Blast class instance

**Arguments**:

- `path` (`str`): path of the executable if none will check $PATH
- `db` (`str`): path and name of the blast database if exists if not it can be created using create_db
- `dbtype` (`str`): type of the database n for nucleotide p for protein

<a id="blast.Blast.create_db"></a>

#### create\_db

```python
def create_db(fasta,
              output_path,
              dbname,
              dbtype="n",
              overwrite=True,
              arg_dict=None)
```

create a blast databse and stor in self.db

**Arguments**:

- `dbtype` (`str`): database type n for nucleotide and p for protein
- `fasta` (`str`): path of the fasta file only fasta is implemented
- `output_path` (`str`): output path for the database this is different from the databse name
- `dbname` (`str
:param overwrite: if there is already a self.db you can override this just edits the class instance value
dooes not touch the databse`): database name so self.db will be output_path/dbname
- `arg_dict` (`dict`): a dictionary of arguments, if left empty will use default values see blast documentation

**Returns**:

`None`: nothing just puts the new database path in self.db after database creation

<a id="blast.Blast.search"></a>

#### search

```python
def search(seq,
           db,
           output_type="tabular",
           exec="blastn",
           arg_dict=None,
           cols=None)
```

Search an existing blast database with a sequence class instance

**Arguments**:

- `seq`: a benchmate.sequence.sequence.Sequence instance
- `db`: the path and name of the database
- `output_type`: tabular or json
- `exec`: what to use for serach depends on the type of sequence being searched
- `arg_dict`: additional arguments to blast
- `cols`: what columns to return if you are returning a table

**Returns**:

pd.DataFrame of dict

<a id="utils"></a>

# utils

<a id="utils.SinglePassFastaIndex"></a>

## SinglePassFastaIndex Objects

```python
class SinglePassFastaIndex()
```

this is a tiny class to access MSA a3m files, these files look like fasta but they are not reall so tools
that deal with them have issues. This is not really a faster solution but a solution.

<a id="utils.SinglePassFastaIndex.__init__"></a>

#### \_\_init\_\_

```python
def __init__(fasta_path, delim="_")
```

constructor, the goal is to create an index of the entries, sometimes you will get multiple entries with the same name
these will have other things next to the name, a combination of these create a unique entry

<a id="foldseek"></a>

# foldseek

<a id="foldseek.FoldSeek"></a>

## FoldSeek Objects

```python
class FoldSeek()
```

A Python wrapper for FoldSeek with support for:
- Querying PDB structures (single or directory) against a database → A3M + TSV output
- Creating FoldSeek databases (standard or GPU-padded)
- GPU acceleration (if DB supports it)
- Flexible extra arguments

<a id="foldseek.FoldSeek.__init__"></a>

#### \_\_init\_\_

```python
def __init__(foldseek_bin: str = "foldseek")
```

Initialize the wrapper.

**Arguments**:

- `foldseek_bin` - Path to the FoldSeek executable (default: assumes in PATH)

<a id="foldseek.FoldSeek.create_database"></a>

#### create\_database

```python
def create_database(pdb_dir: str,
                    db_path: str,
                    gpu_padded: bool = False,
                    extra_args: Optional[Union[List[str], Dict[str,
                                                               str]]] = None,
                    tmp_dir: Optional[str] = None) -> str
```

Create a FoldSeek database from a directory of PDB/CIF files.

**Arguments**:

- `pdb_dir` - Directory containing .pdb, .cif, .pdb.gz, .cif.gz files
- `db_path` - Output database prefix (without extension)
- `gpu_padded` - If True, create padded database for GPU
- `extra_args` - Additional arguments as list or dict
- `tmp_dir` - Temporary directory (if None, system temp is used)
  

**Returns**:

  Path to created database

<a id="foldseek.FoldSeek.pad_db"></a>

#### pad\_db

```python
def pad_db(old_db, new_db, **kwargs)
```

create a padded db from an exising one

:param old_db: old db to pad
:param new_db: new db path
:return the path of the new db if all goes well


<a id="foldseek.FoldSeek.search"></a>

#### search

```python
def search(query_pdb: str,
           target_db: str,
           output_a3m: str,
           output_tsv: str,
           use_gpu: bool = False,
           sensitivity: float = 7.5,
           max_accept: int = 100000,
           evalue: float = 1e-3,
           extra_search_args: Optional[Union[List[str], Dict[str,
                                                             str]]] = None,
           extra_result2msa_args: Optional[Union[List[str], Dict[str,
                                                                 str]]] = None,
           tmp_dir: Optional[str] = None)
```

Run FoldSeek search and generate A3M + TSV from a PDB query.

**Arguments**:

- `query_pdb` - Path to query PDB/CIF file
- `target_db` - FoldSeek database to search against
- `output_a3m` - Output A3M file path
- `output_tsv` - Output TSV file path
- `use_gpu` - Enable GPU (FoldSeek will error if DB not padded or no GPU)
- `sensitivity` - Search sensitivity (higher = slower, more sensitive)
- `max_accept` - Maximum number of alignments to accept
- `evalue` - E-value threshold
- `extra_search_args` - Extra args for `search`
- `extra_result2msa_args` - Extra args for `result2msa`
- `tmp_dir` - Custom temporary directory
  

**Notes**:

  GPU errors are caught and reported (FoldSeek handles compatibility).

