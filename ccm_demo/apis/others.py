# TODO this will include Gtex, biogrid, Omnipath and reactome (not sure if this is needed)

import pandas as pd
import requests


class GTEX:
    def __init__(self):
        self.base_url = "https://gtexportal.org/api/v2/"
        self.headers = {"Content-Type": "application/json"}
        self.datasets = ["gtex_v8", "gtex_snrnaseq_pilot", "gtex_10"]
        self.tissues = ["Adipose - Subcutaneous", "Adipose - Visceral (Omentum)", "Adrenal Gland", "Artery - Aorta",
                        "Artery - Coronary", "Artery - Tibial", "Bladder", "Brain - Amygdala",
                        "Brain - Anterior cingulate cortex (BA24)", "Brain - Caudate (basal ganglia)",
                        "Brain - Cerebellar Hemisphere", "Brain - Cerebellum", "Brain - Frontal Cortex (BA9)",
                        "Brain - Hippocampus", "Brain - Hypothalamus", "Brain - Nucleus accumbens (basal ganglia)",
                        "Brain - Putamen (basal ganglia)", "Breast - Mammary Tissue",
                        "Cells - EBV-transformed lymphocytes", "Cells - Transformed fibroblasts", "Cervix - Ectocervix",
                        "Cervix - Endocervix", "Colon - Sigmoid", "Colon - Transverse",
                        "Esophagus - Gastroesophageal Junction", "Esophagus - Mucosa", "Esophagus - Muscularis",
                        "Heart - Atrial Appendage", "Heart - Left Ventricle", "Kidney - Cortex", "Liver", "Lung",
                        "Minor Salivary Gland", "Muscle - Skeletal", "Nerve - Tibial", "Ovary", "Pancreas",
                        "Pituitary Gland", "Prostate", "Skin - Not Sun Exposed (Suprapubic)",
                        "Skin - Sun Exposed (Lower leg)", "Spleen", "Stomach", "Testis", "Thyroid", "Uterus", "Vagina",
                        "Whole_Blood"]

    def eqtl(self, gene, tissue, dataset="gtex_v8", items_per_page=1000, multi_tissue=False, by_location=False,
             grange=None):
        page = 0
        params = {}
        if multi_tissue:
            endpoint = "https://gtexportal.org/api/v2/association/multiTissueEqtl"
        else:
            if by_location:
                endpoint = "https://gtexportal.org/api/v2/association/singleTissueEqtlByLocation"
                if grange is None:
                    raise ValueError("grange must be provided when by_location is True")
                location = {"start": grange.start, "end": grange.end, "chrom": grange.chrom}
                params = {**params, **location}
            else:
                endpoint = "https://gtexportal.org/api/v2/association/singleTissueSqtl"

        if dataset not in self.datasets:
            raise ValueError(f"Invalid dataset. Must be one of {self.datasets}")

        if tissue not in self.tissues and not multi_tissue:
            raise ValueError(f"Invalid tissue. Must be one of {self.tissues}")

        if not multi_tissue:
            common_params = {"gencodeId": gene, "TissueSiteDetailId": tissue, "datasetId": dataset,
                             "itemsPerPage": items_per_page, "page": page}
        else:
            common_params = {"gencodeId": gene, "TissueSiteDetailId": tissue, "datasetId": dataset,
                             "itemsPerPage": items_per_page, "page": page}
        params = {**params, **common_params}

        results = self.fetch_data(endpoint, params)
        return results

    def sqlt(self, gene, tissue, dataset, items_per_page=1000):
        endpoint = "https://gtexportal.org/api/v2/association/singleTissueSqtl"
        if dataset not in self.datasets:
            raise ValueError(f"Invalid dataset. Must be one of {self.datasets}")

        if tissue not in self.tissues:
            raise ValueError(f"Invalid tissue. Must be one of {self.tissues}")
        page = 0
        params = {"gencodeId": gene, "TissueSiteDetailId": tissue, "datasetId": dataset, "itemsPerPage": items_per_page,
                  "page": page}
        results = self.fetch_data(endpoint, params)
        return results

    def ieqtl(self, gene, tissue, dataset, items_per_page=1000):
        endpoint = "https://gtexportal.org/api/v2/association/singleTissueIEqtl"

        if dataset not in self.datasets:
            raise ValueError(f"Invalid dataset. Must be one of {self.datasets}")

        if tissue not in self.tissues:
            raise ValueError(f"Invalid tissue. Must be one of {self.tissues}")

        page = 0
        parameters = {"gencodeId": gene, "TissueSiteDetailId": tissue, "datasetId": dataset,
                      "itemsPerPage": items_per_page, "page": page}
        results = self.fetch_data(endpoint, parameters)
        return results

    def isqtl(self, gene, tissue, dataset, items_per_page=1000):
        endpoint = "https://gtexportal.org/api/v2/association/singleTissueISqtl"

        if dataset not in self.datasets:
            raise ValueError(f"Invalid dataset. Must be one of {self.datasets}")

        if tissue not in self.tissues:
            raise ValueError(f"Invalid tissue. Must be one of {self.tissues}")

        page = 0
        parameters = {"gencodeId": gene, "TissueSiteDetailId": tissue, "datasetId": dataset,
                      "itemsPerPage": items_per_page, "page": page}
        results = self.fetch_data(endpoint, parameters)
        return results

    def fetch_data(self, endpoint, params):
        page = 0
        number_of_pages = 1
        results = []
        while page < number_of_pages:
            response = requests.get(endpoint, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                number_of_pages = data["paging_info"]["numberOfPages"]
                page += 1
                results.append(data["data"])
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")
        return pd.DataFrame(results)

    #TODO
    def expression(self, type, tissue, dataset, attribute=None):
        pass

    #TODO samples, genes, histology and that will be it.

class BioGrid:
    def __init__(self, access_key):
        self.access_key = access_key
        self.evidence_types = self._get_evidence_types()
        self.organisms=self._get_organisms()
        self.id_types=self._get_supported_identifiers()

    def interactions(self, gene_list, id_types=None, evidence_types=None):
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



class OmniPath:
    def __init__(self):
        pass
