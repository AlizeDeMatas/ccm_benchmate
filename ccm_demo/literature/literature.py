import os.path

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

#TODO bibtex support to backwards pull abstracts
class Paper:
    def __init__(self, source, id=None, filepath=None, destination=None):
        if id is None and filepath is not None:
            self.file_paths=filepath
        else:
            self.file_paths = None
            self.source = source
            self.download_link = None
            self.title = None
            self.abstract = None
            self.id = id
            self.get_meta()
            self.download(destination)
        self.table_interpretation = None
        self.figure_interpretation = None
        self.text = None
        self.figures = None
        self.tables = None
        #self.process()

    #TODO get mesh?, get references?
    def get_meta(self):
        if self.source =="pubmed":
            response=requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}".format(self.id))
            response.raise_for_status()
            soup=bs(response.text, "xml")
            self.title = soup.find("ArticleTitle").text
            abstract=soup.find("AbstractText")
            if abstract is not None:
                self.abstract = soup.find("AbstractText").text
            id_list=[item for item in soup.find_all("PubmedData")[0] if item.name=="ArticleIdList"][0]
            pmc = [item.text for item in id_list if item["IdType"] == "pmc"]
            if len(pmc) ==1 :
                pmc_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={}".format(pmc[0])
                response = requests.get(pmc_url)
                response.raise_for_status()
                links=bs(response.text, "xml").find_all("link")
                if len(links) > 0:
                    self.download_link=links[0]["href"].replace("ftp://", "https://")

        elif self.source == "arxiv":
            response = requests.get("http://export.arxiv.org/api/query?search_query=id:{}".format(self.id))
            response.raise_for_status()
            soup=bs(response.text, "xml")
            self.abstract = soup.find("summary").text
            if self.abstract is None:
                raise NoPapersError("could not find a paper with id {}".format(self.id))
            else:
                titles = soup.find_all("title")
                for title in titles:
                    if "Arxiv Query" in title.text:
                        continue
                    else:
                        self.title = title.text
                links = soup.find_all("link")
                for link in links:
                    if link.has_attr("href") and link.has_attr("type"):
                        if link["type"] == "application/pdf":
                            self.download_link = link["href"]
        else:
            raise NotImplementedError("source must be pubmed or arxiv other sources are not implemented")

        return self

    def download(self, destination):
        if self.source == "pubmed":
            download = requests.get(self.download_link, stream=True)
            download.raise_for_status()
            name="{}/{}.tar.gz".format(destination, self.id)
            with open(name, "wb") as f:
                f.write(download.content)
            file_paths=extract_pdfs_from_tar(name, destination)
        elif self.source == "arxiv":
            download = requests.get(self.download_link, stream=True)
            download.raise_for_status()
            with open("{}/{}.pdf".format(destination, self.id), "wb") as f:
                f.write(download.content)
            file_paths=os.path.join("{}/{}.pdf".format(destination, self.id))
        return file_paths

    def process(self):
        article_text, figures, tables, figure_interpretation, table_interpretation = process_pdf(self.file_path)
        self.text=article_text
        self.figures=figures
        self.tables=tables
        self.figure_interpretation=figure_interpretation
        self.table_interpretation=table_interpretation
        return self






