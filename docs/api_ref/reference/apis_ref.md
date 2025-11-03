---
layout: default
title: APIs module reference
parent: API Reference
nav_order: 1
---

<a id="reactome"></a>

# reactome

<a id="reactome.Reactome"></a>

## Reactome Objects

```python
class Reactome()
```

<a id="reactome.Reactome.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

constructor reactome class, there are no parameters, while getting constructed obtains the latest information from the api

<a id="reactome.Reactome.search"></a>

#### search

```python
@api_call
def search(query,
           species=None,
           compartments=None,
           keywords=None,
           types=None,
           start=0,
           num_rows=1000,
           cluster=True,
           force_filters=True)
```

general query that return specific reactome ids for different types

**Arguments**:

- `query`: a string to be searched
- `species`: a species name see self.show_fields["species"]
- `compartments`: compartment name see self.show_fields["compartment"]
- `keywords`: see self.show_fields["keyword"]
- `types`: see self.show_fields["type"]
- `start`: where to start the search, default is 0
- `num_rows`: number of rows to return default is 1000 (shouldbe more than enough)
- `cluster`: whether the cluster the results by different types default True
- `force_filters`: if True and nothing is found will return an empty dict otherwise will try again w/o any filters

**Returns**:

response dict or an error

<a id="reactome.Reactome.get_details"></a>

#### get\_details

```python
@api_call
def get_details(id)
```

get detailed information about a reactome entry, you need the reactome id

**Arguments**:

- `id`: reactome id

**Returns**:

response dict

<a id="reactome.Reactome.show_values"></a>

#### show\_values

```python
def show_values(field)
```

show available values for a given field

**Arguments**:

- `field`: see show fields

**Returns**:

a list

<a id="reactome.Reactome.show_fields"></a>

#### show\_fields

```python
def show_fields()
```

show available fields for filtering

**Returns**:

a list

<a id="uniprot"></a>

# uniprot

<a id="uniprot.UniProt"></a>

## UniProt Objects

```python
class UniProt()
```

<a id="uniprot.UniProt.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

constructor for the UniProt class, which is used to gather data from the UniProt API and process it in a readable format.

<a id="uniprot.UniProt.search"></a>

#### search

```python
def search(query, page_size=500)
```

free text query for the UniProt API

**Arguments**:

- `query`: text query, anything that can be searched on the UniProt website
- `page_size`: number of items per request, this is not the total number of results, it will get results until
there are no more pages

**Returns**:

a dataframe of name, UniProt ID, gene name, organism and a brief description

<a id="uniprot.UniProt.get_info"></a>

#### get\_info

```python
@api_call
def get_info(uniprot_id,
             consolidate_refs=True,
             get_variations=True,
             get_interactions=True,
             get_mutagenesis=True,
             get_isoforms=True)
```

gather all the information about a specific entry described by the UniProt ID

**Arguments**:

- `uniprot_id`: UniProt accession
- `consolidate_refs`: whether to consolidate all the references from the different sections into a single list
- `get_variations`: whether to call the variations api
- `get_interactions`: whether to call the interactions api
- `get_mutagenesis`: whether to call the mutagenesis api
- `get_isoforms`: whether to call the isoforms api

<a id="uniprot.UniProt.get_features"></a>

#### get\_features

```python
def get_features(results, feature_types=None)
```

filter already extracted features by type, this just filters the features from the json response

**Arguments**:

- `feature_types`: type of the feature to filter by

**Returns**:

the features

<a id="uniprot.UniProt.get_comments"></a>

#### get\_comments

```python
def get_comments(results, types=None)
```

get already extracted comments from the json response

**Arguments**:

- `types`: comment types to filter by

**Returns**:

comments

<a id="uniprot.Interactions"></a>

## Interactions Objects

```python
class Interactions()
```

<a id="uniprot.Interactions.__init__"></a>

#### \_\_init\_\_

```python
def __init__(uniprot)
```

query the UniProt API for interaction data

**Arguments**:

- `uniprot`: UniProt class

<a id="uniprot.Isoforms"></a>

## Isoforms Objects

```python
class Isoforms()
```

<a id="uniprot.Isoforms.__init__"></a>

#### \_\_init\_\_

```python
def __init__(uniprot)
```

query the UniProt API for isoform data, not all proteins have isoforms and there will be warnings if none are found

**Arguments**:

- `uniprot`: uniprot class

<a id="uniprot.Mutagenesis"></a>

## Mutagenesis Objects

```python
class Mutagenesis()
```

<a id="uniprot.Mutagenesis.__init__"></a>

#### \_\_init\_\_

```python
def __init__(uniprot)
```

query the UniProt API for mutagenesis data this is different than variations, these are not variations that are

seen in the wild but from experimental data

**Arguments**:

- `uniprot`: UniProt class

<a id="others"></a>

# others

<a id="others.BioGrid"></a>

## BioGrid Objects

```python
class BioGrid()
```

<a id="others.BioGrid.__init__"></a>

#### \_\_init\_\_

```python
def __init__(access_key)
```

Initialize the BioGrid class with the provided access key.

**Arguments**:

- `access_key`: you can get one from https://webservice.thebiogrid.org/

<a id="others.BioGrid.interactions"></a>

#### interactions

```python
@api_call
def interactions(gene_list, evidence_types=None, organism=None)
```

Get the interactions for the given gene list.

**Arguments**:

- `gene_list`: list of genes
- `id_types`: the type of the identifier, e.g. "entrez", "uniprot", "ensembl"
- `evidence_types`: see self.evidence_types

**Returns**:

a pandas dataframe with the interactions and kinds of evidences that support them

<a id="others.IntAct"></a>

## IntAct Objects

```python
class IntAct()
```

<a id="others.IntAct.intact_search"></a>

#### intact\_search

```python
@api_call
def intact_search(ebi_id, page=0)
```

search intact database

**Arguments**:

- `ebi_id`: ebi
- `page`: which page to start from, this is more of a precaution for very large searches, if you lose connection you can
resume from the last page you got data from, default 0

**Returns**:

a dataframe of all interactions found

<a id="others.AlphaGenome"></a>

## AlphaGenome Objects

```python
class AlphaGenome()
```

<a id="others.AlphaGenome.__init__"></a>

#### \_\_init\_\_

```python
def __init__(access_key)
```

Create an AlphaGenome object. this is used to query the alphagenome api, but unlike other api calls this does

not return and api_call dataclass instance, instead it returns depending on the method, a variant, a genomic_range or
a dataframe will be returned

**Arguments**:

- `access_key`: your alphagenome api key, you can get one from their website.

<a id="others.AlphaGenome.predict_variant"></a>

#### predict\_variant

```python
def predict_variant(variants,
                    interval_size="SEQUENCE_LENGTH_2KB",
                    organism="human")
```

for a given list of variants predict their consequences, this does not mean you can pass a whole vcf file to it

but you can do a few dozen at a time no problem.

**Arguments**:

- `variants`: list of variant objects, they do not need to have annotations
- `interval_size`: which interval should we consider, default 2KB
- `organism`: which organism should we consider, default human the other option is mouse, that's it.

**Returns**:

a benchmate.Variant.SequenceVariant instances, the same ones passed to the function but with annotations

<a id="others.AlphaGenome.predict_sequence"></a>

#### predict\_sequence

```python
def predict_sequence(sequences,
                     ontology_terms,
                     interval_size="SEQUENCE_LENGTH_2KB",
                     output_types=None,
                     organism="human")
```

predict features of a list of sequences, if you have only one you should pass [sequence]

**Arguments**:

- `sequences`: list of benchmate.sequences.Sequence objects
- `ontology_terms`: which ontology terms to use if you do not specify any we'll use all of them
- `interval_size`: interval size to consider, default 2KB but if needs to be longer than your sequence
- `output_types`: see self.ouput_types or get them all (if none)
- `organism`: which organism to consider, default human the other option is mouse, that's it

**Returns**:

a list of benchmate.sequences.Sequence objects, the same ones with the features property filled in

<a id="others.AlphaGenome.predict_interval"></a>

#### predict\_interval

```python
def predict_interval(granges,
                     ontology_terms,
                     interval_size="SEQUENCE_LENGTH_2KB",
                     output_types=None,
                     organism="human")
```

predict things about an interval,

**Arguments**:

- `granges`: a list of granges or a granges list object, if you have only one grange then pass it as a list [grange]
- `ontology_terms`: which ontology terms to use
- `interval_size`: interval size to consider, default 2KB, it needs to be longer then len(grange)
- `output_types`: see above
- `organism`: see above

**Returns**:

a list of granges, with annotations

<a id="others.AlphaGenome.mutagenesis"></a>

#### mutagenesis

```python
def mutagenesis(granges,
                scorers,
                mutagenesis_region=None,
                interval_size="SEQUENCE_LENGTH_2KB",
                output_types=None,
                organism="human")
```

Perform in-silico mutagenesis for all the sequences in the range you provided

**Arguments**:

- `granges`: list of granges
- `scorers`: list of scorers, see self.scorers
- `interval_size`: which interval size to consider, default 2KB, it needs to be longer then len(grange)
- `mutagenesis_region`: which region of the sequence to mutate extensively, this needs to be shorter than your
interval size, the method picks the center of the rage and mutagenesis_region/2 on each side

**Returns**:

a dataframe of scores or a list of dataframe of scores if you picked more than one scorer, if you get
greedy and ask for all the things the server might kick you out.

<a id="rnacentral"></a>

# rnacentral

<a id="rnacentral.RnaCentral"></a>

## RnaCentral Objects

```python
class RnaCentral()
```

<a id="rnacentral.RnaCentral.get_information"></a>

#### get\_information

```python
@api_call
def get_information(id: str,
                    get_xrefs: bool = True,
                    get_publications: bool = True)
```

Get information about a specific RNAcentral entry.

**Arguments**:

- `id`: rnacentral identifier
- `get_xrefs`: whether to get cross-references form other databases
- `get_publications`: whether to get publications related to the entry, these will return pubmed ids

**Returns**:

a dictionary containing information about the RNAcentral entry

<a id="stringdb"></a>

# stringdb

<a id="stringdb.StringDb"></a>

## StringDb Objects

```python
class StringDb()
```

<a id="stringdb.StringDb.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

constructor for StringDb class

**Arguments**:

- `name`: some sort of identifier for the protein it support UniProt, gene name, gene name synonyms
- `species`: species id for the protein, default is human, you can taxanomy id from NCBI
- `network_depth`: how deep you want to go in the network, default is 1, if more than 1 it will re search all the
results for the next depth this will increase the time it takes to get the network and the number will increase exponentially

<a id="stringdb.StringDb.gather"></a>

#### gather

```python
@api_call
def gather(species, name, get_network=False, network_depth=1)
```

gather all the information about a specific entry

**Arguments**:

- `species`: which specices, this is to disambiguate, since homologs can have the same name across species
- `name`: name of the query
- `get_network`: whether to get the interactors of interactors
- `network_depth`: depth of the networks, this makes the queries grow exponentially.

**Returns**:

a dictionary of results, if the network depth is greater than one, under the "network" key you will
see other entries

<a id="ncbi"></a>

# ncbi

<a id="ncbi.Ncbi"></a>

## Ncbi Objects

```python
class Ncbi()
```

<a id="ncbi.Ncbi.__init__"></a>

#### \_\_init\_\_

```python
def __init__(access_key=None, email=None, collect_info=False)
```

**Arguments**:

- `api_key`: NCBI API key, you can get one from https://www.ncbi.nlm.nih.gov/account/settings/
- `email`: you can also use your email address if these are not provided the searches will be limited and there will be
stricter rate limits

<a id="ncbi.Ncbi.search"></a>

#### search

```python
@api_call
def search(db, query, retmax=100)
```

thin wrapper around the NCBI Entrez esearch

**Arguments**:

- `db`: the database to search, use show_databases to see available databases
- `query`: the query string, this can be anything that can be typed into the NCBI search bar
- `retmax`: maximum number of results to return 10000 is the api max

**Returns**:

a list of ncbi ids matching the query from that database the ids are not unique to each database so there can be
another item with the same id in another database

<a id="ncbi.Ncbi.summary"></a>

#### summary

```python
@api_call
def summary(db, id)
```

thin wrapper around the NCBI Entrez esummary

**Arguments**:

- `db`: db name
- `id`: id to get summary for, you can get the ids from the search function

**Returns**:

list of summary records

<a id="ncbi.Ncbi.fetch"></a>

#### fetch

```python
@api_call
def fetch(db, id)
```

thin wrapper around the NCBI Entrez fetch

**Arguments**:

- `db`: database name
- `id`: id to fetch

**Returns**:

list parsed from the xml

<a id="ncbi.Ncbi.show_databases"></a>

#### show\_databases

```python
def show_databases()
```

show available databases

**Returns**:

a list of strings of database names, these strings can be used in other functions

<a id="ncbi.Ncbi.get_db_info"></a>

#### get\_db\_info

```python
def get_db_info(db)
```

get database info

**Arguments**:

- `db`: name of the database fron show_databases

**Returns**:

list of parameters and how they can be searched

<a id="ensembl"></a>

# ensembl

<a id="ensembl.Ensembl"></a>

## Ensembl Objects

```python
class Ensembl()
```

Ensembl API wrapper for the Ensembl REST API.

<a id="ensembl.Ensembl.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

Initialize the Ensembl API wrapper. there are some basic variables that are set there is nothing here for the user to
set. The base url is the ensembl rest api url, the dataset is the dataset that will be used for the queries, and the
headers are the headers that will be used for the queries.

<a id="ensembl.Ensembl.variation"></a>

#### variation

```python
@api_call
def variation(id,
              method=None,
              species="human",
              pubtype=None,
              add_annotations=False)
```

Get variation information from the Ensembl REST API.

**Arguments**:

- `id`: variant id
- `method`: search method, default is None which means we will get information otherwise you can search for
publications (pmid and pmcid) or translation which converts the notations to other notations
- `species`: species to search for, default is human
- `pubtype`: 

**Returns**:

returns a detailed dict with the variation information depending on the parameters described above

<a id="ensembl.Ensembl.vep"></a>

#### vep

```python
@api_call
def vep(species, variant, tools, check_existing=True)
```

"

Get variant effect prediction from the Ensembl REST API.

**Arguments**:

- `species`: species to search for
- `variant`: variant to search for, must be a Variant object
- `tools`: tools to use for the prediction, default is None which means we will just return basic information
- `check_existing`: check population frequencies from gnomad and 1kg

**Returns**:

variant effect prediction a detailed dict, not all tools are compatible with all variants and each other

<a id="ensembl.Ensembl.phenotype"></a>

#### phenotype

```python
@api_call
def phenotype(grange, species="human")
```

Get phenotype information from the Ensembl REST API that is associated with the genomic range.

**Arguments**:

- `grange`: a GenomicRange object
- `species`: species to search for, default is human

**Returns**:

a dictionary with the phenotype information

<a id="ensembl.Ensembl.sequence"></a>

#### sequence

```python
@api_call
def sequence(id,
             trim_end=None,
             trim_start=None,
             expand_3=None,
             expand_5=None,
             sequence_type="genomic")
```

Get sequence information from the Ensembl REST API for a given Ensembl id

**Arguments**:

- `id`: Ensembl id, because the ids also specify the species you do not need to specify the species
- `trim_end`: trim this many nucleotides from the end
- `trim_start`: trim this many nucleotides from the start
- `expand_3`: expand this many nucleotides from the 3' end not compatible with trim_end
- `expand_5`: expand this many nucleotides from the 5' end not compatible with trim_start
- `sequence_type`: genomics, cds, protein, cdna

**Returns**:

sequence of the thing that is requested, depending on the type this can be genomic sequence, cds sequence, protein sequence or cdna sequence,
multiple sequences are returned as a dataframe

<a id="ensembl.Ensembl.xrefs"></a>

#### xrefs

```python
@api_call
def xrefs(id, species="human", external=False)
```

Get cross references from the Ensembl REST API for a given Ensembl id

**Arguments**:

- `id`: Ensembl id, because the ids also specify the species you do not need to specify the species

**Returns**:

a dict of cross references these can be used to get the ids from other databases from other apis

<a id="ensembl.Ensembl.mapping"></a>

#### mapping

```python
@api_call
def mapping(id, start, end, type="cDNA")
```

Get mapping information from the Ensembl REST API for a given Ensembl id, convert between cDNA, CDS and protein

**Arguments**:

- `id`: Ensembl id, because the ids also specify the species you do not need to specify the species
- `start`: start position of the range
- `end`: end position of the range
- `type`: type of mapping, cDNA, CDS or protein

**Returns**:

dict of mapping information, this not really compatible with genomicranges that's why the inputs are different

<a id="ensembl.Ensembl.overlap"></a>

#### overlap

```python
@api_call
def overlap(grange, features=None, species="human")
```

Get overlap information from the Ensembl REST API for a given genomic range, this can be used to get the features that are

within a region of interest. The features can be specified as a list of strings, if no features are specified all features will be returned.

**Arguments**:

- `grange`: a GenomicRange object
- `features`: features to get, default is None which means all features will be returned
- `species`: species to search for, default is human

**Returns**:

a dict of overlap information, this is a dict of dicts where the keys are the features and the values are the genomic features

<a id="ensembl.Ensembl.homology"></a>

#### homology

```python
@api_call
def homology(id,
             type="orthologues",
             target_species=None,
             source_species="human")
```

Get homology information from the Ensembl REST API for a given ensembl id, this can be used to get orthologues and paralogues

**Arguments**:

- `id`: ensembl id, because the ids also specify the species you do not need to specify the species
- `type`: type of homology, orthologues or paralogues
- `target_species`: target species to get the homology for, if None all species will be returned
- `source_species`: source species to get the homology for, default is human

**Returns**:

a dict of homology information

<a id="ensembl.Ensembl.info"></a>

#### info

```python
def info()
```

Get information from the Ensembl REST API, this returns general information about the api,

used to get an idea of what is available in the api.

**Returns**:

divisions, species and consequences that are available in the api

<a id="utils"></a>

# utils

<a id="utils.api_call"></a>

#### api\_call

```python
def api_call(func)
```

add metadata to an api call and return the apicall dataclass instance instead of just a dict

**Arguments**:

- `func`: function to be decorated

**Returns**:

a wrapper function, this will return an ApiCall instance with all information about the api call

<a id="utils.ApiCall"></a>

## ApiCall Objects

```python
@dataclass
class ApiCall()
```

Stores metadata and results of an API call. This is to make it easier to track api calls for knowledge base construction.

<a id="utils.ApiCall.rerun"></a>

#### rerun

```python
def rerun(access_key=None, email=None)
```

rerun the api call with the same parameters, useful if the api call failed or if you want to update the results

**Arguments**:

- `access_key`: if the api requires an access key like alphagenome or biogrid
- `email`: if the api requires an email like NCBI

**Returns**:

an updated ApiCall instance

<a id="utils.ApiCall.chunks"></a>

#### chunks

```python
@cached_property
def chunks(path="root", max_chunk_chars: int = 1000)
```

chunks an api response, this will be used for semantic searching the chunks

**Arguments**:

- `max_chunk_chars`: for larger ones with text

**Returns**:

list of chunks with path of the dict starting with root

<a id="utils.ApiCall.flat"></a>

#### flat

```python
@cached_property
def flat()
```

Flatten JSON response into a single summary string. This will be used for tsvector in full text search

