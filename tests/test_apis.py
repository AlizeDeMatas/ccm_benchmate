from datetime import timedelta, datetime
from benchmate import apis

from benchmate.apis.ensembl import Ensembl
from benchmate.apis.ncbi import Ncbi
from benchmate.apis.reactome import Reactome
from benchmate.apis.uniprot import UniProt
from benchmate.apis.stringdb import StringDb
from benchmate.apis.rnacentral import RnaCentral
from benchmate.apis.others import BioGrid, IntAct

from benchmate.apis.utils import Apis, ApiCall

email="mail@mail.com"
biogrid_api_key="123456789"

apis=Apis(email=email, biogrid_api_key=biogrid_api_key)

#TODO need add a legit api key using pyenv for actual testing
class TestApis:
    def test_init(self):
        assert isinstance(apis.biogrid, BioGrid)
        assert isinstance(apis.intact, IntAct)
        assert isinstance(apis.ncbi, Ncbi)
        assert isinstance(apis.reactome, Reactome)
        assert isinstance(apis.uniprot, UniProt)
        assert isinstance(apis.stringdb, StringDb)
        assert isinstance(apis.rnacentral, RnaCentral)

class TestEnsembl:
    def test_ensembl_variation_basic(self):
        info = apis.ensembl.variation("rs56116432", add_annotations=False)
        assert isinstance(info, ApiCall)
        assert isinstance(info.query_time, datetime)
        assert info.query_time > datetime.now() - timedelta(minutes=1)
        assert info.class_name == "Ensembl"
        assert info.method_name == "variation"
        assert info.args == ("rs56116432",)
        assert info.kwargs == {"add_annotations": False}
        assert info.results is not None
        assert isinstance(info.results, dict)

    def test_ensembl_variation_pub(self):
        info = apis.ensembl.variation("26318936", method="publication", pubtype="pubmed")
        assert isinstance(info.query_time, datetime)
        assert info.query_time > datetime.now() - timedelta(minutes=1)
        assert isinstance(info, ApiCall)
        assert info.class_name == "Ensembl"
        assert info.method_name == "variation"
        assert info.args == ("26318936",)
        assert info.kwargs == {"method": "publication", "pubtype": "pubmed"}
        assert info.results is not None
        assert isinstance(info.results, list)

    def test_ensembl_variation_translate(self):
        info = apis.ensembl.variation("rs56116432", method="translate")
        assert isinstance(info.query_time, datetime)
        assert info.query_time > datetime.now() - timedelta(minutes=1)
        assert isinstance(info, ApiCall)
        assert info.class_name == "Ensembl"
        assert info.method_name == "variation"
        assert info.args == ("rs56116432",)
        assert info.kwargs == {"method": "translate"}
        assert info.results is not None
        assert isinstance(info.results, list)

    def test_ensembl_vep(self):
        pass


class TestNcbi:
    pass


class TestReactome:
    pass


class TestUniProt:
    pass

class TestStringDb:
    pass

class TestRnaCentral:
    pass

class TestBioGrid:
    pass

class TestIntAct:
    pass

