---
layout: default
title: APIs
parent: Modules
nav_order: 1
---

The goal of the module is to provide a unified(-ish) interface to different biological databases. The module has interfaces
the following databases:

+ [Uniprot](unprot.org): This is a database of protein sequences and annotations. The module provides a way to search for proteins
and their respective annotations. The entirety of the Uniprot database can be searched using the module, including variation
isoforms and mutagenesis endpoints. These are then integrated into a single dictionary that can be used to access the data.
+ [NCBI](ncbi.nlm.nih.gov): This is a database of nucleotide sequences and annotations. The module provides a way to search for all 
of the NCBI databases, including nucleotide sequences, protein sequences, gene annotations, and more. While you can search pubmed
using this module, the [literature module](literature.md) is better suited for that purpose (see below). 
+ [Ensembl](ensembl.org): This is a database of genomic sequences and annotations. The module provides a way to search for gene variants
mapping between different coordinates systems, and more. The module also provides a way to search for genes and their annotations,
annotate variants, query cross-references from different databases and more. 
+ [stringdb](stringdb.org): This is a database of protein-protein interactions. The module provides a way to search for protein-protein interactions. 
Additionally you can use the Biogrid and IntAct endpoints under others to perform similar queries.
+ [reactome](reactome.org): Reactome is a comprehensive database of biolgicla reaction, proteins and pathways. You can query many of the endpoints using 
this submodule
+ [rnacentral](rnacentral.org): RnaCentral *the* non-coding RNA sequence database, this is different from the NCBI genes in that it is dedicated to non-coding
sequences. 
+ [BioGrid]("https://thebiogrid.org/"): Biogrid is a biomedical interaction repository that contains information about protein-protein and protein-chemical 
interactions that are mostly manually curated at different levels. You will need a free API key to be able to use this module. You can obtain one [here](https://webservice.thebiogrid.org/)
+ [IntAct](https://www.ebi.ac.uk/intact/home): Simlar to BioGrid this database contains interaction data. You can query this database to arbitrary depth
to obtain information about different biological complexes and much more. 
+ [AlphaGenome](https://www.alphagenomedocs.com/index.html): AlphaGenome is a server running the latest alphagenome models
for variant, sequence and genomic interval consequence/feature predictions. 

You can see detailed usage examples for each of these publicly available databases in their respective documentation. Not every database provides
a robus api to query, nor their documentaion is exhaustive or even well prepared. We are a small team and we are trying to generate
as many resources as we can while being mindful or the work that is required to achieve the highest yield in the shortest amount of time. 

