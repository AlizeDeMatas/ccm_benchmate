# TODO this will include Gtex, biogrid, Omnipath and reactome (not sure if this is needed)

import pandas as pd
import requests
import json

#TODO: add docstrings to all classes and methods not all methods are implemented yet.

class BioGrid:
    def __init__(self, access_key):
        """
        Initialize the BioGrid class with the provided access key.
        :param access_key: you can get one from https://webservice.thebiogrid.org/
        """
        self.access_key = access_key
        self.evidence_types = self._get_evidence_types()
        self.organisms=self._get_organisms()
        self.id_types=self._get_supported_identifiers()

    def interactions(self, gene_list, id_types=None, evidence_types=None):
        """
        Get the interactions for the given gene list.
        :param gene_list: list of genes
        :param id_types: the type of the identifier, e.g. "entrez", "uniprot", "ensembl"
        :param evidence_types: see self.evidence_types
        :return: a pandas dataframe with the interactions and kinds of evidences that support them
        """
        params= {
            "geneList": "|".join(gene_list),
            "additionalIdentifierTypes": "|".join(id_types),
            "evidenceList": "|".join(evidence_types),
            "accessKey": self.access_key
        }
        if evidence_types is not None:
            params["includeEvidence"]=True

        url = f"https://webservice.thebiogrid.org/interactions?{params}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results=[]
            for interaction, values in data.items():
                results.append(values)
            df = pd.DataFrame(results)
            return df
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def _get_evidence_types(self):
        """
        Get the evidence types from BioGrid.
        :return: A list of evidence types.
        """
        url = f"https://webservice.thebiogrid.org/evidenceTypes?accessKey={self.access_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content.decode().split("\n")
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def _get_organisms(self):
        """
        Get the organisms from BioGrid.
        :return: A list of organisms.
        """
        url = f"https://webservice.thebiogrid.org/organisms?accessKey={self.access_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content.decode().split("\n")
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def _get_supported_identifiers(self):
        """
        Get the supported identifiers from BioGrid.
        :return: A list of supported identifiers.
        """
        url = f"https://webservice.thebiogrid.org/supportedIdentifiers?accessKey={self.access_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content.decode().split("\n")
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")


class IntAct:
    def __init__(self, page=0, page_size=100):
        self.url = 'https://www.ebi.ac.uk/intact/ws/interaction/findInteractions/{}?page={}&pageSize={}'
        self.page = page
        self.page_size = page_size

    def _search(self, ebi_id):
        """
        Search for interactions in IntAct database.
        :param ebi_id: The EBI ID to search for.
        :return: A list of interactions.
        """

        intact_response = requests.get(self.url.format(ebi_id, self.page, self.page_size))
        intact_response.raise_for_status()
        intact_response = json.loads(intact_response.content.decode())
        interactions = []
        for ints in intact_response["content"]:
            interaction = {"idA": ints["idA"], "idB": ints["idB"], "taxidA": ints["taxIdA"], "taxidB": ints["taxIdB"],
                           "experimental_role_A": ints["experimentalRoleA"],
                           "experimental_role_B": ints["experimentalRoleB"], "stoichiometry_A": ints["stoichiometryA"],
                           "stoichiometry_B": ints["stoichiometryB"], "detection_method": ints["detectionMethod"],
                           "annotations": "\n".join(item for item in ints["allAnnotations"]),
                           "is_negative": ints["negative"], "affected_by_mutation": ints["affectedByMutation"],
                           "pubmed_id": ints["publicationPubmedIdentifier"], "score": ints["intactMiscore"], }

            interactions.append(interaction)
        if intact_response["last"]:
            last_page = True
        else:
            last_page = False

        return interactions, last_page

    def intact_search(self, ebi_id, page=0, page_size=1000):
        interactions, last_page = self._search(ebi_id, page, page_size)
        while not last_page:
            page = page + 1
            next_page_interactions, last_page = self._search(ebi_id, page=page, page_size=page_size)
            interactions.extend(next_page_interactions)
        interactions = pd.DataFrame(interactions)
        return interactions