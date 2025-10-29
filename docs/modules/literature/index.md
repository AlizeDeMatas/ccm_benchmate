---
layout: default
title: Literature
parent: Modules
nav_order: 1
---

## Literature module:

This module provides a way to search for scientific literature. It is designed to work with the NCBI PubMed and ARXIV databases.
You can search for articles and using free text queries as well as retriving specific articles by their identifiers. The latter is 
useful for retrieving articles that you already know about or more importantly are mentioned in the data you have retrieved using the 
APIs modules. 

Articles titles and abstracts are returned as from Pubmed and ARXIV searches (Pubmed already archives medarxiv and bioarxiv articles).
Additionally, you can search for open acceess articles using [openalex](openalex.org) and retrieve their full text pdf files for download. 

These downloaded pdf (as well as any other local pdf that you already have) can be processed to extract the text, figures, tables from the 
downloaded documents. Using semantic chunking methods (sepearing the text into sections that convey similar topics) the text can further be
processed. Figures and tables can be automaticall interpreted using a vision language model (default is QWEN-7.5B-VL). These interpretations 
are similarly processed to the full text data. All of this can be permanantly stored in a database for later retrieval and analysis 
(more on that later, see knowledge_base module). 

Depending on your use case you can also use a description of your research interest to filter papers based on their abstracts to save on compute
time and resources. Please see the literature module [documentation](literature.md) for more information and how to use these features. 