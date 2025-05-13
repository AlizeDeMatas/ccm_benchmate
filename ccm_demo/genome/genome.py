import os

import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Session

from Bio.Seq import Seq
import pysam

from ccm_demo.genome.utils import parse_gtf, insert_genome
from ccm_demo.utils.genomicranges import *


class Genome:
    def __init__(self, genome_fasta, transcriptome_fasta=None,
                 proteome_fasta=None, db_conn=None, taxon_id=None,):
        """
        :param gtf_path: Path to the GTF file
        :param genome_fasta: Path to the genome fasta file
        :param transcriptome_fasta:  Path to the transcriptome fasta file
        :param proteome_fasta: Path to the proteome fasta file
        :param db_conn: database connection object this is a sqlalchemy engine
        :param taxon_id: taxon id of the genome
        """
        self.db=db_conn
        self.session = Session(self.db)
        self.metadata = sqlalchemy.MetaData(self.db)
        self.metadata.reflect(bind=self.db)
        self.genome_fasta = pysam.FastaFile(genome_fasta)
        if transcriptome_fasta is not None:
            self.transcriptome_fasta=pysam.FastaFile(transcriptome_fasta)
        if proteome_fasta is not None:
            self.proteome_fasta=pysam.FastaFile(proteome_fasta)
        self.taxon_id=taxon_id

    def genes(self, id=None, range=None, overlap_type=None):
        """
        Gene id or range if range is provided it will return the genes in that range depending on the overlap type
        :param id: Gene id, that used in the gtf file
        :param range: A GenomicRange object
        :param overlap_type: one of ['any', 'start', 'end', 'within']
        :return: a GenomicRangesDict object with the genes in it
        """
        if overlap_type not in ['any', 'start', 'end', 'within']:
            raise ValueError("overlap_type must be one of ['any', 'start', 'end', 'within']")

        pass

    def transcripts(self, gene_id=None, id=None, range=None, overlap_type=None):
        """
        same as genes
        :param gene_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        pass

    def exons(self, transcript_id=None, id=None, range=None, overlap_type=None):
        """
        same as genes but will need to search by transcript not gene, if you do not know the transcript search for it with transcripts first
        :param transcript_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        pass

    def coding(self, transcript_id=None, id=None, range=None, overlap_type=None):
        """
        same as exons
        :param transcript_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        pass

    def introns(self, transcript_id=None, id=None, range=None, overlap_type=None):
        """
        same as exons
        :param transcript_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        pass

    def __generate_transcriptome(self):
        """
        This will generate the transcriptome from the database and the fasta file and will save another fasta file to disk as well as the pysam connection
        :return:
        """
        pass

    def __generate_proteome(self):
        """
        same as generate transcriptome but for the proteome
        :return:
        """
        pass

    def __upload_genome(self):
        chroms, genes, transcripts, exons, cdss, three_utrs, five_utrs, introns = parse_gtf(self.gtf_path)
        insert_genome(chroms, genes, transcripts, exons, cdss, three_utrs, five_utrs, introns, self.db)

    def get_sequence(self, genomic_range):
        """
        Get the sequence of a genomic range. This takes a single genomc range you can iterate over a GenomicRangeList or GenomicRangeDict
        :param genomic_range: GenomicRange object
        :return: sequence as string
        """

        if genomic_range.chromosome not in self.genome_fasta.references:
            raise ValueError(f"Chromosome {genomic_range.chromosome} not found in genome fasta file.")
        start = genomic_range.start
        end = genomic_range.end
        strand = genomic_range.strand
        seq = self.genome_fasta.fetch(genomic_range.chromosome, start, end)
        if strand == '-':
            seq = str(Seq(seq).reverse_complement())
        return seq


    def __str__(self):
        return f"Genome: for : {self.taxon_id}"


