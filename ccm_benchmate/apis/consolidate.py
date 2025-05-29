# Consolidate imports from various modules in the ccm_benchmate.apis package

from ccm_benchmate.apis import (
    ensembl,
    ncbi,
    others,
    reactome,
    uniprot,
    rna, stringdb
)

class ApiCalls:
    def __init__(self):
        self.ensembl=ensembl.Ensembl()
        self.ncbi=ncbi.Ncbi()
        self.reactome=reactome.Reactome()
        self.uniprot=uniprot.UniProt()
        #self.rfamily=rna.Rfam()
        self.rnacentral=rna.RnaCentral()
        self.gtex=others.GTEX()
        self.intact=others.IntAct()
        self.stringdb=stringdb.StringDb()
        self.biogrid=others.BioGrid()

        self.available_apis=["ensembl", "ncbi", "reactome", "uniprot",
                             "rnacentral", "gtex", "intact", "stringdb", "biogrid"]

    def _call_apis(self, ids, **kwargs):
    #ids are a dict with api names and the ids to query
        pass

    def _consolidate_xrefs(self, results):
        pass

    def _consolidate_references(self, results):
        pass

    def _get_other_ids(self, ids):
        #TODO need to figure out how to get other ids from the results and then pass them to the other apis
        pass





