from dataclasses import dataclass
from typing import Optional
import io
import json

import numpy as np
from sqlalchemy import select, insert
from PIL import Image
from sqlalchemy.exc import NoResultFound

from benchmate.utils.general_utils import DataIntegrityError

@dataclass(slots=True)
class PaperInfo:
    """
    Dataclass to hold information about a paper, this is constructed inside the Paper class and desined to be compatible with
    semantic search and embedding distance searches
    """
    # in papers table
    id: str
    external_ids: Optional[dict] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    abstract_embeddings: Optional[np.ndarray] = None
    download_links: Optional[list] = None
    file_paths: Optional[list] = None
    full_json: Optional[dict] = None
    authors: Optional[list] = None
    text: Optional[str] = None

    #body_text_chunk table
    text_chunks: Optional[list] = None
    chunk_embeddings: Optional[np.ndarray] = None

    #in figures table
    figures: Optional[list] = None
    figure_embeddings: Optional[np.ndarray] = None
    figure_interpretation: Optional[list] = None
    figure_interpretation_embeddings: Optional[np.ndarray] = None

    #in tables table
    tables: Optional[list] = None
    table_embeddings: Optional[np.ndarray] = None
    table_interpretation: Optional[list] = None
    table_interpretation_embeddings: Optional[np.ndarray] = None

    #references table
    references: Optional[list] = None

    #related works table
    related_works: Optional[list] = None

    #cited by table
    cited_by: Optional[list] = None

    #TODO fix
    def to_kb(self, project):
        papers_table = project.kb.db_tables["papers"]
        figures_table = project.kb.db_tables["figures"]
        tables_table = project.kb.db_tables["tables"]
        body_text_table = project.kb.db_tables["body_text"]
        chunked_text_table = project.kb.db_tables["body_text_chunked"]
        references_table = project.kb.db_tables["references"]
        related_works_table = project.kb.db_tables["related_works"]
        cited_by_table = project.kb.db_tables["cited_by"]

        #TODO this is the part that needs fixing
        stms = insert(papers_table.c.source_id, papers_table.c.source, papers_table.c.title,
                      papers_table.c.project_id,
                      papers_table.c.abstract, papers_table.c.abstract_embeddings,
                      papers_table.c.pdf_url, papers_table.c.pdf_path,
                      papers_table.c.full_json,
                      papers_table.c.authors).values(self.id, self.external_ids,
                                                         self.title,
                                                         project.project_id,
                                                         self.abstract,
                                                         self.abstract_embeddings,
                                                         self.download_links,
                                                         self.file_path,
                                                         self.full_json,
                                                         self.authors).returning(papers_table.c.paper_id)
        
        paper_id = project.kb.session().execute(stms).scalars().one()

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

    #TODO fix
    @classmethod
    def from_kb(cls, project, id):
        papers_table = project.kb.db_tables["papers"]
        figures_table = project.kb.db_tables["figures"]
        tables_table = project.kb.db_tables["tables"]
        chunked_text_table = project.kb.db_tables["body_text_chunked"]
        references_table = project.kb.db_tables["references"]
        related_works_table = project.kb.db_tables["related_works"]
        cited_by_table = project.kb.db_tables["cited_by"]

        #this is the part that needs fixing
        selection = select(
            papers_table.c.source_id,
            papers_table.c.source,
            papers_table.c.title,
            papers_table.c.abstract,
            papers_table.c.abstract_embeddings,
            papers_table.c.text,
            papers_table.c.pdf_url,
            papers_table.c.pdf_path,
            papers_table.c.full_json,
            papers_table.c.authors,
        ).where(papers_table.c.paper_id == id)
        paper_info = project.kb.session().execute(selection).fetchall()

        if len(paper_info) > 1:
            raise DataIntegrityError("There are multiple papers with the id {}".format(id))
        elif len(paper_info) == 0:
            raise NoResultFound("Could not find a paper with id:{}".format(id))
        else:
            paper = cls(paper_id=paper_info[0][0], id_type=paper_info[0][1], get_abstract=False)
            paper.title = paper_info[0][2]
            paper.abstract = paper_info[0][3]
            paper.abstract_embeddings = paper_info[0][4]
            paper.text = paper_info[0][5]
            paper.download_link = paper_info[0][6]
            paper.file_path = paper_info[0][7]
            if paper.file_path is not None:
                paper.downloaded = True
            else:
                paper.downloaded = False
            paper.full_json = paper_info[0][8]
            paper.authors = paper_info[0][9]

        figures = select(figures_table.c.image_blob,
                         figures_table.c.figure_embeddings,
                         figures_table.c.ai_caption,
                         figures_table.c.figure_interpretation_embeddings).where(figures_table.c.paper_id == id)
        figures = project.kb.session().execute(figures).fetchall()
        if len(figures) == 0:
            paper.figures = None
        else:
            paper.figures = [Image.open(io.BytesIO(figure[0])) for figure in figures]
            paper.figure_embeddings = [figure[1] for figure in figures]
            paper.figure_interpretation = [figure[2] for figure in figures]
            paper.figure_interpretation_embeddings = [figure[3] for figure in figures]

        tables = select(tables_table.c.image_blob,
                        tables_table.c.table_embeddings,
                        tables_table.c.ai_caption,
                        tables_table.c.table_interpretation_embeddings).where(tables_table.c.paper_id == id)
        tables = project.kb.session().execute(tables).fetchall()
        if len(tables) == 0:
            paper.tables = None
        else:
            paper.tables = [Image.open(io.BytesIO(table[0])) for table in tables]
            paper.table_embeddings = [table[1] for table in tables]
            paper.table_interpretation = [table[2] for table in tables]
            paper.table_interpretation_embeddings = [table[3] for table in tables]

        chunks = select(chunked_text_table.c.chunk,
                        chunked_text_table.c.chunk_embeddings).where(chunked_text_table.c.paper_id == id)
        chunks = project.kb.session().execute(chunks).fetchall()
        if len(chunks) == 0:
            paper.text_chunks = None
        else:
            paper.text_chunks = [chunk[0] for chunk in chunks]
            paper.chunk_embeddings = [chunk[1] for chunk in chunks]

        references = select(references_table.c.target_id).where(references_table.c.paper_id == id)
        references = project.kb.session().execute(references).fetchall()
        if len(references) == 0:
            paper.references = None
        else:
            refs = []
            for ref in references:
                ref_paper = cls.from_kb(project, ref[1])
                refs.append(ref_paper)
            paper.references = refs

        cited_by = select(cited_by_table.c.target_id).where(cited_by_table.c.paper_id == id)
        cited_by = project.kb.session().execute(cited_by).fetchall()
        if len(cited_by) == 0:
            paper.cited_by = None
        else:
            refs = []
            for ref in cited_by:
                ref_paper = cls.from_kb(project, ref[1])
                refs.append(ref_paper)
            paper.cited_by = refs

        related_works = select(related_works_table.c.target_id).where(related_works_table.c.paper_id == id)
        related_works = project.kb.session().execute(related_works).fetchall()
        if len(related_works) == 0:
            paper.related_works = None
        else:
            refs = []
            for ref in related_works:
                ref_paper = cls.from_kb(project, ref[1])
                refs.append(ref_paper)
            paper.related_works = refs

        return paper
