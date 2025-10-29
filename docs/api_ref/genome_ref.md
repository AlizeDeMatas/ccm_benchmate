<a id="genome"></a>

# genome

<a id="genome.Genome"></a>

## Genome Objects

```python
class Genome()
```

<a id="genome.Genome.__init__"></a>

#### \_\_init\_\_

```python
def __init__(genome_fasta,
             gtf,
             name,
             db_conn,
             description=None,
             transcriptome_fasta=None,
             standalone=False,
             proteome_fasta=None,
             create=True)
```

**Arguments**:

- `gtf_path`: Path to the GTF file
- `genome_fasta`: Path to the genome fasta file
- `transcriptome_fasta`: Path to the transcriptome fasta file
- `proteome_fasta`: Path to the proteome fasta file
- `db_conn`: database connection object this is a sqlalchemy engine
- `taxon_id`: taxon id of the genome

<a id="genome.Genome.genes"></a>

#### genes

```python
def genes(gene_ids=None, range=None, ignore_strand=True)
```

Gene id or range if range is provided it will return the genes in that range depending on the overlap type

**Arguments**:

- `id`: Gene id, that used in the gtf file
- `range`: A GenomicRange object
- `ignore_strand`: whether to ignore strand this will return all the genes in the range regardless of strand

**Returns**:

a GenomicRangesDict object with the genes in it, each key is the gene name and the value is a GenomicRange object

<a id="genome.Genome.transcripts"></a>

#### transcripts

```python
def transcripts(gene_ids=None,
                ids=None,
                range=None,
                ignore_strand=True,
                group_by_gene=True)
```

return transcripts by gene id, transcript id or range

**Arguments**:

- `gene_ids`: return transcripts for these gene ids
- `ids`: return transcripts with these transcript ids
- `range`: return transcripts in this range
- `ignore_strand`: ignore strand when searching by range
- `group_by_gene`: whether to group the returned transcripts by gene id, if true the returned object
will have gene ids as keys and GenomicRangesList as values, if false the returned object will have transcript ids as keys and GenomicRange as values

**Returns**:

a genomic ranges dict object

<a id="genome.Genome.exons"></a>

#### exons

```python
def exons(transcript_ids=None,
          range=None,
          group_by_transcript=True,
          ignore_strand=True)
```

same as genes but will need to search by transcript not gene, if you do not know the transcript search for it with transcripts first

**Arguments**:

- `transcript_id`: return all exons for this transcript id
- `id`: return exon with this id
- `range`: return exons in this range
- `group_by_transcript`: whether to group the returned exons by transcript id, if true the returned object
- `ignore_strand`: whether to ignore strand when searching by range

**Returns**:

a genomic ranges dict object, if not grouped by transcript the keys will be exon ids otherwise the keys will be transcript ids

<a id="genome.Genome.coding"></a>

#### coding

```python
def coding(transcript_ids=None,
           range=None,
           group_by_transcript=True,
           ignore_strand=True)
```

same as exons return all the coding sequences for a transcript or a list of transcripts

**Arguments**:

- `transcript_id`: return all coding sequences for this transcript id
- `id`: return coding sequence with this id
- `range`: return coding sequences in this range
- `group_by_transcript`: whether to group the returned coding sequences by transcript id, if true the returned object

**Returns**:

a genomic ranges dict object, if not grouped by transcript the keys will be coding sequence ids otherwise the keys will be transcript ids

<a id="genome.Genome.three_utr"></a>

#### three\_utr

```python
def three_utr(transcript_ids=None, range=None, ignore_strand=True)
```

return all the 3' utrs for a transcript or a list of transcripts

**Arguments**:

- `transcript_ids`: return 3' utrs for these transcript ids
- `range`: return 3' utrs in this range
- `ignore_strand`: regardless of strand

**Returns**:

a genomic ranges dict object with transcript ids as keys and GenomicRangesList as values, the utrs are not described as
separate exons but the exons are merged into one if that utr spans multple exons. Additionally if the utrs ends in the middle
of an exon the utr will end there.

<a id="genome.Genome.five_utr"></a>

#### five\_utr

```python
def five_utr(transcript_ids=None, ids=None, range=None, ignore_strand=True)
```

return all the 5' utrs for a transcript or a list of transcripts

**Arguments**:

- `transcript_ids`: return 3' utrs for these transcript ids
- `range`: return 3' utrs in this range
- `ignore_strand`: regardless of strand

**Returns**:

a genomic ranges dict object with transcript ids as keys and GenomicRangesList as values, the utrs are not described as
separate exons but the exons are merged into one if that utr spans multple exons. Additionally if the utrs ends in the middle
of an exon the utr will end there.

<a id="genome.Genome.introns"></a>

#### introns

```python
def introns(transcript_ids=None,
            ids=None,
            range=None,
            group_by_transcript=True,
            ignore_strand=True)
```

return all the introns for a transcript or a list of transcripts

**Arguments**:

- `transcript_id`: return introns for this transcript id
- `id`: return intron with this id (introns usually are not descibed in a gtf, so this id may not be very useful since
it is an auto incremented id)
- `range`: return introns in this range
- `group_by_transcript`: return introns grouped by transcript
- `ignore_strand`: whether to ignore strand when searching by range

**Returns**:

return: a genomic ranges dict object, if not grouped by transcript the keys will be intron ids otherwise the keys will be transcript ids

<a id="genome.Genome.get_sequence"></a>

#### get\_sequence

```python
def get_sequence(genomic_range, type='genome')
```

Get the sequence of a genomic range. This takes a single genomc range you can iterate over a GenomicRangeList or GenomicRangeDict

**Arguments**:

- `genomic_range`: GenomicRange object

**Returns**:

sequence as string

<a id="genome.Genome.add_annotation"></a>

#### add\_annotation

```python
def add_annotation(table, row_id, annots)
```

add arbitrary annotations as a dictionary to a specific row in a specific table

**Arguments**:

- `table`: which table to add the annotations to
- `id`: which row id to add the annotations to, this is the datbase internal id not the gene_id or transcript_id, those
ids can be found in the annotations of each row
- `annots`: a dictionary of annotations to add

**Returns**:

None but the database will be updated

