import os
import subprocess
import io
import gzip
from dataclasses import dataclass
from typing import List, Union, Tuple, Optional, BinaryIO

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

import biotite
from biotite.structure import distance, get_chains, alphabet, to_sequence
from biotite.structure.io.pdb import PDBFile
from biotite.structure.io.pdbx import CIFFile, get_structure

from benchmate.utils.general_utils import compressed_stream_manager, decompressed_stream_manager
from benchmate.structure.utils import *
from benchmate.sequence.sequence import Sequence, SequenceList
from benchmate.utils.general_utils import DataIntegrityError



def _read(file):
    if file.endswith(".pdb"):
        structure = PDBFile.read(file).get_structure()[0]
    elif file.endswith(".cif") or file.endswith(".mmcif"):
        file = CIFFile.read(file)
        structure = get_structure(file, model=1)
    else:
        raise NotImplementedError("We can only read PDB or CIF files")
    return structure

@dataclass(slots=True)
class StructureInfo:
    name: str
    atoms: biotite.structure.AtomArray
    chains: List
    annotations: Optional[dict] = None

    #TODO I need to figure out how to write pdb to stream and compress w/o i/o
    def to_kb(self, project):
        structure_table = project.kb.db_tables["structure"]
        with compressed_stream_manager(self.atoms, self.biotite_pdb_transformer) as compressed_pdb:
            row_data = {
                "name": self.name,
                'chains': self.chains,
                "atoms": compressed_pdb,
                "features": self.annotations
            }

            # 3. Execute the insert
            stmt = structure_table().insert().values(**row_data).returning(structure_table.c.id)
        return project.session.execute(stmt)

    @classmethod
    def from_kb(cls, project, id):
        structure_table = project.kb.db_tables["structure"]
        stmt = select(structure_table).where(structure_table.c.id == id)

        results = project.kb.session().execute(stmt).fetchall()

        if len(results) == 0:
            raise NoResultFound("Could not find a molecule with id {}".format(id))

        if len(results) > 1:
            raise DataIntegrityError("Found more than one molecule with id {}".format(id))

        with gzip.GzipFile(fileobj=io.BytesIO(results[0][2]), mode='rb') as gz:
            with io.TextIOWrapper(gz, encoding='utf-8') as text_wrapper:
                pdb_file = PDBFile.read(text_wrapper)
                atom_array = pdb_file.get_structure(model=1)

        return cls(name=results[0][0], atoms=atom_array,
                   chains=results[0][1], annotations=results[0][3])

    def biotite_pdb_transformer(self, binary_stream):
        # We wrap the binary stream in text mode ONLY when needed
        with io.TextIOWrapper(binary_stream, encoding='utf-8', write_through=True) as text_wrapper:
            pdb_file = PDBFile()
            pdb_file.set_structure(self.atoms)
            pdb_file.write(text_wrapper)

    def biotite_pdb_reconstructor(self, binary_stream: BinaryIO):
        # Wrap in text mode for the PDB parser
        with io.TextIOWrapper(binary_stream, encoding='utf-8') as text_wrapper:
            pdb_file = PDBFile.read(text_wrapper)
            return pdb_file.get_structure(model=1)


class Structure:
    def __init__(self, name, atoms, annotations:dict=None):
        """
        :param name: name
        :param file: pdb or cif file
        :param id: id can be none if file is none and id is not we will download from source
        :param source: where to get the pdb from
        :param destination: where to download it, these are passed to structure.utils.download
        """
        chains = get_chains(atoms)
        self.info=StructureInfo(name, atoms, chains, annotations)

    #TODO parse these
    def align(self, other, destination):
        """
        align 2 structures (they must have a file) using mustang
        :param other:  other structure
        :param destination: where to save the output
        :return: result of the file, html output for alignment and rotation
        """
        file1=self.write(destination + "structure1.pdb")
        file2=other.write(destination + "structure2.pdb")

        command = ["mustang", "-i", os.path.abspath(file1), os.path.abspath(file2), "-o",
                   os.path.abspath(destination), "-r", "ON"]

        process = subprocess.run(command)
        if process.returncode != 0:
            raise ValueError("There was an error aligning structures. See error below \n {}".format(process.stderr))

        aligned_pdb = os.path.abspath(destination + "results.pdb")
        rotation_file = os.path.abspath(destination + "results.rms_rot")
        html_report = os.path.abspath(destination + "results.html")
        return aligned_pdb, rotation_file, html_report

    def find_pockets(self, **kwargs):
        """
        Run fpocket on this structure and return detected pocket info.
        Returns (pocket_files, pocket_coords)
        """
        cmd_params = " ".join([f"--{k} {v}" for k, v in kwargs.items()])
        command = f"fpocket -f {self.file} -x -d {cmd_params}"
        run = subprocess.run(command, shell=True, capture_output=True, text=True)

        if run.returncode != 0:
            raise RuntimeError(run.stderr)

        results_dir = self.file.replace(".pdb", "_out")
        pocket_files = [f for f in os.listdir(results_dir) if f.endswith(".pdb")]
        pocket_coords = [get_pocket_dimensions(os.path.join(results_dir, f)) for f in pocket_files]

        return pocket_files, pocket_coords

    def to_3di(self, chain):
        "for a chain convert the structure to 3di"
        chain=self._get_chain(chain)
        seq, _ = str(alphabet.to_3di(chain)[0])
        return Sequence(name=self.info.name + "_" + chain.chain_id, sequence=seq, seq_type="3di")

    def sequence(self):
        "extract the aa sequence from the pdb, if there are gap there will be - if there are uknown aa there will be an X"
        seqs=[]
        for chain in self.info.chains:
            chain_atoms = self._get_chain(chain)
            seq=to_sequence(chain_atoms, allow_hetero=True)[0][0]
            seq = str(seq)
            seqs.append(Sequence(name=self.info.name + "_" + chain, sequence=seq, seq_type="protein"))
        if len(seqs) == 1:
            return seqs[0]
        else:
            return SequenceList(seqs)

    def tm_score(self, other):
        """
        run us-align to get the tm score between 2 structures
        :param other: other structure
        :return: retun the tm score
        """
        assert(isinstance(other, Structure))
        cmd = ["USalign", self.file, other.file, "-outfmt", "2"]
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode != 0:
            raise RuntimeError(run.stderr)
        for line in run.stdout.splitlines():
            if "TM-score=" in line:
                return float(line.split("=")[1].split()[0])
        return None

    def _get_chain(self, chain_id):
        return self.structure[self.structure.chain_id == chain_id]

    def write(self, fpath):
        PDBFile.write(self.file, fpath)

    def contacts(self, chain_id1, chain_id2, cutoff=5.0, level="atom", measure="any"):
        """
        Get contacts between two chains in the structure.
        :param chain_id1: chain 1
        :param chain_id2: chain 2
        :param cutoff: distance cutoff to be called contacting default 5A
        :param level: if "atom" return the contacting atom, if residue return the resdiues
        :measure: how the contact is calculated, if any any atom within the cutoff range will be included
        if CA only alpha carbons are counted
        :return:a list of atoms, residues etc.
        """
        chain1 = self._get_chain(chain_id1)
        chain2 = self._get_chain(chain_id2)
        contacts=[]
        for i in range(len(chain1)):
            for j in range(len(chain2)):
                if measure == "any":
                    dist = distance(chain1[i], chain2[j])
                elif measure=="CA":
                    if "CA" in chain1[i].atom_name and "CA" in chain2[j].atom_name:
                        dist = distance(chain1[i], chain2[j])
                    else:
                        continue
                if dist < cutoff:
                    if level == "atom":
                        contacts.append({chain_id1: i, chain_id2: j,
                                     "distance": dist})
                    elif level == "residue":
                        contacts.append({chain_id1: chain1[i].res_id, chain_id2: chain2[j].res_id,
                                     "distance": dist})

        return contacts

    def __repr__(self):
        return "Structure(name={}, pdb={}, chains={})".format(self.info.name, self.info.file, ",".join(self.chains))

    def __str__(self):
        return self.file

    def __getitem__(self, key: Union[str, int, slice, Tuple[str, Union[int, str]]]):
        """
        Support indexing:
          - structure['A'] -> returns chain atoms (Biotite AtomArray slice)
          - structure[0] -> returns first chain atoms (by order in self.chains)
          - structure['A', 100] -> returns list of atoms belonging to residue id 100 in chain A
          - structure[0:2] -> list of chain AtomArray slices for the first two chains
        """
        if isinstance(key, str):
            return self._get_chain(key)
        if isinstance(key, int):
            chain_id = self.chains[key]
            return self._get_chain(chain_id)
        if isinstance(key, slice):
            sel = self.chains[key]
            return [self._get_chain(ch) for ch in sel]
        if isinstance(key, tuple) and len(key) == 2:
            chain_id, resid = key
            chain = self._get_chain(chain_id)
            atoms = [atom for atom in chain if atom.res_id == resid]
            return atoms
        raise KeyError(f"Unsupported key type: {type(key)}")

    @classmethod
    def from_file(cls, name, file, source=None, destination=None, id=None):
        if file is not None:
            file = os.path.abspath(file)
            structure=_read(file)

        if file is None and id is not None:
            file=os.path.abspath(download(id, source, destination))
            structure = _read(file)

        if file is None and id is None:
            raise ValueError("You must provide a file or an id as well as a source and destination")

        atoms=structure.get_structure()
        return cls(name, atoms)

    @classmethod
    def from_kb(cls, project, id):
        info=StructureInfo.from_kb(project, id)
        struct=cls(name=info.name, atoms=info.atoms, annotations=info.annotations)
        struct.info=info
        return struct

    def to_kb(self, project):
        return self.info.to_kb(project)

