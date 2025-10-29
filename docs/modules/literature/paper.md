---
layout: default
title: Paper
parent: Literature
grand_parent: Modules
nav_order: 2
---

## Paper

The `Paper` class handles downloading and processing individual papers. All the paper information is stored in a 
python `dataclass` under the paper.info attribute.

### Usage

```python
from benchmate.literature.literature import Paper

# Initialize from PubMed ID
paper = Paper(
    paper_id="12345678",
    id_type="pubmed",
    citations=True,      # Get citation data
    references=True,     # Get reference data
    related_works=True   # Get related papers
)

# Initialize from arXiv ID 
paper = Paper(
    paper_id="2101.12345",
    id_type="arxiv"
)

# Initialize from local PDF file
paper = Paper(
    paper_id=None,
    filepath="/path/to/paper.pdf"
)

# If you use an arxiv or pubmed id the abstract and the paper title will be automatically extracted
print(paper.info.title)
print(paper.info.abstract)

# you can additional information about the paper via openalex

paper.search_info()
paper.get_references()
paper.get_cited_by()
paper.get_related_works()
```

These methods will modify the paper class in place. The `paper_info` dataclass stores all the relevant information about the paper.
about the paper. Openalex provides a lot of information, including whether a paper is available via open access. If this is the
case there will be a link to the PDF that is stored in the `paper.info.pdf_link` attribute.

To download the PDF to a location of your choice, you can use the `download_pdf` method.

```python
paper.download(destination="/path/to/destination")
```

There are a few limitations to downloading papers. Due to NCBI api key restrictions (that is I don't have one). I cannot 
write an additional method to download papers using pubmed. Therefore I have not written the code for that. And since I do not
have a pubmed API key, I am limited to open access papers, that are indexed by openalex. Even among these there are restrictions for
making simple get requests that sometimes (or all the times) the publishers may refuse to return data for such requests. There is 
nothing I can do about this as I do not control what different publishers do with their servers. That said if you have a list of 
id=pdf key value store you can fill in the paper.info.download_link attribute manually and continue with paper processing discussed 
under [paper processor module](./paper_processor.md)

## PaperInfo Dataclass

We created the `PaperInfo` dataclass to store all the information that is associated with that paper. This includes all the
information that is generated after processing. The dataclass looks like this: 

```python
@dataclass
class PaperInfo:
    """
    Dataclass to hold information about a paper, this is constructed inside the Paper class and desined to be compatible with
    semantic search and embedding distance searches
    """
    id: str
    id_type: str
    title: Optional[str] = None
    authors: Optional[list] = None
    abstract: Optional[str] = None
    abstract_embeddings: Optional[np.ndarray]  = None
    text: Optional[str] = None
    text_chunks: Optional[list] = None
    chunk_embeddings: Optional[np.ndarray] = None
    figures: Optional[list] = None
    figure_embeddings: Optional[np.ndarray] = None
    tables: Optional[list] = None
    table_embeddings: Optional[np.ndarray] = None
    figure_interpretation: Optional[str] = None
    table_interpretation: Optional[str] = None
    download_link: str = None
    downloaded: bool = False
    file_path: str = None
    openalex_info: Optional[dict] = None
    references: Optional[list] = None
    related_works: Optional[list] = None
    cited_by: Optional[list] = None
```

Most of these are populated by the `PaperProcessor`