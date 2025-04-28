import os

import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Session

from Bio.Seq import Seq
import pysam


#TODO genome class



class Genome:
    def __init__(self, annotation_path, genome_fasta, transcriptome_fasta=None,
                 proteome_fasta=None, db_conn=None, taxon_id=None,):
        self.session = Session(self.db)
        self.metadata = sqlalchemy.MetaData(self.db)
        self.metadata.reflect(bind=self.db)
        pass

    def genes(self):
        pass

    #TODO I want to do this txdb style where a transcript is a list of exons
    def transcripts(self):
        pass

    def exons(self):
        pass

    def coding(self):
        pass

    def introns(self):
        pass



    def __generate_transcriptome(self):
        pass

    def __generate_proteome(self):
        pass

    def __str__(self):
        pass


