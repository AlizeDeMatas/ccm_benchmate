import warnings

import pandas as pd
import requests
import json

from ccm_demo.variant.variant import Variant
from ccm_demo.utils.genomicranges import GenomicRange

#I'm skipping the genome stuff because we have the genome class that will get the genome build the db etc.
# this is also the whole point of genomic ranges classes, that we can do these calculations locally, I do not think
# user will be using more than a few genomes at any given time so there is no reason for api calls
class Ensembl:
    def __init__(self, dataset="hsapiens_gene_ensembl"):
        self.base_url = "https://rest.ensembl.org"
        self.dataset = "hsapiens_gene_ensembl"
        self.headers={ "Content-Type" : "application/json"}
        self.vep_tools = ['AlphaMissense', 'AncestralAllele', 'Blosum62', 'CADD', 'Conservation', 'DisGeNET',
                          'DosageSensitivity', 'EVE', 'Enformer', 'GO', 'GeneSplicer', 'Geno2MP', 'IntAct', 'LoF',
                          'Mastermind', 'MaveDB', 'MaxEntScan', 'NMD', 'OpenTargets', 'Phenotypes', 'SpliceAI',
                          'UTRAnnotator', 'appris', 'canonical', 'ccds', 'dbNSFP', 'dbscSNV',
                          'distance', 'domains', 'failed', 'flag_pick', 'flag_pick_allele', 'flag_pick_allele_gene',
                          'ga4gh_vrs', 'gencode_basic', 'hgvs', 'mane', 'merged', 'minimal', 'mirna', 'mutfunc',
                          'numbers', 'per_gene', 'pick', 'pick_allele', 'pick_allele_gene', 'protein',
                          'refseq', 'shift_3prime', 'shift_genomic', 'transcript_version',
                          'tsl', 'uniprot', 'variant_class', 'vcf_string', 'xref_refseq']

    def variation(self,  id, method=None, species=None, pubtype=None):
        methods=["translate", "publication"]
        if method not in methods and method is not None:
            raise NotImplementedError("Method {} not implemented".format(method))
        elif method is None:
            ext = f"/variation/{species}/{id}"
        else:
            if method == "translate":
                ext = f"/variant_recorder/{species}/{id}"
            elif method == "recorder":
                if pubtype=="pumbed":
                    ext = f"/variation/human/pmid/{id}?"
                elif pubtype=="pmc":
                    ext = f"/variation/human/pmcid/{id}?"
                else:
                    raise ValueError("pubtype must be one of ['pubmed', 'pmc']")
        response= requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded = json.loads(response.text)
        return decoded


    def vep(self, species, variant, tools):
        ext= f"/vep/{species}/id/{variant.chrom}:{variant.start}-{variant.end}/{variant.alt}"
        if tools is not None:
            for tool in tools:
                if tool in self.vep_tools:
                    warnings.warn(f"Tool {tool} not available in VEP api")
                else:
                    ext = f"{ext};{tool}={1}"
        response = requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded = json.loads(response.text)
        decoded = decoded[0]
        return pd.DataFrame(decoded)

    def phenotype(self, grange, species="human"):
        if not isinstance(grange, GenomicRange):
            raise ValueError("grange must be a GenomicRange object")

        ext= f"/phenotype/region/species/{grange.chrom}/{grange.start}-{grange.end}"
        response = requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded = json.loads(response.text)
        return decoded

    def sequence(self, id, trim_end=None, trim_start=None, expand_3=None, expand_5=None, sequence_type="genomic"):
        types=["genomic", "cds", "protein", "cdna"]
        if trim_end is not None and expand_3 is not None:
            raise ValueError("trim_end and trim_start are mutually exclusive")
        elif trim_start is not None and expand_5 is not None:
            raise ValueError("trim_start and expand_5 are mutually exclusive")
        else:
            ext = f"/sequence/id/{id}"

        if sequence_type not in types:
            raise ValueError("sequence_type must be one of ['genomic', 'cds', 'protein', 'cdna']")

        ext=f"{ext};type={sequence_type};multiple_sequences=1"
        response = requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded = pd.DataFrame(response.json())
        return decoded


    def xrefs(self, id):
        ext = f"/xrefs/id/?{id}"
        response = requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded=pd.DataFrame(response.json())
        return decoded

    def mapping(self, id, start, end, type="cDNA"):
        if type == "cDNA":
            ext = f"/mapping/cdns/{id/start}..{end}"
        elif type == "CDS":
            ext = f"/mapping/cds/{id/start}..{id/end}"
        elif type == "protein":
            ext = f"/mapping/translate/{id/start}..{id/end}"
        else:
            raise ValueError("type must be one of ['cDNA', 'CDS', 'protein']")

        response = requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded = json.loads(response.text)
        return decoded

    def overlap(self, grange, features=None, species="human"):
        available_features= ["band", "gene", "transcript", "cds", "exon", "repeat", "simple", "misc", "variation", "somatic_variation",
                       "structural_variation", "somatic_structural_variation", "constrained", "regulatory", "motif", "mane"]
        if features is None:
            features=available_features
        else:
            for feature in features:
                if feature not in available_features:
                    warnings.warn(f"Feature {feature} not available")
                    continue
                else:
                    features.append(feature)


        if not isinstance(grange, GenomicRange):
            raise ValueError("grange must be a GenomicRange object")

        initial_ext = f"/overlap/region/species/{grange.chrom}/{grange.start}-{grange.end}"
        for feature in features:
            ext = f"{initial_ext};feature={feature}"

        response = requests.get(f"{self.base_url}{ext}", headers=self.headers)
        response.raise_for_status()
        decoded = json.loads(response.text)
        return decoded

    def info(self):
        # this is going to ge, species, consequence types
        divisions = "https://rest.ensembl.org/info/divisions?"
        species = "https://rest.ensembl.org/info/species"
        consequences = "https://rest.ensembl.org/info/variation/consequence_types?"

        divisions=requests.get(divisions, headers=self.headers)
        divisions=json.loads(divisions.text)

        species=requests.get(species, headers=self.headers)
        species=json.loads(species.text)

        consequences=requests.get(consequences, headers=self.headers)
        consequences=json.loads(consequences.text)

        data={"divisions": divisions,
              "species": species,
              "consequences": consequences}
        return data




