import os
import subprocess
import shlex
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
from Bio.PDB import PDBParser, PDBIO, Select

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FoldDisco:
    """
    A Python class for running Folddisco on PDB files, extracting specific chains and residue ranges,
    and building indices from folders of PDB files. Integrates with Folddisco via subprocess calls.

    Requires Folddisco installed and accessible in PATH (e.g., via conda or binary download).
    Uses Biopython for PDB parsing and extraction.
    """

    def __init__(self, pdb_file: str, chain_id: str, residue_range: Optional[Tuple[int, int]] = None):
        """
        Initialize the FolddiscoAnalyzer with a PDB file, optional chain ID, and optional residue range.
        If chain_id and residue_range are provided, the entire PDB is used unless specified.

        Args:
            pdb_file (str): Path to the PDB file.
            chain_id (str): Chain identifier (e.g., 'A'). If None, uses the first chain.
            residue_range (Optional[Tuple[int, int]]): Start and end residue numbers (inclusive).
                If None, uses all residues in the chain.
        """
        self.pdb_file = Path(pdb_file)
        self.chain_id = chain_id.upper() if chain_id else None
        self.residue_range = residue_range
        self.parser = PDBParser(QUIET=True)

        if not self.pdb_file.exists():
            raise FileNotFoundError(f"PDB file {self.pdb_file} does not exist.")

        self.structure = self._load_pdb()
        self._validate_chain_and_residues()

    def _load_pdb(self):
        """Load the PDB file using Biopython's PDBParser."""
        try:
            return self.parser.get_structure('protein', self.pdb_file)
        except Exception as e:
            logger.error(f"Failed to parse PDB file {self.pdb_file}: {e}")
            raise

    def _validate_chain_and_residues(self) -> None:
        """Validate that the chain and residue range exist in the PDB file."""
        model = next(iter(self.structure))
        if self.chain_id:
            if self.chain_id not in model:
                available_chains = list(model.keys())
                raise ValueError(
                    f"Chain {self.chain_id} not found in {self.pdb_file}. Available chains: {available_chains}")
            chain = model[self.chain_id]
        else:
            chain = next(iter(model.values()))
            self.chain_id = chain.id  # Default to first chain

        residue_ids = [res.id[1] for res in chain if res.id[0] == ' ']
        if not residue_ids:
            raise ValueError(f"No standard residues found in chain {self.chain_id}.")

        if self.residue_range:
            start, end = self.residue_range
            if not (min(residue_ids) <= start <= max(residue_ids) and min(residue_ids) <= end <= max(residue_ids)):
                raise ValueError(f"Residue range {self.residue_range} is invalid for chain {self.chain_id}.")

    def _format_residues(self) -> str:
        """
        Format the chain and residue range into Folddisco residue syntax.
        E.g., 'A1-50' or 'A' (all residues in chain).
        """
        if not self.residue_range:
            return self.chain_id  # All residues in chain

        start, end = self.residue_range
        return f"{self.chain_id}{start}-{end}"

    def extract_chain_segment(self, output_pdb: str) -> str:
        """
        Extract the specified chain and residue range to a new PDB file.

        Args:
            output_pdb (str): Path to the output PDB file.

        Returns:
            str: Path to the extracted PDB file.
        """

        class ChainResidueSelect(Select):
            def __init__(self, chain_id: str, residue_range: Optional[Tuple[int, int]] = None):
                self.chain_id = chain_id
                self.start, self.end = residue_range or (None, None)

            def accept_chain(self, chain):
                return chain.id == self.chain_id

            def accept_residue(self, residue):
                if residue.id[0] != ' ':
                    return 0
                res_id = residue.id[1]
                if self.start is not None and self.end is not None:
                    return 1 if self.start <= res_id <= self.end else 0
                return 1  # All residues if no range

        io = PDBIO()
        io.set_structure(self.structure)
        io.save(output_pdb, ChainResidueSelect(self.chain_id, self.residue_range))
        logger.info(
            f"Extracted chain {self.chain_id} {'residues ' + str(self.residue_range) if self.residue_range else 'all residues'} to {output_pdb}")
        return str(Path(output_pdb).resolve())

    def run_query(self, index_path: str, output_file: Optional[str] = None,
                  distance_threshold: float = 0.5, angle_threshold: float = 5.0,
                  threads: int = 4, skip_match: bool = False, top: Optional[int] = None,
                  per_structure: bool = False, header: bool = True, sort_by_rmsd: bool = False,
                  **kwargs: Any) -> Dict[str, Any]:
        """
        Run Folddisco query on the extracted chain segment against the given index.

        Args:
            index_path (str): Path to the Folddisco index directory.
            output_file (Optional[str]): Path to write output (if None, captures stdout).
            distance_threshold (float): Distance threshold in Å (default: 0.5).
            angle_threshold (float): Angle threshold in degrees (default: 5.0).
            threads (int): Number of threads (default: 4).
            skip_match (bool): Skip RMSD calculation for faster pre-filter only (default: False).
            top (Optional[int]): Limit to top N hits.
            per_structure (bool): Output per structure instead of per match (default: False).
            header (bool): Include header in output (default: True).
            sort_by_rmsd (bool): Sort by RMSD (default: False; use sort_by_score for idf_score).
            **kwargs: Additional Folddisco query parameters (e.g., sampling_ratio=0.3, connected_node=0.75).

        Returns:
            Dict[str, Any]: Dictionary with 'stdout' (output text), 'returncode', and 'parsed_results' (list of dicts).
        """
        temp_pdb = self.extract_chain_segment(f"temp_{self.pdb_file.stem}_{self.chain_id}.pdb")
        residues = self._format_residues()

        cmd = [
            "folddisco", "query",
            f"-i {shlex.quote(index_path)}",
            f"-p {shlex.quote(temp_pdb)}",
            f"-q {residues}",
            f"-d {distance_threshold}",
            f"-a {angle_threshold}",
            f"-t {threads}"
        ]

        if skip_match:
            cmd.append("--skip-match")
        if top is not None:
            cmd.append(f"--top {top}")
        if per_structure:
            cmd.append("--per-structure")
        if header:
            cmd.append("--header")
        if sort_by_rmsd:
            cmd.append("--sort-by-rmsd")
        # Note: For sort-by-score, add sort_by_score=True and append "--sort-by-score"

        # Add **kwargs
        for key, value in kwargs.items():
            flag = f"--{key.replace('_', '-')}"
            cmd.extend([flag, str(value)])

        try:
            if output_file:
                with open(output_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, text=True, check=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                stdout = result.stdout
            logger.info(f"Folddisco query completed for {temp_pdb}")

            # Clean up temp file
            Path(temp_pdb).unlink(missing_ok=True)

            return {
                "stdout": stdout if not output_file else open(output_file).read(),
                "returncode": result.returncode,
                "parsed_results": self._parse_folddisco_output(stdout if not output_file else open(output_file).read())
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Folddisco query failed: {e.stderr}")
            raise

    def _parse_folddisco_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse Folddisco output into a list of dictionaries (one per line/match or structure).

        Args:
            output (str): Raw Folddisco output text.

        Returns:
            List[Dict[str, Any]]: Parsed rows.
        """
        lines = output.strip().split('\n')
        results = []
        if not lines:
            return results

        # Skip header if present
        if lines[0].startswith('id\t'):
            lines = lines[1:]

        for line in lines:
            if not line.strip():
                continue
            fields = line.split('\t')
            if len(fields) < 7:  # Minimum for per-match
                continue
            row = {
                "id": fields[0],
                "node_count": int(fields[1]) if fields[1].isdigit() else fields[1],
                "idf_score": float(fields[2]),
                "rmsd": float(fields[3]),
                "matching_residues": fields[4],
                "key": int(fields[5]),
                "query_residues": fields[6]
            }
            # Add extra fields for per-structure if present
            if len(fields) > 7:
                row.update({
                    "total_match_count": int(fields[7]),
                    "edge_count": int(fields[8]),
                    "max_node_cov": float(fields[9]),
                    "min_rmsd": float(fields[10]),
                    "nres": int(fields[11]),
                    "plddt": float(fields[12]) if len(fields) > 12 else None,
                    # matching_residues and key/query_residues shift; adjust accordingly
                })
            results.append(row)
        return results

    @classmethod
    def create_index(cls, pdb_folder: str, index_path: str, threads: int = 4,
                     distance_bins: int = 16, angle_bins: int = 4,
                     big_mode: bool = False, verbose: bool = False,
                     feature_type: str = "default", **kwargs: Any) -> None:
        """
        Create a Folddisco index from a folder of PDB files.

        Args:
            pdb_folder (str): Path to folder containing PDB/mmCIF files.
            index_path (str): Path to the output index directory.
            threads (int): Number of threads (default: 4).
            distance_bins (int): Distance bins in Å (default: 16).
            angle_bins (int): Angle bins in degrees (default: 4).
            big_mode (bool): Enable big mode for >65k structures (default: False).
            verbose (bool): Verbose output (default: False).
            feature_type (str): Feature type: 'default', 'pdb', or 'tr' (default: 'default').
            **kwargs: Additional Folddisco index parameters.
        """
        pdb_folder_path = Path(pdb_folder)
        if not pdb_folder_path.is_dir():
            raise ValueError(f"{pdb_folder} is not a valid directory.")

        if not any(pdb_folder_path.glob("*.pdb")) and not any(pdb_folder_path.glob("*.cif")):
            logger.warning(f"No PDB or mmCIF files found in {pdb_folder}.")

        cmd = [
            "folddisco", "index",
            f"-p {shlex.quote(str(pdb_folder_path))}",
            f"-i {shlex.quote(index_path)}",
            f"-t {threads}",
            f"-d {distance_bins}",
            f"-a {angle_bins}"
        ]

        if big_mode:
            cmd.append("-m big")
        if verbose:
            cmd.append("-v")
        cmd.append(f"--type {feature_type}")

        # Add **kwargs
        for key, value in kwargs.items():
            flag = f"--{key.replace('_', '-')}"
            cmd.extend([flag, str(value)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Folddisco index created at {index_path}")
            if verbose:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Folddisco index failed: {e.stderr}")
            raise


# Example usage
if __name__ == "__main__":
    # Example: Create index from folder
    FolddiscoAnalyzer.create_index(
        pdb_folder="data/serine_peptidases",
        index_path="index/serine_peptidases_folddisco",
        threads=12,
        big_mode=False
    )

    # Example: Analyze a single PDB
    analyzer = FolddiscoAnalyzer(
        pdb_file="query/4CHA.pdb",
        chain_id="B",  # But uses full PDB; residues specify
        residue_range=(57, 195)  # Example range, but for motif use specific in query
    )
    # For specific residues like B57,B102,C195, set residue_range=None and pass residues manually if needed
    # But since init takes range, for motifs, extract full and specify -q
    results = analyzer.run_query(
        index_path="index/serine_peptidases_folddisco",
        distance_threshold=0.5,
        angle_threshold=5,
        threads=6,
        skip_match=False,
        top=10,
        per_structure=True,
        sampling_ratio=1.0  # Example kwarg
    )
    print(results["parsed_results"])