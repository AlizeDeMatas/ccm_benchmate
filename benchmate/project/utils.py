import os
from functools import cached_property, partial

#alignment
from benchmate.alignment.blast import Blast
from benchmate.alignment.mmseqs import MMSeqs
from benchmate.alignment.foldseek import FoldSeek

#APIS
from benchmate.apis.ensembl import Ensembl
from benchmate.apis.uniprot import UniProt
from benchmate.apis.stringdb import StringDb
from benchmate.apis.reactome import Reactome
from benchmate.apis.ebi import EBI
from benchmate.apis.ols import OLS
from benchmate.apis.others import IntAct, BioGrid, AlphaGenome
from benchmate.apis.rnacentral import RnaCentral
from benchmate.apis.ncbi import Ncbi

#Literature
from benchmate.literature.literature import LitSearch, Paper
from benchmate.literature.paper_processor import PaperProcessor

# no need for genome or knowledgebase they will be created by the clases themselves
# sequence, molecule, structure, variant, ranges are created per instance basis, so there needs to be
# some sort of method to add sequence, molecule etc.

class Apis:
    def __init__(self, config):
        self.config=config
        self.ensembl=Ensembl()
        self.uniprot=UniProt()
        self.stringdb=StringDb()
        self.biogrid=BioGrid(access_key=config["biogrid_api_key"])
        self.alphagenome=AlphaGenome(access_key=config["alphagenome_api_key"])
        self.reactome=Reactome()
        self.ebi=EBI(email=config["email"])
        self.ols=OLS()
        self.intact=IntAct()
        self.rnacentral=RnaCentral()
        self.ncbi=Ncbi(email=config["email"])

# the main issue here is now we need to create literture.paper instances not paper
class Literature:
    def __init__(self, config, inference):
        self.config=config
        self.litsearch=LitSearch()
        self.paper=Paper
        self.paper.download=partial(self.paper.download, destination=config["pdf_path"])
        self.processor=PaperProcessor(inference=inference, config=config)


class Alignment:
    def __init__(self, config):
        self.config=config
        self.blast=Blast()
        self.blast.create_db=partial(self.blast.create_db, output_path=self.config["blast_db_path"])
        self.mmseqs=MMSeqs()
        self.mmseqs.create_database=partial(self.mmseqs.create_database, db_path=self.config["mmseqs_db_path"])
        self.mmseqs.download_database=partial(self.mmseqs.download_database, location=self.config["mmseqs_db_path"])
        self.foldseek=FoldSeek()
        self.foldseek.create_database=partial(self.foldseek.create_database, db_path=self.config["foldseek_db_path"])
        self.foldseek.download_database=partial(self.foldseek.download_database, location=self.config["foldseek_db_path"])


