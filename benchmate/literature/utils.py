import os
import tarfile

import torch
import json

from benchmate.utils.general_utils import *

def extract_pdfs_from_tar(file, destination):
    """
    extract all pdf files from a tar.gz file to a destination folder and return the paths to the extracted pdf files
    this is there to process pmc tar.gz files
    :param file: downloaded tar.gz file
    :param destination: where to extract the pdf files
    :return: a list of paths to the extracted pdf files
    """
    if not os.path.exists(destination):
        raise FileNotFoundError("{} does not exist.".format(destination))

    try:
        if file.endswith(".tar.gz"):
            read_str="r:gz"
        elif file.endswith(".tar.bz2"):
            read_str="r:bz2"
        elif file.endswith(".zip"):
            read_str="r:zip"
        else:
            read_str="r"

        paths=[]
        with tarfile.open(file, read_str) as tar:
            for member in tar.getmembers():
                if member.name.endswith("pdf"):
                    tar.extract(member, destination)
                    paths.append(os.path.abspath(os.path.join(destination, file, member.name)))

        return paths

    except FileNotFoundError:
        print(f"Error: File not found: {file}")
        return None

    except tarfile.ReadError:
        print(f"Error: Could not open or read {file}. It might be corrupted or not a valid tar.gz file.")
        return None

#This is not for the end user, this is for the developers
def filter_openalex_response(response, fields=["id", "ids", "doi", "title", "topics", "keywords", "concepts",
                "mesh", "best_oa_location", "referenced_works", "related_works",
                "cited_by_api_url", "datasets"]):
    """
    filters the openalex response to only include the specified fields
    :param response: openalex response
    :param fields: which fields to include a list of strings
    :return: new response with only the specified fields
    """
    if fields is None:
        fields=["id", "ids", "doi", "title", "topics", "keywords", "concepts",
                "mesh", "best_oa_location", "referenced_works", "related_works",
                "cited_by_api_url", "datasets"]
    new_response = {}
    for field in fields:
        if field in response.keys():
            new_response[field] = response[field]
    return new_response

# the whole citeby references etc need to be removed and then re-written as a separate function
# I give up on semantic scholar, it is unlikely I will get an api key, and openalex is good enough
def search_openalex(id_type, paper_id, fields=None):
    """
    api call for openalex to retrieve paper information
    :param id_type: pubmed or arxiv
    :param paper_id: the id
    :param fields: which field to get, passed to filter_openalex_response
    :return:
    """
    base_url = "https://api.openalex.org/works/{}"
    if id_type == "doi":
        paper_id = f"https://doi.org/:{paper_id}"
    elif paper_id == "MAG":
        paper_id = f"mag:{paper_id}"
    elif id_type == "pubmed":
        paper_id = f"pmid:{paper_id}"
    elif id_type == "pmcid":
        paper_id = f"pmcid:{paper_id}"
    elif id_type == "openalex":
        paper_id=paper_id

    url = base_url.format(paper_id)
    response = requests.get(url)
    try:
        response = json.loads(response.content.decode().strip())
        new_response = filter_openalex_response(response, fields)
    except:
        raise ValueError("Could not retrieve information for paper id {} of type {}".format(paper_id, id_type))

    return new_response

# its here, not sure if I will use it, still waiting for an api key, feel like not gonna happen
def search_semantic_scholar(paper_id, id_type, api_key=None, fields=None):
    """
    api call for semantic scholar to retrieve paper information, requires an api key
    :param paper_id: paper id
    :param id_type: id type, doi, arxiv, mag, pubmed, pmcid, ACL
    :param api_key: api key for semantic scholar
    :param fields: which fields to retrieve, list of strings
    :return: a dict with the paper information, this is currently not used not it is compatible with the paper class or other
    supporting functions
    """
    base_url="https://api.semanticscholar.org/graph/v1/paper/{}?fields={}"
    if id_type == "doi":
        paper_id=f"DOI:{paper_id}"
    elif id_type == "arxiv":
        paper_id=f"ARXIV:{paper_id}"
    elif paper_id == "mag":
        paper_id=f"MAG:{paper_id}"
    elif id_type == "pubmed":
        paper_id=f"PMID:{paper_id}"
    elif id_type == "pmcid":
        paper_id=f"PMCID:{paper_id}"
    elif id_type == "ACL":
        paper_id=f"ACL:{paper_id}"

    available_fields=["paperId", "corpusID", "externalIds", "url", "title", "abstract", "venue",
                      "publicationVenue", "year", "referenceCount", "citationCount", "influentialCitationCount",
                      "isOpenAccess", "openAccessPdf", "fieldsOfStudy", "s2FieldsOfStudy",
                      "publicationTypes", "publicationDate", "journal", "citationStyles", "authors",
                      "citations", "references", "embedding", "tldr"]
    acceptable_fields=[]
    for field in fields:
        if field in available_fields:
            acceptable_fields.append(field)
        else:
            warnings.warn("field '{}' not available".format(field))

    if api_key is not None:
        headers = {
            'X-API-Key': api_key,
            'Accept': 'application/json'
        }
    url=base_url.format(paper_id, ",".join(acceptable_fields))
    response = requests.get(url)
    response.raise_for_status()
    response=json.loads(response.content.decode().strip())
    return response




