import os

import requests
import json
import pandas as pd



#TODO This is not done, but also not sure if needed
class Rfam:
    def __init__(self, rfam_api_url: str = "https://rfam.org/"):
        self.rfam_api_url = rfam_api_url,
        self.headers = {"Content-Type": "application/json"}

    # a function for each endpoint
    def family(self, family_id: str):
        """
        Get information about a specific Rfam family.
        :param family_id: The ID of
        :return: A dictionary containing information about the family.
        """
        pass

    def secondary_structure(self, id: str, type: str):
        """
        Get the secondary structure of a specific Rfam family.
        :param family_id: The ID of the family.
        :return: A dictionary containing the secondary structure information.
        """
        if type not in ["cons", "fcbp", "cov", "ent", "maxcm", "norm", "rscape", "rscape-cyk"]:
            raise ValueError("Invalid type. Must be one of ['cons', 'fcbp', 'cov', 'ent', 'maxcm', 'norm', 'rscape', 'rscape-cyk']")

        else:
            self._get_data(self.base_url + f"/")


    def regions(self, id: str):
        """
        Get the regions of a specific Rfam family.
        :param family_id: The ID of the family.
        :return: A dictionary containing the regions information.
        """
        pass


    def phylogenic_tree(self, id: str):
        """
        Get the phylogenic tree of a specific Rfam family.
        :param family_id: The ID of the family.
        :return: A dictionary containing the phylogenic tree information.
        """
        pass

    def alignments(self, id: str, format: str = "stockholm"):
        """
        Get the alignments of a specific Rfam family.
        :param family_id: The ID of the family.
        :return: A dictionary containing the alignments information.
        """
        pass



# this might not be that useful either but it's there
class RNAcentral:
    def __init__(self, id, rna_central_api_url: str = "https://rnacentral.org/api/v1"):
        self.rna_central_api_url = rna_central_api_url
        self.headers = {"Content-Type": "application/json"}
        self.response=self.get_information(id)
        xrefs_page=self.response["xrefs"]
        xrefs=[]
        while xrefs_page is not None:
            page_xrefs, xrefs_page = self.get_xrefs(xrefs_page)
            xrefs.append(page_xrefs)
        self.get_xrefs=pd.concat(xrefs)

        publications_page=self.response["publications"]
        pubs=[]
        while publications_page is not None:
            page_pubs, publications_page = self.get_publications()
            pubs.append(page_pubs)
        self.publications=pd.concat(pubs)


    def get_information(self, id:str):
        """
        Get information about a specific RNAcentral entry.
        :param id: The ID of the entry.
        :return: A dictionary containing information about the entry.
        """
        url = f"{self.rna_central_api_url}/api/v1/accession/{id}/"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")


    def get_xrefs(self, url):
        """
        :param id:
        :return:
        """
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            response = response.json()
            data=[]
            for item in response["results"]:
                results={}
                for key, value in item.items():
                    if key=="accession":
                        for acc_key, acc_value in value.items():
                            results[acc_key]=acc_value
                    else:
                        results[key]=value
                data.append(results)
            df = pd.DataFrame(data)
            return df, response["next"]
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")


    def get_publications(self):
        """
        :return:
        """
        url=self.response["publications"]
        response=requests.get(url, headers=self.headers)
        if response.status_code == 200:
            response=response.json()
            response=response["results"]
            data=[]
            for item in response:
                results={"title":item["title"],
                         "publication":item["publication"],
                         "pmid":item["pubmed_id"],
                         "doi":item["doi"],
                         "pub_id":item["pub_id"],
                         "expert_db":item["expert_db"],}
                data.append(results)
            df = pd.DataFrame(data)
            return df, response["next"]
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")




