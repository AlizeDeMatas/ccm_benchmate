import os
import json

import requests
import pandas as pd

from ccm_demo.protein.utils import *

class UniProt:
    def __init__(self, uniprot_id, search_intact=True, consolidate_refs=True, **kwargs):
        self.description = None
        self.xrefs = None
        self.xref_types = None
        self.variation = None
        self.comment_types = None
        self.gene = None
        self.name = None
        self.alternative_names = None
        self.feature_types = None
        self.sequence = None
        self.organism = None
        self.secondary_accessions = None
        self.id = None
        self.uniprot_id = uniprot_id
        self.json = self.gather()
        self.process_uniprot()
        self.get_description()
        if "citationCrossReferences" in self.json:
            self.references = self.extract_references()
        else:
            self.references = []
        self.get_xrefs()
        self.get_features()
        self.get_comments()
        self.get_variations()
        self.cross_references = self.get_xrefs()
        self.interactions=Interactions(self, search_intact=search_intact, **kwargs)
        self.isoforms=Isoforms(self)
        self.mutagenesis=Mutagenesis(self)
        if consolidate_refs:
            self.consolidate_references()


    def gather(self):
        url = urls["base_response"].format(self.uniprot_id)
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        content = response.content.decode().strip()
        content = json.loads(content)
        if len(content)>1:
            raise ValueError("Your query returned more than one result please check your accession")
        return content[0]

    def process_uniprot(self):

        self.id = self.json["id"]
        self.sequence = self.json["sequence"]["sequence"]
        self.organism = {"name": self.json["organism"]['names'],
                         "taxid": self.json["organism"]["taxonomy"]}
        self.secondary_accessions=[self.json["secondaryAccession"]]
        self.name = self.json["protein"]['recommendedName']["fullName"]['value']
        self.alternative_names=self.json["protein"]['alternativeName']
        self.gene=self.json['gene']
        self.feature_types=[feat['type'] for feat in self.json["features"]]
        self.comment_types=set([feat["type"] for feat in self.json['comments']])


    def get_features(self, feature_types=None):
        if feature_types is not None:
            features = [feat for feat in self.json["features"] if feat["type"] in feature_types]
        else:
            features = [feat for feat in self.json["features"]]

        return features

    def get_comments(self, types=None):
        if types is not None:
            if type(types) == str:
                types = [types]
            comments = [comment for comment in self.json["comments"] if comment["type"] in types]
        else:
            comments = [feat for feat in self.json["comments"]]
        return comments

    def extract_references(self):
        refs = []
        for reference in self.json["references"]:
            for db in reference["dbReferences"]:
                if db["type"] in ["PubMed", "arxiv", "medarxiv", "bioarxiv"]:
                    refs.append(db)
        self.references = refs
        return self

    def get_xrefs(self):
        xrefs = self.json["dbReferences"]
        self.xref_types = list(set([item["type"] for item in xrefs]))
        self.xrefs = xrefs
        return self

    def extract_xrefs(self, types=None):
        if type(types) is str:
            types = [types]
        if type is None:
            return self.xrefs
        else:
            return [item for item in self.xrefs if item["database"] in types]

    def get_description(self):
        desc = []
        for comment in self.json["comments"]:
            if "texts" in comment.keys():
                desc.append("\n".join([item["value"] for item in comment["texts"]]))

        self.description = "\n".join(desc)
        return self

    def get_variations(self):
        variants=requests.get(urls["variation"].format(self.uniprot_id))
        variants.raise_for_status()
        variants=json.loads(variants.content.decode())[0]
        variants=variants["features"]
        variants=pd.DataFrame(variants)
        self.variation=variants
        return self


    def consolidate_references(self):
        if self.isoforms is not None or len(self.isoforms) > 0:
            for isoform in self.isoforms.isoforms:
                for refs in isoform["pubmed_id"]:
                    self.references.append({"type":"Pubmed", "id":isoform["pubmed_id"]})

        if self.mutagenesis is not None or self.mutagenesis.mutations.shape[0] > 0:
            for ref in self.mutagenesis.mutations["pubmed_id"].tolist():
                self.references.extend(ref)

        if self.interactions is not None or self.interactions.shape[0] > 0:
            if self.interactions.intact_results is not None:
                self.references.extend(self.interactions.intact_results["pubmed_id"].tolist())

        if self.variation is not None or self.variation.shape[0] > 0:
            var_refs=self.variation["evidences"].dropna().tolist()
            for ref_list in var_refs:
                for ref in ref_list:
                    if ref["source"]["name"].lower() == "pubmed":
                        self.references.append(ref["source"]["id"])

        self.references=list(set(self.references))
        return self

    def __str__(self):
        return self.description

    def __repr__(self):
        return "Uniprot instance with name {} and {} aa long".format(self.name, len(self.sequence))


class Interactions:
    def __init__(self, uniprot, search_intact=True, **kwargs):
        self.intact_results = None
        self.interactions = None
        self.uniprot_id = uniprot.uniprot_id
        self.gather()
        if search_intact:
            self.intact_results=self.intact_search(**kwargs)

    def gather(self):
        response = requests.get(urls["interactions"].format(self.uniprot_id), headers=headers)
        response.raise_for_status()
        response = json.loads(response.content.decode())
        self.interactions = pd.DataFrame(response[0]["interactions"])
        
    #TODO need to move logic out of there for recursion need a __method__
    def intact_search(self, page=0, page_size=1000):
        ebi_id = self.interactions["interactor1"].tolist()[0]
        interactions, last_page =search_intact(ebi_id, page, page_size)
        while not last_page:
            page=page+1
            next_page_interactions, last_page =search_intact(ebi_id, page=page, page_size=page_size)
            interactions.extend(next_page_interactions)
        interactions=pd.DataFrame(interactions)
        return interactions


class Isoforms:
    def __init__(self, uniprot):
        self.isoforms = None
        self.uniprot_id = uniprot.uniprot_id
        self.gather()

    def gather(self):
        isoforms = []
        isoforms_response = requests.get(urls["isoforms"].format(self.uniprot_id), headers=headers)
        isoforms_response.raise_for_status()
        isoforms_response = json.loads(isoforms_response.content.decode())
        for iso in isoforms_response:
            accession = iso["accession"]
            comments = [comment["type"] for comment in iso["comments"]]
            sequence = iso["sequence"]["sequence"]
            external_references= iso["dbReferences"]
            ref_ids=[]
            references= [ref for ref in iso["references"]]
            for ref in references:
                reftypes=ref["citation"]["dbReferences"]
                for rtype in reftypes:
                    if rtype["type"] == "Pubmed":
                        ref_ids.append(type["id"])
            isoform={"accession":accession,
                     "comments":comments,
                     "sequence":sequence,
                     "pubmed_id":ref_ids,
                     "external_references":external_references,}
            isoforms.append(isoform)
        self.isoforms = isoforms
        return self

class Mutagenesis:
    def __init__(self, uniprot):
        self.uniprot_id = uniprot.uniprot_id
        self.mutations = None
        self.gather()

    def gather(self):
        mutations = []
        mutations_response = requests.get(urls["mutagenesis"].format(self.uniprot_id), headers=headers)
        mutations_response.raise_for_status()
        mutations_response = json.loads(mutations_response.content.decode())[0]["features"]
        for mutation in mutations_response:
            type = mutation["type"]
            alt=mutation["alternativeSequence"]
            start = mutation["begin"]
            end = mutation["end"]
            description = mutation["description"]
            references=[ref["source"]["id"] for ref in mutation["evidences"] if ref["source"]["name"]=="PubMed"]
            mut={"type":type,
                 "description":description,
                 "start":start,
                 "end":end,
                 "alt":alt,
                 "pubmed_id":references,}
            mutations.append(mut)
        self.mutations = pd.DataFrame(mutations)
        return self


