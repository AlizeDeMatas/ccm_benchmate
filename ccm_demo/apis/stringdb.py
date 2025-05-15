import json
import requests

#TODO maybe to networkx?
# also need to remove the name, species and network depth from the constructor
class StringDb:
    def __init__(self, name, species=9606, network_depth=1):
        """
        constructor for StringDb class
        :param name: some sort of identifier for the protein it support uniprot, gene name, gene name synonyms
        :param species: species id for the protein, default is human, you can taxanomy id from ncbi
        :param network_depth: how deep you want to go in the network, default is 1, if more than 1 it will re search all the
        results for the next depth this will increase the time it takes to get the network and the number will increase exponentially
        """
        # name parameter supports use of uniprot id, uniprot accession #, gene name, or gene name synonyms
        # default organism is homo sapiens

        self.name = name
        if species is None:
            species = 9606
        else:
            self.species = species
        self.get_identifiers()
        self.get_interactions()
        self.get_network(network_depth)

    def get_identifiers(self):
        """
        get all the identifiers for the protein of interest.
        :return: self (will change)
        """
        response = requests.get(
                f"https://string-db.org/api/json/get_string_ids?identifiers={self.name}&species={self.species}")

        response.raise_for_status()
        content = response.content.decode().strip()
        content = json.loads(content)

        self.string_id = content[0]["stringId"]
        self.common_name = content[0]["preferredName"]
        self.annotation=content[0]["annotation"]
        return self

    def get_interactions(self):
        """
        return interactions
        :return: self
        """
        response = requests.get(
            f"https://string-db.org/api/json/network?identifiers={self.string_id}")
        response.raise_for_status()

        interactions = response.content.decode().strip()
        interactions = json.loads(interactions)
        self.interactions=interactions
        return self

    #TODO add a depth parameter to this when calling the function after refactoring
    def get_network(self, visited_nodes=None):
        """
        generate a network of interactions for the protein of interest
        :param depth:
        :param visited_nodes:
        :return:
        """
        if visited_nodes is None:
            visited_nodes = set()

        if self.string_id in visited_nodes or self.depth < 1:
            return {}

        visited_nodes.add(self.string_id)
        interactions = self.get_interactions(self.string_id)
        results = {self.string_id: interactions}
        current_depth = self.depth
        while current_depth >= 1:
            for interaction in interactions:
                a = interaction["preferredName_A"]
                b = interaction["preferredName_B"]
                for partner in (a, b):
                    if partner not in visited_nodes:
                        results.update(self.get_network(partner, current_depth, visited_nodes))
            current_depth -= 1
        self.network = results
        return self

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