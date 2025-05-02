import os.path
import warnings

from bs4 import BeautifulSoup as bs
import requests
import tarfile

from ccm_demo.literature.utils import *

class NoPapersError(Exception):
    pass

class LitSearch:
    def __init__(self, pubmed_api_key=None):
        """
        create the ncessary framework for searching
        :param pubmed_api_key:
        """
        self.pubmed_key = pubmed_api_key

    #TODO advanced search, while technically supported because query is just a string it would be nice if it was explicit
    def search(self, query, database="pubmed", results="id", max_results=1000):
        """
        search pubmed and arxiv for a query, this is just keyword search no other params are implemented at the moment
        :param query:
        :param database:
        :param results: what to return, default is paper id PMID and arxiv id
        :param max_results:
        :return:
        """
        #TODO implement pubmed api key for non-free papers
        if database == "pubmed":
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}&retmax={}".format(query, max_results)
            search_response = requests.get(search_url)
            search_response.raise_for_status()

            soup = bs(search_response.text, "xml")
            ids = [item.text for item in soup.find_all("Id")]

            if results == "doi":
                dois = []
                for paperid in ids:
                    response = requests.get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}".format(paperid))
                    response.raise_for_status()
                    soup = bs(response.text, "xml")
                    dois.append([item.text for item in soup.find_all("ArticleId") if item.attrs["IdType"] == "doi"])
                to_ret=dois
            else:
                to_ret=ids

        elif database == "arxiv":
            search_url="http://export.arxiv.org/api/search_query?{}&max_results={}".format(query, str(max_results))
            search_response = requests.get(search_url)
            search_response.raise_for_status()
            soup = bs(search_response.text, "xml")
            ids=[item.text.split("/").pop() for item in soup.find_all("id")][1:] #first one is the search id
            to_ret= ids
        return to_ret


class Paper:
    def __init__(self, paper_id, id_type="pubmed", filepath=None, citations=False, references=False, related_works=False):
        self.table_interpretation = None
        self.figure_interpretation = None
        self.tables = None
        self.figures = None
        self.text = None
        if paper_id is None and filepath is not None:
            self.file_paths=filepath
        else:
            self.id_type=id_type
            self.id=paper_id
            self.paper_info=search_openalex(id_type=self.id_type, paper_id=self.id, cited_by=citations,
                                            references=references, related_works=related_works)
            if "best_oa_location" in self.paper_info.keys():
                if self.paper_info["best_oa_location"]["pdf_url"] is not None:
                    self.download_link=self.paper_info["best_oa_location"]["pdf_url"]
                else:
                    warnings.warn("Did not find a direct pdf download link")
            else:
                warnings.warn("There is no place to download the paper, this paper might not be open access")

        self.abstract=None

    def get_abstract(self):

        abstract_text=None
        if self.id_type =="pubmed":
            response=requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}".format(self.paper_id))
            response.raise_for_status()
            soup=bs(response.text, "xml")
            abstract=soup.find("AbstractText")
            if abstract is not None:
                abstract_text = soup.find("AbstractText").text

        elif self.id_type == "arxiv":
            response = requests.get("http://export.arxiv.org/api/query?search_query=id:{}".format(self.paper_id))
            response.raise_for_status()
            soup=bs(response.text, "xml")
            abstract_text = soup.find("summary").text
        else:
            raise NotImplementedError("source must be pubmed or arxiv other sources are not implemented")

        self.abstract=abstract_text
        return self

    def download(self, destination):
        download = requests.get(self.download_link, stream=True)
        download.raise_for_status()
        with open("{}/{}.pdf".format(destination, self.id), "wb") as f:
            f.write(download.content)
        file_paths=os.path.abspath(os.path.join("{}/{}.pdf".format(destination, self.id)))
        return file_paths

    def process(self):
        article_text, figures, tables, figure_interpretation, table_interpretation = process_pdf(self.file_path)
        self.text=article_text
        self.figures=figures
        self.tables=tables
        self.figure_interpretation=figure_interpretation
        self.table_interpretation=table_interpretation
        return self






