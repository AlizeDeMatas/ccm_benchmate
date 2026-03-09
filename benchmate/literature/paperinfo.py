from dataclasses import dataclass
from typing import Optional
import io
import json

import numpy as np
from sqlalchemy import select, insert
from PIL import Image
from sqlalchemy.exc import NoResultFound

from benchmate.project.utils import DataIntegrityError
from benchmate.literature.literature import Paper

#TODO this is probably broken, there are too many things to consider here. One of the main issues is the authors, I will not solve that problem
# probably ever.

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
    abstract_embeddings: Optional[np.ndarray] = None
    text: Optional[str] = None
    text_chunks: Optional[list] = None
    chunk_embeddings: Optional[np.ndarray] = None
    figures: Optional[list] = None
    figure_embeddings: Optional[np.ndarray] = None
    tables: Optional[list] = None
    table_embeddings: Optional[np.ndarray] = None
    figure_interpretation: Optional[list] = None
    figure_interpretation_embeddings: Optional[np.ndarray] = None
    table_interpretation: Optional[list] = None
    table_interpretation_embeddings: Optional[np.ndarray] = None
    download_link: str = None
    downloaded: bool = False
    file_path: str = None
    openalex_info: Optional[dict] = None
    references: Optional[list] = None
    related_works: Optional[list] = None
    cited_by: Optional[list] = None
    pmc_id: Optional[str] = None

    def to_kb(self, project):
        papers_table = project.kb.db_tables["papers"]
        authors_table = project.kb.db_tables["authors"]
        figures_table = project.kb.db_tables["figures"]
        tables_table = project.kb.db_tables["tables"]
        body_text_table = project.kb.db_tables["body_text"]
        chunked_text_table = project.kb.db_tables["body_text_chunked"]
        references_table = project.kb.db_tables["references"]
        related_works_table = project.kb.db_tables["related_works"]
        cited_by_table = project.kb.db_tables["cited_by"]

        stms = insert(papers_table.c.source_id, papers_table.c.source, papers_table.c.title,
                      papers_table.c.project_id,
                      papers_table.c.abstract, papers_table.c.abstract_embeddings,
                      papers_table.c.pdf_url, papers_table.c.pdf_path,
                      papers_table.c.openalex_response).values(self.id, self.id_type,
                                                         self.title,
                                                         project.project_id,
                                                         self.abstract,
                                                         self.abstract_embeddings,
                                                         self.download_link,
                                                         self.file_path,
                                                         self.openalex_info).returning(papers_table.c.paper_id)
        
        paper_id = project.kb.session().execute(stms).scalars().one()

        # TODO need to check if already in db, this is wrong because I need to get the author, id, I might give up on this
        # altogether because there are so many things that can go wrong with this.
        for author in self.authors:
            author_stms = insert(authors_table.c.paper_id,
                                 authors_table.c.name,
                                 authors_table.c.affiliation).values(paper_id,
                                                              author["name"],
                                                              author["affiliation"])
            project.kb.session().execute(author_stms)

        if self.figures is not None:
            for i in range(len(self.figures)):
                img = Image.open(self.figures[i])
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="JPEG")
                img_bytes = img_byte_arr.getvalue()
                figure_stms = insert(figures_table.c.paper_id, figures_table.c.image_blob,
                                     figures_table.c.ai_caption,
                                     figures_table.c.figure_embeddings,
                                     figures_table.c.figure_interpretation_embeddings).values(paper_id,
                                                                                              img_bytes,
                                                                                              self.figure_interpretation[
                                                                                                  i],
                                                                                              json.dumps(
                                                                                                  self.figure_embeddings[
                                                                                                      i].tolist()),
                                                                                              self.figure_interpretation_embeddings[
                                                                                                  i]
                                                                                              )
                project.kb.session().execute(figure_stms)

        if self.tables is not None:
            for i in range(len(self.tables)):
                img = Image.open(self.tables[i])
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="JPEG")
                img_bytes = img_byte_arr.getvalue()
                table_smts = insert(tables_table.c.paper_id, tables_table.c.image_blob,
                                    tables_table.c.ai_caption,
                                    tables_table.c.table_embeddings,
                                    tables_table.c.table_interpretation_embeddings).values(paper_id,
                                                                                           img_bytes,
                                                                                           self.table_interpretation[
                                                                                               i],
                                                                                           json.dumps(
                                                                                               self.table_embeddings[
                                                                                                   i].tolist()),
                                                                                           self.table_interpretation_embeddings[
                                                                                               i]
                                                                                           )
                project.kb.session().execute(table_smts)

        if self.text is not None:
            text_stms = insert(body_text_table.c.paper_id, body_text_table.c.text, ).values(paper_id, self.text)
            project.kb.session().execute(text_stms)

        if self.text_chunks is not None:
            for i in range(len(self.text_chunks)):
                chunk_stms = insert(chunked_text_table.c.paper_id, chunked_text_table.c.chunk,
                                    chunked_text_table.c.chunk_embeddings).values(paper_id,
                                                                                  self.text_chunks[i],
                                                                                  self.chunk_embeddings[i].tolist())
                project.kb.session().execute(chunk_stms)

        if self.references is not None:
            for paper in self.references:
                existing = select(papers_table.c.paper_id).where(papers_table.c.source_id == paper.id,
                                                                 papers_table.c.id_type == paper.id_type)
                ref_id = project.kb.session().execute(existing).scalar()
                if ref_id is None:
                    ref_id = project.add_papers(paper)
                stms = insert(references_table.c.paper_id, references_table.c.id, ).values(paper_id, ref_id)
                project.kb.session().execute(stms)

        if self.related_works is not None:
            for paper in self.related_works:  #
                existing = select(papers_table.c.paper_id).where(papers_table.c.source_id == paper.id,
                                                                 papers_table.c.id_type == paper.id_type)
                related_id = project.kb.session().execute(existing).scalar()
                if related_id is None:
                    related_id = project.add_papers(paper)
                stms = insert(related_works_table.c.paper_id, related_works_table.c.id, ).values(paper_id, related_id)
                project.kb.session().execute(stms)

        if self.cited_by is not None:
            for paper in self.cited_by:
                existing = select(papers_table.c.paper_id).where(papers_table.c.source_id == paper.id,
                                                                 papers_table.c.id_type == paper.id_type)
                cited_id = project.kb.session().execute(existing).scalar()
                if cited_id is None:
                    cited_id = project.add_papers(paper)
                stms = insert(cited_by_table.c.paper_id, cited_by_table.c.id, ).values(paper_id, cited_id)
                project.kb.session().execute(stms)

        project.kb.session().commit()
        return paper_id


    @classmethod
    def from_kb(cls, project, id):
        papers_table = project.kb.db_tables["papers"]
        authors_table = project.kb.db_tables["authors"]
        figures_table = project.kb.db_tables["figures"]
        tables_table = project.kb.db_tables["tables"]
        chunked_text_table = project.kb.db_tables["body_text_chunked"]
        references_table = project.kb.db_tables["references"]
        related_works_table = project.kb.db_tables["related_works"]
        cited_by_table = project.kb.db_tables["cited_by"]

        selection = select(
            papers_table.c.source_id,
            papers_table.c.source,
            papers_table.c.title,
            papers_table.c.abstract,
            papers_table.c.abstract_embeddings,
            papers_table.c.text,
            papers_table.c.pdf_url,
            papers_table.c.pdf_path,
            papers_table.c.openalex_response,
        ).where(papers_table.c.paper_id == id)
        paper_info = project.kb.session().execute(selection).fetchall()

        if len(paper_info) > 1:
            raise DataIntegrityError("There are multiple papers with the id {}".format(id))
        elif len(paper_info) == 0:
            raise NoResultFound("Could not find a paper with id:{}".format(id))
        else:
            paper = Paper(paper_id=paper_info[0][0], id_type=paper_info[0][1], get_abstract=False)
            paper.info.title = paper_info[0][2]
            paper.info.abstract = paper_info[0][3]
            paper.info.abstract_embeddings = paper_info[0][4]
            paper.info.text = paper_info[0][5]
            paper.info.download_link = paper_info[0][6]
            paper.info.file_path = paper_info[0][7]
            if paper.info.file_path is not None:
                paper.info.downloaded = True
            else:
                paper.info.downloaded = False
            paper.info.openalex_response = paper_info[0][8]

        authors = select(authors_table.c.name, authors_table.c.affiliation).where(authors_table.c.paper_id == id)
        authors = project.kb.session().execute(authors).fetchall()
        paper.info.authors = []
        for author in authors:
            auth = {}
            auth["name"] = author[0]
            auth["affiliation"] = author[1]
            paper.info.authors.append(auth)

        figures = select(figures_table.c.image_blob,
                         figures_table.c.figure_embeddings,
                         figures_table.c.ai_caption,
                         figures_table.c.figure_interpretation_embeddings).where(figures_table.c.paper_id == id)
        figures = project.kb.session().execute(figures).fetchall()
        if len(figures) == 0:
            paper.info.figures = None
        else:
            paper.info.figures = [Image.open(io.BytesIO(figure[0])) for figure in figures]
            paper.info.figure_embeddings = [figure[1] for figure in figures]
            paper.info.figure_interpretation = [figure[2] for figure in figures]
            paper.info.figure_interpretation_embeddings = [figure[3] for figure in figures]

        tables = select(tables_table.c.image_blob,
                        tables_table.c.table_embeddings,
                        tables_table.c.ai_caption,
                        tables_table.c.table_interpretation_embeddings).where(tables_table.c.paper_id == id)
        tables = project.kb.session().execute(tables).fetchall()
        if len(tables) == 0:
            paper.info.tables = None
        else:
            paper.info.tables = [Image.open(io.BytesIO(table[0])) for table in tables]
            paper.info.table_embeddings = [table[1] for table in tables]
            paper.info.table_interpretation = [table[2] for table in tables]
            paper.info.table_interpretation_embeddings = [table[3] for table in tables]

        chunks = select(chunked_text_table.c.chunk,
                        chunked_text_table.c.chunk_embeddings).where(chunked_text_table.c.paper_id == id)
        chunks = project.kb.session().execute(chunks).fetchall()
        if len(chunks) == 0:
            paper.info.text_chunks = None
        else:
            paper.info.text_chunks = [chunk[0] for chunk in chunks]
            paper.info.chunk_embeddings = [chunk[1] for chunk in chunks]

        references = select(references_table.c.target_id).where(references_table.c.paper_id == id)
        references = project.kb.session().execute(references).fetchall()
        if len(references) == 0:
            paper.info.references = None
        else:
            refs = []
            for ref in references:
                ref_paper = cls.from_kb(project, ref[1])
                refs.append(ref_paper)
            paper.info.references = refs

        cited_by = select(cited_by_table.c.target_id).where(cited_by_table.c.paper_id == id)
        cited_by = project.kb.session().execute(cited_by).fetchall()
        if len(cited_by) == 0:
            paper.info.cited_by = None
        else:
            refs = []
            for ref in cited_by:
                ref_paper = cls.from_kb(project, ref[1])
                refs.append(ref_paper)
            paper.info.cited_by = refs

        related_works = select(related_works_table.c.target_id).where(related_works_table.c.paper_id == id)
        related_works = project.kb.session().execute(related_works).fetchall()
        if len(related_works) == 0:
            paper.info.related_works = None
        else:
            refs = []
            for ref in related_works:
                ref_paper = cls.from_kb(project, ref[1])
                refs.append(ref_paper)
            paper.info.related_works = refs

        return paper
