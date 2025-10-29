---
layout: default
title: Literature Search
parent: Literature
grand_parent: Modules
nav_order: 1
---



## LitSearch

The `LitSearch` class provides methods to search PubMed and arXiv databases.

### Usage

```python
from benchmate.literature.literature import LitSearch

# Initialize searcher (optional PubMed API key)
searcher = LitSearch(pubmed_api_key="your_api_key")  # API key optional

# Search PubMed
pubmed_ids = searcher.search(
    query="BRCA1 breast cancer",
    database="pubmed",
    results="id",     # Return PMIDs
    max_results=1000  # Max number of results to return
)

# Search with DOIs
dois = searcher.search(
    query="BRCA1 breast cancer", 
    database="pubmed",
    results="doi"     # Return DOIs instead of PMIDs
)

# Search arXiv
arxiv_ids = searcher.search(
    query="machine learning genomics",
    database="arxiv"
)
```

This search only returns the paper ids. You can sort your results by relevance or publication date. For other
more advanced search you can pass them as free text into the query parameter. Anything you can type in the pubmed
search bar you can also use in the query text. These include special characters like `[Author]`. 