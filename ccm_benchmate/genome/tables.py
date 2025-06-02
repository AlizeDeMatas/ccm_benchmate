
from sqlalchemy import (
    Column, ForeignKey, Integer, String, JSON
)

from ccm_benchmate.knowledge_base.tables import Base


#TODO metadata about the genome like spikeins etc
class Genome(Base):
    __tablename__ = 'genome'
    genome_id = Column(Integer, primary_key=True, autoincrement=True)
    genome_id=Column(String, nullable=True)
    version = Column(String, nullable=True)
    source=Column(String, nullable=True)
    genome_fasta_file = Column(String, nullable=True)
    transcriptome_fasta_file = Column(String, nullable=True)
    proteome_fasta_file = Column(String, nullable=True)

class Chrom(Base):
    __tablename__ = 'chrom'
    chrom_id = Column(Integer, autoincrement=True, primary_key=True)
    chrom=Column(String, nullable=True)
    genome_id=Column(Integer, ForeignKey('genome.genome_id'), nullable=True)

class Gene(Base):
    __tablename__ = 'gene'
    gene_id = Column(Integer, autoincrement=True, primary_key=True)
    gene_name = Column(String, nullable=False)
    chrom=Column(Integer, ForeignKey('chrom.chrom_id'), nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    strand = Column(String, nullable=False)
    annot=Column(JSON)

class Transcript(Base):
    __tablename__ = 'transcript'
    transcript_id = Column(Integer, autoincrement=True, primary_key=True)
    transcript_name = Column(String, nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    gene=Column(Integer, ForeignKey('gene.gene_id'))
    annot=Column(JSON)

class Exon(Base):
    __tablename__ = 'exon'
    exon_id = Column(Integer, autoincrement=True, primary_key=True)
    exon_name = Column(String, nullable=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    exon_rank = Column(Integer, nullable=False)
    transcript=Column(Integer, ForeignKey('transcript.transcript_id', nullable=True))

class ThreeUTR(Base):
    __tablename__ = 'three_utr'
    three_utr_id = Column(Integer, autoincrement=True, primary_key=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    exon_id = Column(Integer, ForeignKey('exon.exon_id'), nullable=True)

class FiveUTR(Base):
    __tablename__ = 'five_utr'
    five_utr_id = Column(Integer, autoincrement=True, primary_key=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    exon_id = Column(Integer, ForeignKey('exon.exon_id'), nullable=True)

class Cds(Base):
    __tablename__ = 'cds'
    cds_id = Column(Integer, autoincrement=True, primary_key=True)
    cds_name = Column(String, nullable=True)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    exon=Column(Integer, ForeignKey('exon.exon_id'), nullable=False)

class Introns(Base):
    __tablename__ = 'introns'
    id = Column(Integer, autoincrement=True, primary_key=True)
    tx_id = Column(Integer, ForeignKey('transcript.transcript_id'), nullable=False)
    intron_rank = Column(Integer, nullable=False)
    start=Column(Integer)
    end=Column(Integer)

