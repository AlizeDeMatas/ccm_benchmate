from PIL.features import featuresfrom PIL.features import featuresfrom sympy.physics.units.definitions.dimension_definitions import information

# API's module

This module includes the API classes for the ccm_demo application. Each API class is responsible for 
handling a specific type of request and returning the appropriate response. The classes assume that you know what you are
looking for and gives you the power to link different public databases to each other programmatically. Each of the apis
return a dictionary with varying degrees and the parsing also is different. The API classes are as follows:

The apis marked with (WIP) are still under development and may not be fully functional yet.

+ Ensembl
+ Uniprot
+ NCBI E utils
+ Reactome (WIP)
+ stringdb
+ Intact
+ RNAcentral
+ Rfam (WIP)
+ GTEx (WIP)
+ EBI tools (WIP)
+ BioGrid
+ Omnipath (WIP)


These APIs are used to retrieve data from various biological databases and perform operations such as searching for genes, 
paper etc. Here is a small breakdown of the apis and the overall structure what they return. Depending on the api the
and the parameters you pass to the api you will get different results. The API classes are designed to be flexible and
allow for easy customization and extension. You can add new API classes or modify existing ones to suit your needs.

# API classes

## Ensembl

The Ensembl API class is used to retrieve data from the Ensembl database. It provides methods for searching for genes,
transcripts, not all the endpoints are implemented and not sure if they ever will be. Below is a list of the endpoints

### Variation

The variation API is used to retrieve information about genetic variations. It provides methods for serching for publications
given a certain variant. This can be taking an rsID and converting into other formats like HGVS or Ensembl ID. It also provides
methods searching for publications given a certain variant. This can be taking an rsID and converting into other formats like HGVS or Ensembl ID.

```python
from ccm_demo.apis.ensembl import Ensembl
ensembl=Ensembl()
info=ensembl.variation("rs56116432")
```



This assumes that you know the name of the variant that you are interested in. If you do not know if there is an rsid or something
similar you can use the VEP endpoint to get the information. The VEP endpoint is used to retrieve information about genetic variations and their effects on genes. 

If you are using the translation method this will convert different ways to represent the variant

```python
ensembl.variation("rs56116432", method="translate")

The publication method returns all the variants mentioned in a publication not the other way around. For that you might want to use
the VEP api. 

```python
ensembl.variation("26318936", method="publication", pubtype="pubmed")

```

### VEP

This is an api that is used to retrieve information about genetic variations and their effects on genes. It provides methods for searching for several
tools and databases. There is a large list of tools that are available. Depending on the variant not all of them will return a value, for example
you will not get an alphamissense record for an intronic variant. It will not be null, it just wont be where. So plan your scripts accordingly. 

Please see [here](https://rest.ensembl.org/documentation/info/vep_region_get) for the full list of tools that are available. Currently,
only region method is implemented and it may stay that way. For getting publication and allele frequency information you will need to specify
the check_existing method as True. If you do not specify any tools it will return basic information about the variant. 

This section is still under development and is not functional as relies on a Variant class (see it's documentation) that is not yet implemented.
You might getway with it by implementing a simpla variant class on your own like so in the meantime. 

```python
class Variant:
    def __init__(self, chrom, start, end, ref, alt):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.ref = ref
        self.alt = alt

myvar=Variant(1, 6524705, 6524705, "C", "T")

ensembl.vep(myvar, check_exisits=True)
```
This method accepts not just SNVs but also small INDEL, DEL, INS and dups, the alt needs to be what it would be on a vcf file. By default
as it normally does, VEP returns information about all consequences for example consequences on each of the transcripts. 

At any given time, VEP api will return the latest information. There is no way to search for older versions of annotations. If that is 
what you need you will need a local installation of VEP which are available in HPC.

### Phenotype

This returns all the phenotype information that is associated with a genomic range. It requires a GenomicRange
object (see it's documentation). 

```python
from ccm_demo.ranges.genomicranges import GenomicRange
grange=GenomicRange(9, 22125503, 22125502, "+")
ensembl.phenotype(grange)
```

### Sequence

This will return the sequence given an ensembl id. If you are looking for just a few things this might be useful. For a more
performant way of getting the sequence you might want to use the Genome module (see it's docmentation) and associated fasta files. 

You can specify whether you want the genomics, coding, cdna or protein sequences. You can 
add or trim 5' and 3' ends of the sequence. 

```python
ensembl.sequence("ENSG00000139618")
```
### Overlap

This will return the ensembl ids of things that map to a given region. It takes a GenomicRange object and returns the ids
and basic information about the things that map to that region. Again if you are dealing just a few things you can use this in
conjunction with the sequence apis to get what you need. 

```python
grange=GenomicRange(9, 22125503, 22125502, "+")
features=["gene", "transcript", "cds", "exon", "repeat"]
ensembl.overlap(grange, features)
```

### Xrefs

This returns all the cross references that are associated with an ensembl id. This is useful to get ids of things for other
databases that in turn you can use to search. 

### Mapping

This can convert cDNA/CDS/protein coodinates and genomic coordinates. Because these are arbitrary coordinates you need to
pass the coodrinates you are interested in. 

```python
ensembl.mapping("ENSP00000288602", 100, 300)
```

### Info

This method is meant to be used as an exploratory mechanism before you automate your api calls and research needs. It provides
information about different datasets that are currently available in the API and how they can be queried. I am currenly only
retrieving species, divisions and consequences (for variation and VEP). The rest of the information is not yet implemented.

# NCBI E utils

This is a very thin wrapper around the NCBI E utils API. It has features that allows
