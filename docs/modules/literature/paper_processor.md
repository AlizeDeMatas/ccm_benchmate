---
layout: default
title: Paper Processor
parent: Literature
grand_parent: Modules
nav_order: 3
---

# Paper Processor

This class is main workhorse of the literature module, it is responsible for the followin

+ Extracting text, figures and tables from a pdb
+ Semantically chunking the text
+ Generating embeddings for these chunks
+ Generating embeddings for the figures and tables (they are stored as images)
+ Generating interpretaions for figures and tables

The main reason for the last item is, because figure and table captions in papers come in many shapes and sizes. Sometimes
they are not even in the same page. The preparation of the pages also depends heavily from publisher to publisher and being
extremely flexible pdf files can contain all sorts of information about the content or none at all. Therefore it is more reliable
to create captions then to actually find them in the pdf. That said the text extraction method can and does capture all the text
this includes the figure and table captions. 

To start the processor class instance all you need is the config. 

```python
from benchmate.config import literature
from benchmate.literature.paper_processor import PaperProcessor

processor=PaperProcessor(literature)
```

There are many methods that you can use in the class but there are 2 that can capture all the functionality. 

```python
papers=["A list of paper class instances"]

papers=processor.pipeline(papers, extract=True, embed_text=True, embed_images=True,
                            interpret_images=True)

```

As the names suggest, the class goes through every paper in the list one by one and applies each function
one by one in the order above. Each method is performed for each paper before moving on to the next. This way 
we minimize the amount of VRAM used. 

The other method interest is the text score, this measures the relevancy of a papers' abstract to a piece of text, this is
extremely useful if you are trying to figure out which papers to actually spend the compute power to process. 

```python
query="some paragraph"

scores=processor.text_score(query, papers)
```

This will return a score for each paper between 0 and 1. 1 being indentical. A score > 0.55 is a pretty safe bet that the paper
is relevant (it might not be exactly what you are looking for but it will be relevant). 

