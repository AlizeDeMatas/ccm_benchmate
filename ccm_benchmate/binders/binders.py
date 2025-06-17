# many thanks to @kobehuynh for writing most of this code

import os
import subprocess
from io import StringIO

import pandas as pd
from Bio.PDB import *
import rdkit

parser = PDBParser(PERMISSIVE=1)

from ccm_benchmate.binders.utils import *

# You can provide structure or sequence instance
from ccm_benchmate.sequence.sequence import Sequence
from ccm_benchmate.structure.structure import Structure
from ccm_benchmate.container_runner.container_runner import ContainerRunner

from usearch_molecules.dataset import FingerprintedDataset, shape_ecfp4, shape_fcfp4, shape_maccs


class Ligand:
    def __init__(self, name, target=None, bound_structure=None):
        self.name=name
        self.target=target
        self.bound_structure=bound_structure

        #the binder needs to be one of these, they can be generated using the contructors of each class
        if type(target) is Structure:
            pass
        elif type(target) is Sequence:
            pass
        else:
            raise NotImplementedError("The target can only be a Sequence or Structure class instance")

    #TODO this will use the bound_structure
    def find_contacts(self):
        pass

    #TODO same as above
    def bounding_box(self, use="target", amino_acids=None, use_alpha_carbon=False):
        """
        generate a bounding box around a given list of amino acid ids. This can be used to generate more molecules or
        calculate properties of a pocket
        :param use: target or bound structure, this needs to be a Structure instance
        :param amino_acids: which amino acids to use
        :param use_alpha_carbon: whether to use the alpha carbon or the side chains to get the bounding box
        :return: 6 coordinates of the bounding box
        """

        if use=="target" and type(self.target) is Structure:
            structure = self.target
        elif use=="bound" and type(self.bound_structure) is Structure:
            structure = self.bound_structure
        else:
            raise NotImplementedError("The target can only be a Structure class instance whether bound or apo structure")

        coord = []

        for model in structure:
            for chain in model:
                for residue in chain:
                    if amino_acids is None or residue.resname in amino_acids:
                        for atom in residue:
                            if use_alpha_carbon:
                                if atom.name == "CA":
                                    coord.append(atom.coord)
                            else:
                                coord.append(atom.coord)

        coord_numpy = np.array(coord)

        x_max, y_max, z_max = np.max(coord_numpy, axis=0)
        x_min, y_min, z_min = np.min(coord_numpy, axis=0)

        return {"xmax": x_max, "ymax": y_max, "zmax": z_max, "xmin": x_min, "ymin": y_min, "zmin": z_min}


class SmallMolecule(Ligand):
    def __init__(self, name, smiles=None, target=None, bound_structure=None):
        super().__init__(name, target, bound_structure)
        self.smiles = smiles

    def find_pockets(self, **kwargs):
        """
        :param kwargs: these are additional key value pairs to be fed into fpocket, read its documentation for details
        :return:
        """
        command_params = []
        for key, value in kwargs.items():
            command_params.append(f"--{key} {value}")

        command_params = " ".join(command_params)
        command = "fpocket -f {pdb} -x -d {command_params}".format(pdb=self.pdb, command_params=command_params)
        run = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if run.returncode != 0:
            raise RuntimeError(run.stderr.decode())
        else:
            results = run.stdout.decode()
            pocket_properties = pd.read_csv(StringIO(results), sep=" ")
            pocket_list = [file for file in os.listdir(self.pdb.replace(".pdb", "_out")) if file.endswith(".pdb")]
            pocket_coords = [get_pocket_dimensions(item) for item in pocket_list]
            return pocket_list, pocket_properties, pocket_coords

    def calculate_properties(self):
        pass

    def generate(self, container, **kwargs):
        #use target structure
        pass

    def search(self, library, using="ecfp4", metric="tanimoto", n=100):
        """
        using usearch molecules will search library for a given metric, the only metric implemented is tanimoto similarity
        :param library: a list of directories that contain usearch parquet files
        :param using: the implemented ones are ecfp4, fcfp4 and maccs
        :param metric: tanimoto otherwise NotImplementedError
        :param n: number of molecules to return
        :return: list of smiles for molecules
        """
        if metric != "tanimoto":
            raise NotImplementedError("metric must be tanimoto")

        if using not in ["ecfp4", "fcfp4", "maccs"]:
            raise NotImplementedError("method must be ecfp4 or fcfp4 or maccs")
        elif using == "ecfp4":
            shape = shape_ecfp4
        elif using == "fcfp4":
            shape = shape_ecfp4
        elif using == "maccs":
            shape = shape_maccs

        data = FingerprintedDataset(library, shape=shape)
        results = data.search(smiles=self.smiles, n=n)
        return results

    #run a model like AF3 or boltz to "verify" the bound structure
    def verify(self, container, **kwargs):
        pass

    def generate_molecules(self, container, **kwargs):
        #TODO this will be a containerRunner
        pass


    def calculate_properties(self, *args):
        """
        calculate numerous properties using RDkit simple wrapper
        :param args: properties to get
        :return: returns properites of a smiles string based on args
        """
        pass

    def verify(self, method="AF3"):
        """
        run AF3 to re-predict the structure to verify binding
        :param method:
        :param kwargs:
        :return:
        """
        pass


class PeptideBinder(Ligand):
    def __init__(self):
        pass

    def find_binding_site(self):
        """
        this will again use fpocket
        :return:
        """
        pass

    def generate_peptides(self, region, n):
        pass

    def verify(self, method="AF3", **kwargs):
        pass
