import pandas as pd

from ccm_benchmate.utils.general_utils import *


class UniProt:
    def __init__(self):
        """
        constructor for the UniProt class, which is used to gather data from the UniProt API. and process it in a readable format.
        :param uniprot_id:
        :param search_intact:
        :param consolidate_refs:
        :param kwargs:
        """
        self.url = "https://www.ebi.ac.uk/proteins/api/proteins?accession={}"
        self.headers = {'Accept': 'application/json'}
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
        self.json = None

    def _gather(self, uniprot_id):
        """
        This function gathers data from the UniProt API using the provided uniprot_id.
        :return: whole json response from the API
        """
        url = self.urls["base_response"].format(uniprot_id)
        response = requests.get(url, headers=self.headers)
        content = warn_for_status(response, "issues with gathering data")
        if content is not None:
            content = json.loads(content)
            if len(content) > 1:
                raise ValueError("Your query returned more than one result please check your accession")
            else:
                content = content[0]

        self.json = content
        return self

    def search_uniprot(self, uniprot_id, consolidate_refs=True, get_variations=True,
                       get_interactions=True, get_mutagenesis=True, get_isoforms=True):
        """
        process the json response from the UniProt API and extract relevant information.
        :return: returns self because it modfies the class instance
        """
        self._gather(uniprot_id)
        self.id = self.json["id"]
        self.sequence = self.json["sequence"]["sequence"]
        self.organism = {"name": self.json["organism"]['names'], "taxid": self.json["organism"]["taxonomy"]}
        if "secondaryAccession" in self.json["apis"].keys():
            self.secondary_accessions = [self.json["secondaryAccession"]]
        self.name = self.json["apis"]['recommendedName']["fullName"]['value']
        if "alternativeNames" in self.json["apis"].keys():
            self.alternative_names = self.json["apis"]['alternativeName']
        self.gene = self.json['gene']
        self.feature_types = set([feat['type'] for feat in self.json["features"]])
        self.comment_types = set([feat["type"] for feat in self.json['comments']])
        self.references = self._extract_references()
        self.xref_types, self.xrefs = self._extract_xrefs()
        self.description = self._extract_description()
        if get_variations:
            self.variation = self._get_variations()

        if get_interactions:
            self.interactions = Interactions(self.id)

        if get_mutagenesis:
            self.mutagenesis = Mutagenesis(self.id)

        if get_isoforms:
            self.isoforms = Isoforms(self.id)

        if consolidate_refs:
            self.references = self.consolidate_references()
        return self

    def _extract_description(self):
        """
        concanate the comments from the json response into a single string this can be used in nlp tasks or comparing
        uniprot instances
        :return:
        """
        desc = []
        for comment in self.json["comments"]:
            if "texts" in comment.keys():
                desc.append("\n".join([item["value"] for item in comment["texts"]]))

        description = "\n".join(desc)
        return description

    def _extract_references(self):
        """
        internal function to extract references from the json response
        :return: references
        """
        refs = []
        for reference in self.json["references"]:
            for db in reference["dbReferences"]:
                if db["type"] in ["PubMed", "arxiv", "medarxiv", "bioarxiv"]:
                    refs.append(db)

        return references

    def _extract_xrefs(self):
        """
        internal function to extract xrefs from the json response
        :return: xref types and xrefs
        """
        xrefs = self.json["dbReferences"]
        xref_types = list(set([item["type"] for item in xrefs]))
        xrefs = pd.DataFrame(xrefs)
        return xref_types, xrefs

    def get_features(self, feature_types=None):
        """
        filter already extracted features by type
        :param feature_types: type of the feature to filter by
        :return: the features
        """
        if feature_types is not None:
            features = [feat for feat in self.json["features"] if feat["type"] in feature_types]
        else:
            features = [feat for feat in self.json["features"]]
        return features

    def get_comments(self, types=None):
        """
        get already extracted comments from the json response
        :param types: comment types to filter by
        :return: comments
        """
        if types is not None:
            if type(types) == str:
                types = [types]
            comments = [comment for comment in self.json["comments"] if comment["type"] in types]
        else:
            comments = [feat for feat in self.json["comments"]]
        return comments

    def get_variations(self):
        """
        query the uniprot API for variations
        :return: pandas DataFrame with the variations
        """
        url = 'https://www.ebi.ac.uk/proteins/api/variation?offset=0&size=-1&accession={}',
        variants = requests.get(url.format(self.uniprot_id))
        warn_for_status(variants, "issues with getting variation")
        variants = json.loads(variants.content.decode())[0]
        variants = variants["features"]
        variants = pd.DataFrame(variants)
        variation = variants
        return variation

    def consolidate_references(self):
        """
        pul all references from the isoforms, mutagenesis, interactions and variations into a single list this is useful
        for literature mining and other tasks
        :return: references
        """
        if self.isoforms.isoforms is not None:
            for isoform in self.isoforms.isoforms:
                for refs in isoform["pubmed_id"]:
                    self.references.append({"type": "Pubmed", "id": refs["pubmed_id"]})

        if self.mutagenesis.mutations is not None:
            for ref in self.mutagenesis.mutations["pubmed_id"].tolist():
                self.references.extend(ref)

        if self.interactions.interactions is not None:
            if self.interactions.intact_results is not None:
                self.references.extend(self.interactions.intact_results["pubmed_id"].tolist())

        if self.variation is not None and "evidences" in self.variation.columns:
            var_refs = self.variation["evidences"].dropna().tolist()
            for ref_list in var_refs:
                for ref in ref_list:
                    if ref["source"]["name"].lower() == "pubmed":
                        self.references.append(ref["source"]["id"])

        references = list(set(self.references))
        return references

    def __str__(self):
        return self.description

    def __repr__(self):
        return "Uniprot instance with name {} and {} aa long".format(self.name, len(self.sequence))


# TODO refactor to seprate intact
class Interactions:
    def __init__(self, uniprot):
        """
        constructor for the Interactions class, which is used to gather interaction data from the UniProt API as well as Intact database.
        :param uniprot:
        :param search_intact:
        :param kwargs:
        """
        self.intact_results = None
        self.interactions = None
        self.uniprot_id = uniprot.uniprot_id
        self.url = 'https://www.ebi.ac.uk/proteins/api/proteins/interaction/{}'
        self.headers = {'Accept': 'application/json'}
        self.gather()

    def gather(self):
        response = requests.get(self.urls["interactions"].format(self.uniprot_id), headers=self.headers)
        content = warn_for_status(response, "issues with gathering interaction data from intact")
        if content is not None:
            content = json.loads(content)
            content = pd.DataFrame(content[0]["interactions"])
        self.interactions = content

    # TODO need to move logic out of there for recursion need a __method__


class Isoforms:
    def __init__(self, uniprot):
        self.isoforms = None
        self.uniprot_id = uniprot.uniprot_id
        self.url = 'https://www.ebi.ac.uk/proteins/api/proteins/{}/isoforms'
        self.headers = {'Accept': 'application/json'}
        self.gather()

    def gather(self):
        isoforms = []
        isoforms_response = requests.get(self.url.format(self.uniprot_id), headers=self.headers)
        if isoforms_response.status_code != 200:
            warnings.warn("Did not find any isoforms for {}".format(self.uniprot_id))
            self.isoforms = None
        else:
            isoforms_response = json.loads(isoforms_response.content.decode())
            for iso in isoforms_response:
                accession = iso["accession"]
                comments = [comment["type"] for comment in iso["comments"]]
                sequence = iso["sequence"]["sequence"]
                external_references = iso["dbReferences"]
                ref_ids = []
                references = [ref for ref in iso["references"]]
                for ref in references:
                    reftypes = ref["citation"]
                    if "dbReferences" in reftypes.keys():
                        for rtype in reftypes:
                            if type(rtype) == dict:
                                if rtype["type"] == "Pubmed":
                                    ref_ids.append(type["id"])
                isoform = {"accession": accession, "comments": comments, "sequence": sequence, "pubmed_id": ref_ids,
                           "external_references": external_references, }
                isoforms.append(isoform)
            self.isoforms = isoforms
        return self


class Mutagenesis:
    def __init__(self, uniprot):
        """
        query the uniprot API for mutagenesis data this is different than variations, these are not variations that are
        seen in the wild but from experimental data
        :param uniprot: uniprot class
        """
        self.uniprot_id = uniprot.uniprot_id
        self.url = 'https://www.ebi.ac.uk/proteins/api/mutagenesis?offset=0&size=-1&accession={}'
        self.headers = {'Accept': 'application/json'}
        self.mutations = self.gather()

    def gather(self):
        mutations = []
        mutations_response = requests.get(self.url.format(self.uniprot_id), headers=self.headers)
        mutations_response = warn_for_status(mutations_response, "issues with gathering mutagenesis data")
        mutations_response = json.loads(mutations_response)
        if mutations_response is not None and len(mutations_response) > 0:
            mutations_response = mutations_response[0]["features"]
            for mutation in mutations_response:
                type = mutation["type"]
                alt = mutation["alternativeSequence"]
                start = mutation["begin"]
                end = mutation["end"]
                description = mutation["description"]
                references = [ref["source"]["id"] for ref in mutation["evidences"] if ref["source"]["name"] == "PubMed"]
                mut = {"type": type, "description": description, "start": start, "end": end, "alt": alt,
                       "pubmed_id": references, }
                mutations.append(mut)
            mutations = pd.DataFrame(mutations)
        else:
            mutations = None

        return mutations
