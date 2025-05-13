import os
import warnings

import requests


from bs4 import BeautifulSoup as bs
from Bio import Entrez

#thin wrapper around the NCBI Entrez API and BioPython
class Entrez:
    def __init__(self, api_key=None, email=None):
        self.search_url= "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.fetch_url= "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        if email is None and api_key is None:
            raise ValueError("No email or API key provided. Please provide an email or API key. Some features may not work or return limited results.")

        self.api_key= api_key
        self.email= email
        databases=requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi")
        databases=bs(databases.content, "xml")
        databases=databases.find_all("DbName")
        self.databases=[db.text for db in databases]
        Entrez.email=self.email
        Entrez.api_key=self.api_key

    def search(self, db, query, retmax=100):
        stream= Entrez.esearch(db=db, term=query, retmax=retmax)
        record = Entrez.read(stream)
        stream.close()
        ids = record["IdList"]

    def summary(self, db, id):
        stream = Entrez.esummary(db=db, id=id)
        record = Entrez.read(stream)
        stream.close()
        return record

    def fetch(self, db, id):
        stream=Entrez.efetch(db=db, id=id, retmode="xml")
        record = Entrez.read(stream)
        stream.close()
        return record

    def show_databses(self):
        return self.databases

    def get_db_info(self, db):
        stream = Entrez.einfo(db=db)
        db_info = Entrez.read(stream)
        record = db_info["DbInfo"]
        return record

