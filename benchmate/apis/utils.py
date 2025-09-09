from dataclasses import dataclass
from datetime import datetime
from functools import wraps

from benchmate.apis.ensembl import Ensembl
from benchmate.apis.ncbi import Ncbi
from benchmate.apis.reactome import Reactome
from benchmate.apis.uniprot import UniProt
from benchmate.apis.stringdb import StringDb
from benchmate.apis.rnacentral import RnaCentral
from benchmate.apis.others import BioGrid, IntAct


@dataclass
class ApiCall:
    """
    Stores metadata and results of an API call. This is to make it easier to track api calls for knowledge base construction.
    """
    class_name: str = None
    method_name: str = None
    results: dict = None
    args: tuple= None
    kwargs: dict = None
    query_time: datetime = None

    def __str__(self):
        return f"ApiCall @ {self.query_time} with args:{self.args}, kwargs:{self.kwargs}"

    def __repr__(self):
        return self.__str__()

def api_call(func):
    """
    add metadata to an api call and return the apicall dataclass instance insteaed of just a dict
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        query_time = datetime.now()
        result = func(*args, **kwargs)

        return ApiCall(
            class_name=args[0].__class__.__name__,
            method_name=func.__name__,
            results=result,
            args=args[1:],  # exclude 'self'
            kwargs=kwargs,
            query_time=query_time
        )
    return wrapper


class Apis:
    """
    This is just an aggreation of the classes in the apis section, this will be part of the project class, as new methods
    are being developed they will be added here, we need to add it to 2 different locations, the api class instances should be
    in one of the self attributes and the name of the instance should be in the "api_clients_to_decorate" list.
    """

    def __init__(self, email, biogrid_api_key):
        """
        collect all the apis in one place
        :param email:
        :param biogrid_api_key:
        """

        self.ensembl= Ensembl()
        self.ncbi=Ncbi(email=email)
        self.reactome=Reactome()
        self.uniprot=UniProt()
        self.stringdb=StringDb()
        self.biogrid=BioGrid(access_key=biogrid_api_key)
        self.rnacentral=RnaCentral()
        self.intact=IntAct()

        api_clients_to_decorate = [
            self.ensembl, self.ncbi, self.reactome, self.uniprot,
            self.stringdb, self.biogrid, self.rnacentral, self.intact
        ]

        for instance in api_clients_to_decorate:
            self._decorate(instance)

    def _decorate(self, instance):
        """
        go through all the attributes of the instance and decotrate the availabl methods, this is a little bit
        too much since we are decorating all the non dunder methods but it's easier and more flexible as we add more
        instances and more methods.
        :param instance:
        :return:
        """
        # Iterate over the attributes of the instance
        for attr_name in dir(instance):
            if not attr_name.startswith("__"):
                attr = getattr(instance, attr_name)
                if callable(attr):
                    unbound_method = getattr(instance.__class__, attr_name)
                    decorated_method = api_call(unbound_method)
                    setattr(instance, attr_name, decorated_method.__get__(instance))




