import os

import pandas as pd
from biotite.sequence.io.gff import GFFFile, get_annotation


def parse_gtf(filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(f'File {filename} does not exist'"")
    elif not filename.endswith('.gff') or not filename.endswith('.gff3'):
        raise NotImplementedError(f"File {filename} does not end with .gff only GFF3 files are supported")
    else:
        gff=GFFFile(filename)
        sections={"chrom":[], "gene":[], "transcript":[], "exon":[], "cds":[], "five_prime_utr":[], "three_prime_utr":[],
                  "introns":[]}
        for i in range(len(gff)):
            seqid, source, region_type, start, end, score, strand, phase, attrib = gff[i]
            if source==".":
                continue
            elif region_type=='chromosome':
                chrom=seqid
                start=int(start)
                end=int(end)
                sections['chrom'].append({"id":chrom, "start":start, "end":end})
            elif region_type=='exon':
                exon_name=attrib['exon_id']
                start=int(start)
                end=int(end)
                rank=attrib['rank']
                transcript=attrib['Parent'].replace("transcript:","")
                sections["exon"].append({"id":exon_name, "start":start, "end":end,
                                         "rank":rank, "transcript":transcript})
            elif region_type=='CDS':
                start=int(start)
                end=int(end)
                phase=int(phase)
                if gff[i-1][2]=="exon":
                    exon_name=gff[i-1][8]["exon_id"]
                else:
                    exon_name = gff[i + 1][8]["exon_id"]
                sections["cds"].append({"start":start, "end":end, "phase":phase, "exon":exon_name})
            elif region_type=='five_prime_UTR':
                start=int(start)
                end=int(end)
                if gff[i - 1][2] == "exon":
                    exon_name = gff[i - 1][8]["exon_id"]
                else:
                    exon_name = gff[i + 1][8]["exon_id"]
                sections["five_prime_utr"].append({"exon":exon_name, "start":start, "end":end})
            elif region_type=='three_prime_UTR':
                start = int(start)
                end = int(end)
                if gff[i - 1][2] == "exon":
                    exon_name = gff[i - 1][8]["exon_id"]
                else:
                    exon_name = gff[i + 1][8]["exon_id"]
                sections["three_prime_utr"].append({"exon":exon_name, "start":start, "end":end})
            else: #transcript and gene
                if "transcript" in attrib["ID"]:
                    start=int(start)
                    end=int(end)
                    transcript_name=attrib["ID"].replace("transcript:", "")
                    gene=attrib["Parent"].replace("gene:", "")
                    annot={}
                    for item in attrib.items():
                        if item[0] not in ["Parent", "ID", "transcript_id", "gene_id"]:
                            annot[item[0]] = item[1]
                        else:
                            continue
                    sections["transcript"].append({"transcript":transcript_name, "start":start, "end":end, "gene":gene, "annot":annot})
                elif "gene" in attrib["ID"]:
                    start=int(start)
                    end=int(end)
                    strand=strand
                    chrom=seqid
                    gene_name=attrib["ID"].replace("gene:", "")
                    annot={}
                    for item in attrib.items():
                        if item[0] not in ["Parent", "ID", "transcript_id", "gene_id"]:
                            annot[item[0]] = item[1]
                        else:
                            continue
                    sections["gene"].append({"chrom":chrom, "gene":gene_name, "start":start,
                                             "end":end, "strand":strand, "annot":annot})
    #TODO introns
