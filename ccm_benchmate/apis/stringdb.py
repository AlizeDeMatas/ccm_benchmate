import json

import requests


class StringDb:
    def __init__(self):
        """
        constructor for StringDb class
        :param name: some sort of identifier for the protein it support uniprot, gene name, gene name synonyms
        :param species: species id for the protein, default is human, you can taxanomy id from ncbi
        :param network_depth: how deep you want to go in the network, default is 1, if more than 1 it will re search all the
        results for the next depth this will increase the time it takes to get the network and the number will increase exponentially
        """
        # name parameter supports use of uniprot id, uniprot accession #, gene name, or gene name synonyms
        # default organism is homo sapiens
        self.string_id = None,
        self.common_name = None
        self.annotation = None
        self.interactions = None
        self.network = None
        self.name = None
        self.species = None
        self.network_depth = None
        self.depth = 1

    def gather(self, species, name, get_network=False, network_depth=2):
        self.name = name
        self.species = species
        self.network_depth = network_depth
        self.string_id, self.common_name, self.annotation = self._get_identifiers(species, name)
        self.interactions = self._get_interactions(self.string_id)
        if get_network and network_depth > 1:
            self.network = self.get_network(self.string_id, visited_nodes=None, network_depth=network_depth)
        return self

    def _get_identifiers(self, species, name):
        """
        get all the identifiers for the protein of interest.
        :return: self (will change)
        """
        response = requests.get(
            f"https://string-db.org/api/json/get_string_ids?identifiers={name}&species={species}")

        response.raise_for_status()
        content = response.content.decode().strip()
        content = json.loads(content)

        string_id = content[0]["stringId"]
        common_name = content[0]["preferredName"]
        annotation = content[0]["annotation"]
        return string_id, common_name, annotation

    def _get_interactions(self, string_id):
        """
        return interactions
        :return: self
        """
        response = requests.get(
            f"https://string-db.org/api/json/network?identifiers={string_id}")
        response.raise_for_status()

        interactions = response.content.decode().strip()
        interactions = json.loads(interactions)
        return interactions

    def get_network(self, id, visited_nodes=None, network_depth=1):
        """

        :param id:
        :param visited_nodes:
        :param network_depth:
        :return:
        """
        if visited_nodes is None:
            visited_nodes = set()

        if id in visited_nodes or network_depth < 1:
            return {}

        visited_nodes.add(id)
        interactions = self._get_interactions(string_id=id)
        results = {id: interactions}
        current_depth = self.depth
        while current_depth >= 1:
            for interaction in interactions:
                a = interaction["preferredName_A"]
                b = interaction["preferredName_B"]
                for partner in (a, b):
                    if partner not in visited_nodes:
                        results.update(self.get_network(partner, visited_nodes, current_depth))
            current_depth -= 1
        return results

    def __str__(self):
        return self.annotation

    def __repr__(self):
        return f"StringDb({self.name}, {self.species}, {self.network_depth})"

    def __len__(self):
        """
        return the number of interactions
        :return:
        """
        return len(self.interactions)
