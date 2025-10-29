---
layout: default
title: Literature module reference
parent: API Reference
nav_order: 2
---


<a id="literature"></a>

# literature

<a id="literature.paper_from_response"></a>

#### paper\_from\_response

```python
def paper_from_response(openalex_response)
```

generate a paper object from an openalex response

**Arguments**:

- `openalex_response`: openalex response json

**Returns**:

a paper object

<a id="literature.paper_from_link"></a>

#### paper\_from\_link

```python
def paper_from_link(link)
```

generate a paper object from an openalex link, this is useful for references and related works

**Arguments**:

- `link`: openalex link

**Returns**:

a paper object

<a id="literature.LitSearch"></a>

## LitSearch Objects

```python
class LitSearch()
```

<a id="literature.LitSearch.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pubmed_api_key=None, email=None, sort_by="relevance")
```

create the ncessary framework for searching

**Arguments**:

- `email`: email to use for pubmed api
- `sort_by`: relevance or pub+date
- `pubmed_api_key`: 

<a id="literature.LitSearch.search"></a>

#### search

```python
def search(query, database="pubmed", results="id", max_results=1000)
```

search pubmed and arxiv for a query, this is just keyword search no other params are implemented at the moment

**Arguments**:

- `query`: this is a string that is passed to the search, as long as it is a valid query it will work and other fields can be specified
- `database`: pubmed or arxiv
- `results`: what to return, default is paper id PMID and arxiv id
- `max_results`: max number of results to return default 1000

**Returns**:

paper ids specific to the database

<a id="literature.PaperInfo"></a>

## PaperInfo Objects

```python
@dataclass
class PaperInfo()
```

Dataclass to hold information about a paper, this is constructed inside the Paper class and desined to be compatible with
semantic search and embedding distance searches

<a id="literature.Paper"></a>

## Paper Objects

```python
class Paper()
```

<a id="literature.Paper.__init__"></a>

#### \_\_init\_\_

```python
def __init__(paper_id, id_type="pubmed", get_abstract=True)
```

This class is used to download and process a paper from a given id, it can also be used to process a paper from a file

**Arguments**:

- `paper_id`: 
- `id_type`: pubmed or arxiv
- `filepath`: if you already have the pdf file you can pass it here, mutually exclusive with paper_id
- `citations`: if you want to get the citations for the paper, need paper id, cannot do it with pdf
- `references`: if you want to get the references for the paper, need paper id, cannot do it with pdf
- `related_works`: if you want to get the related works for the paper, need paper id, cannot do it with pdf

<a id="literature.Paper.get_abstract"></a>

#### get\_abstract

```python
def get_abstract()
```

get the abstract of the paper from pubmed or arxiv

**Returns**:

fill in the paper info abstract, title, authors

<a id="literature.Paper.search_info"></a>

#### search\_info

```python
def search_info()
```

search openalex for the paper info and download link

**Returns**:

fill in the paper info openalex_info and download_link

<a id="literature.Paper.download"></a>

#### download

```python
def download(destination)
```

download the paper pdf to the destination folder

**Arguments**:

- `destination`: where to download the paper, it must exist, the folder will not be created or checked for existence

**Returns**:

download the paper pdf to the destination folder

<a id="literature.Paper.get_references"></a>

#### get\_references

```python
def get_references()
```

get the references of the paper from openalex

**Returns**:

fill in the paper info references

<a id="literature.Paper.get_related_works"></a>

#### get\_related\_works

```python
def get_related_works()
```

get the related works of the paper from openalex

**Returns**:

fill in the paper info related_works

<a id="literature.Paper.get_cited_by"></a>

#### get\_cited\_by

```python
def get_cited_by(cursor="*")
```

get the papers that cite this paper from openalex

**Arguments**:

- `cursor`: the used does not need to worry about this, it is used for pagination and recursive calls

**Returns**:

fill in the paper info cited_by

<a id="paper_processor"></a>

# paper\_processor

<a id="paper_processor.PaperProcessor"></a>

## PaperProcessor Objects

```python
class PaperProcessor()
```

paper processor class, this is the main class for extracting text figures and generating embeddings for the papers
the pipeline method is the main caller where you can specify which steps you would like to run
all the necessary parameters are passed in a config dict so there are no hard coded values and no values to fill

<a id="paper_processor.PaperProcessor.extract"></a>

#### extract

```python
def extract(model, file_path, zoom=2)
```

extract text and images from a pdf, this model gets all the figures and tables from the pdf and returns them as images

as well as extracting the pdf text using tesseract.

**Arguments**:

- `file_path`: pdf file path

**Returns**:

text, figures and tables as pillow images

<a id="paper_processor.PaperProcessor.text_embeddings"></a>

#### text\_embeddings

```python
def text_embeddings(chunker, model, text, splitting_strategy="semantic")
```

genereate text embeddings using a chunking strategy and an embedding model. The model is a huggingface senntence transformer

and the chunker is a chonkie semantic chunker

**Arguments**:

- `text`: text to embed
- `chunker`: chonkie semantic chunker
- `splitting_strategy`: whether to use semantic chunking or not
- `embedding_model`: sentence transformer model

**Returns**:

chunks and embeddings if not chunked then the whole text and its embedding

<a id="paper_processor.PaperProcessor.image_embeddings"></a>

#### image\_embeddings

```python
def image_embeddings(images, processor, model)
```

generate image embeddings using a vision model and its processor

**Arguments**:

- `images`: images, these can be tables or figures
- `processor`: image processor this is a huggingface processor
- `model`: the vl model this is a huggingface model

**Returns**:

return the embeddings as a list. Depending on the kind of model used this can be a 1D or 2D embedding,
the current implementaion of this function does not care but your knowledgebase and the project class will break if the
necessary changes are not made to accomodate the embedding shape

<a id="paper_processor.PaperProcessor.interpret_image"></a>

#### interpret\_image

```python
def interpret_image(image, prompt, model, processor, max_tokens=100)
```

This function takes an image and a prompt, and generates a text description of the image using a vision-language model.

the default model is Qwen2_5_VL.

**Arguments**:

- `image`: PIL image, no need to save to disk
- `prompt`: image prompt, see configs for default
- `processor`: processor class from huggingface
- `model`: model class from huggingface
- `max_tokens`: number of tokens to generate, more tokens = more text but does not mean more information
- `device`: gpu or cpu, if cpu keep it short

**Returns**:

string

<a id="paper_processor.PaperProcessor.pipeline"></a>

#### pipeline

```python
def pipeline(papers,
             extract=True,
             embed_text=True,
             embed_images=True,
             interpret_images=False,
             embed_iterpretations=False)
```

whole paper processing pipeline

**Arguments**:

- `papers`: list of papers see literature.paper for details
- `extract`: extract text, figues and tables (the latter two are images)
- `embed_text`: chunk and embed the pdf text
- `embed_images`: embed images
- `interpret_images`: run a vision language model on the images to generate text
- `embed_iterpretations`: embed the interpretations of the images

**Returns**:

paper class instance with all the attributes filled

<a id="paper_processor.PaperProcessor.text_score"></a>

#### text\_score

```python
def text_score(query, papers)
```

score papers based on text similarity to a query, this is used in the project class to rank papers based on their relevance to a project description

**Arguments**:

- `query`: a description of what you are looking for
- `papers`: a list of paper instances

**Returns**:

a list of scores corresponding to the papers one per paper

<a id="utils"></a>

# utils

<a id="utils.extract_pdfs_from_tar"></a>

#### extract\_pdfs\_from\_tar

```python
def extract_pdfs_from_tar(file, destination)
```

extract all pdf files from a tar.gz file to a destination folder and return the paths to the extracted pdf files

this is there to process pmc tar.gz files

**Arguments**:

- `file`: downloaded tar.gz file
- `destination`: where to extract the pdf files

**Returns**:

a list of paths to the extracted pdf files

<a id="utils.filter_openalex_response"></a>

#### filter\_openalex\_response

```python
def filter_openalex_response(response,
                             fields=[
                                 "id", "ids", "doi", "title", "topics",
                                 "keywords", "concepts", "mesh",
                                 "best_oa_location", "referenced_works",
                                 "related_works", "cited_by_api_url",
                                 "datasets"
                             ])
```

filters the openalex response to only include the specified fields

**Arguments**:

- `response`: openalex response
- `fields`: which fields to include a list of strings

**Returns**:

new response with only the specified fields

<a id="utils.search_openalex"></a>

#### search\_openalex

```python
def search_openalex(id_type, paper_id, fields=None)
```

api call for openalex to retrieve paper information

**Arguments**:

- `id_type`: pubmed or arxiv
- `paper_id`: the id
- `fields`: which field to get, passed to filter_openalex_response

<a id="utils.search_semantic_scholar"></a>

#### search\_semantic\_scholar

```python
def search_semantic_scholar(paper_id, id_type, api_key=None, fields=None)
```

api call for semantic scholar to retrieve paper information, requires an api key

**Arguments**:

- `paper_id`: paper id
- `id_type`: id type, doi, arxiv, mag, pubmed, pmcid, ACL
- `api_key`: api key for semantic scholar
- `fields`: which fields to retrieve, list of strings

**Returns**:

a dict with the paper information, this is currently not used not it is compatible with the paper class or other
supporting functions

