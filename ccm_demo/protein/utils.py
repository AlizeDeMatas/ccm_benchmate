import json

import requests

headers = {"Accept": "application/json"}

urls = {'base_response': "https://www.ebi.ac.uk/proteins/api/proteins?accession={}",
    'interactions': 'https://www.ebi.ac.uk/proteins/api/proteins/interaction/{}',
    'isoforms': 'https://www.ebi.ac.uk/proteins/api/proteins/{}/isoforms',
    'features': 'https://www.ebi.ac.uk/proteins/api/features?offset=0&size=-1&accession={}',
    'variation': 'https://www.ebi.ac.uk/proteins/api/variation?offset=0&size=-1&accession={}',
    'antigen': 'https://www.ebi.ac.uk/proteins/api/antigen?offset=0&size=-1&accession={}',
    'epitope': 'https://www.ebi.ac.uk/proteins/api/epitope?offset=0&size=-1&accession={}',
    'mutagenesis': 'https://www.ebi.ac.uk/proteins/api/mutagenesis?offset=0&size=-1&accession={}',
    'rna-editing': 'https://www.ebi.ac.uk/proteins/api/rna-editing?offset=0&size=-1&accession={}',
    'coordinates': 'https://www.ebi.ac.uk/proteins/api/coordinates?offset=0&size=-1&accession={}',
    'intact': 'https://www.ebi.ac.uk/intact/ws/interaction/findInteractions/{}?page={}&pageSize={}'}


def search_intact(ebi_id, page=0, page_size=100):
    intact_response = requests.get(urls["intact"].format(ebi_id, page, page_size))
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
        last_page=True
    else:
        last_page=False

    return interactions, last_page