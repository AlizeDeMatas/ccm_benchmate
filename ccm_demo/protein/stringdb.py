

#TODO maybe to networkx?
class StringDb:
    def __init__(self, name, species=9606, network_depth=1):
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
        response = requests.get(
            f"https://string-db.org/api/json/network?identifiers={self.string_id}")
        response.raise_for_status()

        interactions = response.content.decode().strip()
        interactions = json.loads(interactions)
        self.interactions=interactions
        return self

    def get_network(self, depth=1, visited_nodes=None):
        if visited_nodes is None:
            visited_nodes = set()

        if self.string_id in visited_nodes or depth < 1:
            return {}

        visited_nodes.add(self.string_id)
        interactions = self.get_interactions(self.string_id)
        results = {self.string_id: interactions}

        while depth > 1:
            for interaction in interactions:
                a = interaction["preferredName_A"]
                b = interaction["preferredName_B"]
                for partner in (a, b):
                    if partner not in visited_nodes:
                        results.update(self.get_network(partner, depth, visited_nodes))
            depth -= 1
        self.network = results
        return self

    def __str__(self):
        return self.annotation

    #TODO add another protein and its network to this
    def __add__(self, other, include_interactions=True):
        pass

    #TODO remote protein from this
    def __sub__(self, other, include_interactions=True):
        pass
