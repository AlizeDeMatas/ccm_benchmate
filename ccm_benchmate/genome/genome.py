
import warnings

import sqlalchemy
from sqlalchemy.orm import Session

from Bio import Seq, SeqIO
import pysam

from ccm_benchmate.genome.utils import parse_gtf, insert_genome
from ccm_benchmate.ranges.genomicranges import *


class Genome:
    def __init__(self, genome_fasta, transcriptome_fasta=None,
                 proteome_fasta=None, db_conn=None, taxon_id=None, generate_transcriptome=False,
                 generate_proteome=False):
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
        self.tables = self.metadata.tables
        self.genome_fasta = pysam.FastaFile(genome_fasta)
        if transcriptome_fasta is not None:
            self.transcriptome_fasta=pysam.FastaFile(transcriptome_fasta)
        if proteome_fasta is not None:
            self.proteome_fasta=pysam.FastaFile(proteome_fasta)
        self.taxon_id=taxon_id
        if transcriptome_fasta is None and generate_transcriptome:
            self.transcriptome_fasta=self.__generate_transcriptome()
        if proteome_fasta is None and generate_transcriptome:
            self.proteome_fasta=self.__generate_proteome()


    def genes(self, ids=None, range=None, overlap_type=None):
        """
        Gene id or range if range is provided it will return the genes in that range depending on the overlap type
        :param id: Gene id, that used in the gtf file
        :param range: A GenomicRange object
        :param overlap_type: one of ['any', 'start', 'end', 'within'] see rangaes and genomicranges for more info
        :return: a GenomicRangesDict object with the genes in it
        """
        if range is not None and overlap_type not in ['any', 'start', 'end', 'within']:
            raise ValueError("overlap_type must be one of ['any', 'start', 'end', 'within']")

        genes_table = self.tables['gene']

        if range is not None and ids is not None:
            return ValueError("Cannot provide both range and ids")

        if ids is not None:
            if type(ids) is str:
                ids = [ids]
            query = sqlalchemy.select(genes_table).where(genes_table.c.gene_id.in_(ids))
        elif range is not None:
            query= sqlalchemy.select(genes_table).where(
                genes_table.c.chrom == range.chromosome,
                genes_table.c.start <= range.end,
                genes_table.c.end >= range.start
            )
        else:
            query = sqlalchemy.select(genes_table)

        result = self.session.execute(query).fetchall()
        ranges=[]
        keys=[]
        for item in result:
            gene_id = item[0]
            chrom = item[1]
            start = item[2]
            end = item[3]
            strand = item[4]
            annot = item[5]
            ranges.append(GenomicRange(chrom, start, end, strand, annot))
            keys.append(gene_id)

        gdict=GenomicRangesDict(keys, ranges)
        return gdict

    def transcripts(self, gene_id=None, ids=None, range=None, overlap_type=None):
        """
        same as genes
        :param gene_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        if range is not None and overlap_type not in ['any', 'start', 'end', 'within']:
            raise ValueError("overlap_type must be one of ['any', 'start', 'end', 'within']")

        transcripts_table = self.tables['transcript']

        if range is not None and ids is not None:
            return ValueError("Cannot provide both range and ids")

        if gene_id is not None and ids is None:
            ids=sqlalchemy.select(transcripts_table.c.transcript_id).where(transcripts_table.c.gene_id == gene_id)
            ids=ids.execute().fetchall()
            ids=[i[0] for i in ids]

        if ids is not None:
            if type(ids) is str:
                ids = [ids]
            query = sqlalchemy.select(transcripts_table).where(transcripts_table.c.transcript_id.in_(ids))
        elif range is not None:
            query= sqlalchemy.select(transcripts_table).where(
                transcripts_table.c.chrom == range.chromosome,
                transcripts_table.c.start <= range.end,
                transcripts_table.c.end >= range.start
            )
        else:
            query = sqlalchemy.select(transcripts_table)

        result = self.session.execute(query).fetchall()
        ranges=[]
        keys=[]
        for item in result:
            transcript_id = item[0]
            chrom = item[1]
            start = item[2]
            end = item[3]
            strand = item[4]
            annot = item[5]
            ranges.append(GenomicRange(chrom, start, end, strand, annot))
            keys.append(transcript_id)

        gdict=GenomicRangesDict(keys, ranges)
        return gdict

    def exons(self, transcript_id=None, id=None, range=None, overlap_type=None):
        """
        same as genes but will need to search by transcript not gene, if you do not know the transcript search for it with transcripts first
        :param transcript_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        if range is not None and overlap_type not in ['any', 'start', 'end', 'within']:
            raise ValueError("overlap_type must be one of ['any', 'start', 'end', 'within']")

        exons_table = self.tables['exon']

        if range is not None and id is not None:
            return ValueError("Cannot provide both range and ids")

        if transcript_id is not None and id is None:
            id=sqlalchemy.select(exons_table.c.exon_id).where(exons_table.c.transcript_id == transcript_id)
            id=id.execute().fetchall()
            id=[i[0] for i in id]

        if id is not None:
            if type(id) is str:
                id = [id]
            query = sqlalchemy.select(exons_table).where(exons_table.c.exon_id.in_(id))
        elif range is not None:
            query= sqlalchemy.select(exons_table).where(
                exons_table.c.chrom == range.chromosome,
                exons_table.c.start <= range.end,
                exons_table.c.end >= range.start
            )
        else:
            query = sqlalchemy.select(exons_table)

        result = self.session.execute(query).fetchall()
        ranges=[]
        keys=[]
        for item in result:
            exon_id = item[0]
            chrom = item[1]
            start = item[2]
            end = item[3]
            strand = item[4]
            ranges.append(GenomicRange(chrom, start, end, strand))
            keys.append(exon_id)

        gdict=GenomicRangesDict(keys, ranges)
        return gdict

    def coding(self, transcript_id=None, ids=None, range=None, overlap_type=None):
        """
        same as exons
        :param transcript_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        if range is not None and overlap_type not in ['any', 'start', 'end', 'within']:
            raise ValueError("overlap_type must be one of ['any', 'start', 'end', 'within']")

        cdss_table = self.tables['cds']

        if range is not None and ids is not None:
            return ValueError("Cannot provide both range and ids")

        if transcript_id is not None and ids is None:
            ids=sqlalchemy.select(cdss_table.c.cds_id).where(cdss_table.c.transcript_id == transcript_id)
            ids=id.execute().fetchall()
            ids=[i[0] for i in ids]

        if ids is not None:
            if type(ids) is str:
                ids = [ids]
            query = sqlalchemy.select(cdss_table).where(cdss_table.c.cds_id.in_(ids))
        elif range is not None:
            query= sqlalchemy.select(cdss_table).where(
                cdss_table.c.chrom == range.chromosome,
                cdss_table.c.start <= range.end,
                cdss_table.c.end >= range.start
            )
        else:
            warnings.warn("You are querying the entire cds table this may take a while")
            query = sqlalchemy.select(cdss_table)
        result = self.session.execute(query).fetchall()
        ranges=[]
        keys=[]
        for item in result:
            cds_id = item[0]
            chrom = item[1]
            start = item[2]
            end = item[3]
            strand = item[4]
            ranges.append(GenomicRange(chrom, start, end, strand))
            keys.append(cds_id)

        gdict=GenomicRangesDict(keys, ranges)
        return gdict

    def introns(self, transcript_id=None, ids=None, range=None, overlap_type=None):
        """
        same as exons
        :param transcript_id:
        :param id:
        :param range:
        :param overlap_type:
        :return:
        """
        if range is not None and overlap_type not in ['any', 'start', 'end', 'within']:
            raise ValueError("overlap_type must be one of ['any', 'start', 'end', 'within']")

        introns_table = self.tables['introns']
        if range is not None and ids is not None:
            return ValueError("Cannot provide both range and ids")

        if transcript_id is not None and ids is None:
            ids=sqlalchemy.select(introns_table.c.intron_id).where(introns_table.c.transcript_id == transcript_id)
            ids=ids.execute().fetchall()
            ids=[i[0] for i in ids]

        if ids is not None:
            if type(ids) is str:
                ids = [ids]
            query = sqlalchemy.select(introns_table).where(introns_table.c.intron_id.in_(ids))
        elif range is not None:
            query= sqlalchemy.select(introns_table).where(
                introns_table.c.chrom == range.chromosome,
                introns_table.c.start <= range.end,
                introns_table.c.end >= range.start
            )
        else:
            warnings.warn("You are querying the entire introns table this may take a while")
            query = sqlalchemy.select(introns_table)
        result = self.session.execute(query).fetchall()
        ranges=[]
        keys=[]
        for item in result:
            intron_id = item[0]
            chrom = item[1]
            start = item[2]
            end = item[3]
            strand = item[4]
            ranges.append(GenomicRange(chrom, start, end, strand))
            keys.append(intron_id)

        gdict=GenomicRangesDict(keys, ranges)
        return gdict

    def __generate_transcriptome(self, path):
        """
        This will generate the transcriptome from the database and the fasta file and will save another fasta file to disk as well as the pysam connection
        :return:
        """

        transcripts=self.transcripts()
        sequences=[]
        for transcript in transcripts:
            transcript_id=transcript.id
            transcript_range=transcript.range
            seq=self.get_sequence(transcript_range)
            seq=SeqIO.SeqRecord(Seq.Seq(seq), id=transcript_id, description="")
            sequences.append(seq)
        SeqIO.write(sequences, path, "fasta")
        return path

    def __generate_proteome(self, path):
        """
        same as generate transcriptome but for the proteome it will get translated using standard codon table, no option to
        specify a different codon table at the moment.
        :return:
        """
        transcripts_table = self.tables['transcript']
        cds_table = self.tables['cds']

        query=sqlalchemy.select(transcripts_table.c.transcript_id)
        transcript_ids=self.session.execute(query).fetchall()
        transcript_ids=[i[0] for i in transcript_ids]

        coding_sequences=[]
        for transcript_id in transcript_ids:
            cdss=self.coding(transcript_id=transcript_id)
            if len(cdss) == 0:
                continue
            else:
                sequences=[]
                for cds in cdss:
                    seq=self.get_sequence(cds)
                    sequences.append(seq)
                coding_sequence=str("".join(sequences))
                protein_seq=coding_sequence.translate()
                coding_sequences.append(SeqIO.SeqRecord(Seq.Seq(protein_seq), id=transcript_id, description=""))
        SeqIO.write(coding_sequences, path, "fasta")
        return path

    #TODO need to add genome annotations
    def _upload_genome(self, gtf_path):
        chroms, genes, transcripts, exons, cdss, three_utrs, five_utrs, introns = parse_gtf(gtf_path)
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
            seq = str(Seq.Seq(seq).reverse_complement())
        return seq


    def __str__(self):
        return f"Genome: for : {self.taxon_id}"


