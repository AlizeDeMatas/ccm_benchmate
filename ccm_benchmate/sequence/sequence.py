import os
import subprocess

from Bio import Seq, SeqIO
from PIL.features import features

from ccm_benchmate.sequence.utils import *

class Sequence:
    def __init__(self, name, sequence, type="protein", features=None):
        """

        :param name:
        :param sequence:
        :param type:
        :param features:
        """
        types=["dna", "rna", "protein", "3di"]
        if type not in types:
            raise ValueError("Invalid sequence type, types can be {types}".format(types=", ".join(types)))
        self.name = name
        self.sequence = sequence
        features=None
        self.device="cuda" if torch.cuda.is_available() else "cpu"

    #TODO need to be able to also do a DNA/RNA embedding
    def embeddings(self, model="esmc_300m", normalize=False):
        if model == "esmc_300m" or model == "esmc_g00m":
            embeddings=esm3_embeddings(sequence=self.sequence, model=model,
                                       normalize=normalize, device=self.device)
        else:
            raise NotImplementedError("That model is not implemented.")
        return embeddings


    def mutate(self, position, to, new_name=None):
        """
        position is 0 based, create a new instance of the sequence with the mutation
        """
        new_sequence = list(self.sequence)
        if position > len(new_sequence)-1:
            raise ValueError("Position is greater than the sequence length {}".format(len(new_sequence)))
        new_sequence[position] = to

        self.sequence = "".join(new_sequence)
        if new_name is not None:
            self.name = new_name
        return self

    def msa(self, database, destination, output_name="msa.a3m", cleanup=True):
        """
        generate a multiple sequence alignment using mmseqs2 this assumes that you already have a database processed.
        :param database: the database that is ready to go
        :param destination: where to save the results.
        :param output_name: name of the a3m file
        :param cleanup: remove temporary files
        :return: path of the output file
        """
        self.write(os.path.join(destination, "query.fasta"))
        script=os.path.join(__file__.replace("sequence.py", ""), "../scripts/run_mmseqs.sh")
        #TODO better packaging
        command=" ".join(["bash", script, " -i", str(os.path.abspath(os.path.join(destination, "query.fasta"))),
                            "-d", database, "-o", str(os.path.join(destination, output_name)),
                            "-c"])
        run=subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if run.returncode != 0:
            raise ChildProcessError("There was an error with mmseqs run see error below '\n' {}".format(run.stderr))
        else:
            print("mmseqs run complete the results are in {}/{}".format(destination, output_name))

        if cleanup:
            items=["query.fasta", "query.index", "query.dbtype", "query.source", "query.lookup", "query",
                   "query.tab", "query_h", "query_h.dbtype", "query_h.index", "align", "align.dbtype","align.index"]
            for item in items:
                os.remove(os.path.join(destination, item))
        return os.path.join(destination, output_name)

    def blast(self, program, database, threshold=10, hitlist_size=50, write=True):
        """
        using the ncbi blast api run blast, I am not sure if localblast is needed
        :param program: which blast program to use
        :param database: which database to use
        :param threshold: e value threshold
        :param hitlist_size: how many hits to return
        :param write: whether to write the output file
        :return:
        """
        search=blast_search(program, database, self.sequence, threshold, hitlist_size)
        results=parse_blast_search(search)
        #TODO write to file and return path
        if write:
            pass
        return results

    def write(self, fpath):
        seq=SeqIO.SeqRecord(Seq.Seq(self.sequence), id=self.name, description="")
        with open(fpath, "w") as handle:
            SeqIO.write(seq, handle, "fasta")

    #read a simple fasta or from database
    def read(self, fpath, db, id):
        pass

    def __str__(self):
        return "Sequence with name {} and {} aas".format(self.name, len(self.sequence))

#This needs to be different than a list of sequences,
class SequenceList:
    def __init__(self, sequences, features=None):
        """
        Sequence list object, the only reason for you to use this if you want to create a paired msa,
        otherwise a list of Sequence instances will have more features.
        :param sequences: list of Sequence instances
        :param features: a dict of annotations, whatever you want
        """
        for item in sequences:
            assert isinstance(item, Sequence)
        self.sequences = sequences

    #paired msa
    def msa(self, paired=True, **kwargs):

        if not paired:
            msa = []
            for item in self.sequences:
                msa.append=item.msa(kwargs)
        else:
            pass

        return msa


    #TODO return a multifasta
    def write(self, fpath):
        pass

    #TODO read multifasta or from database
    def read(self, fpath, db, id):
        pass