#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ccm_demo.apis.ebi_clients.utils import *

logger = logging.getLogger(__name__)

class EBIClient:
    """Base class for EBI Job Dispatcher web service clients."""
    def __init__(self, service_name: str, base_url: str, debug_level: int = 0, output_level: int = 1):
        """Initialize client with service details."""
        self.service_name = service_name
        self.base_url = base_url.rstrip('/')
        self.debug_level = debug_level
        self.output_level = output_level
        self.version = '2024-03-20 12:04'
        self.user_agent = getUserAgent(self.version)
        self.session = setup_session()

    def run_job(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run a job with the specified parameters."""
        printDebugMessage('run_job', f'Submitting job for {self.service_name}', 1, self.debug_level)
        return serviceRun(email, title, params | {'sequence': sequence}, self.base_url, self.user_agent, async_job, self.session)

    def get_status(self, job_id: str) -> str:
        """Check the status of a job."""
        printDebugMessage('get_status', f'Checking status for job {job_id}', 1, self.debug_level)
        return serviceGetStatus(job_id, self.base_url, self.user_agent, self.session)

    def get_result(self, job_id: str, result_type: str) -> bytes:
        """Retrieve a job result."""
        printDebugMessage('get_result', f'Retrieving result {result_type} for job {job_id}', 1, self.debug_level)
        return serviceGetResult(job_id, result_type, self.base_url, self.user_agent, self.session)

    def get_result_types(self, job_id: str) -> List[Dict[str, str]]:
        """Get available result types for a job."""
        printDebugMessage('get_result_types', f'Fetching result types for job {job_id}', 1, self.debug_level)
        return serviceGetResultTypes(job_id, self.base_url, self.user_agent, self.session)

    def poll_job(self, job_id: str) -> str:
        """Poll a job until completion."""
        printDebugMessage('poll_job', f'Polling job {job_id}', 1, self.debug_level)
        return clientPoll(job_id, self.base_url, self.user_agent, self.session)

    def save_result(self, job_id: str, result_type: str, outfile: Optional[str] = None) -> None:
        """Save a job result to a file or stdout."""
        printDebugMessage('save_result', f'Saving result {result_type} for job {job_id}', 1, self.debug_level)
        content = self.get_result(job_id, result_type)
        if outfile:
            storeFile(outfile, content)
        else:
            sys.stdout.buffer.write(content)

    def __del__(self):
        """Clean up session."""
        if hasattr(self, 'session'):
            self.session.close()

class ClustalOmega(EBIClient):
    """Client for Clustal Omega multiple sequence alignment."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('Clustal Omega', 'https://www.ebi.ac.uk/Tools/services/rest/clustalo', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run Clustal Omega alignment."""
        return self.run_job(email, sequence, async_job, title, **params)

class Disembl(EBIClient):
    """Client for DisEMBL protein disorder prediction."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('DisEMBL', 'https://www.ebi.ac.uk/Tools/services/rest/disembl', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run DisEMBL analysis."""
        return self.run_job(email, sequence, async_job, title, **params)

class EMBOSSBacktranseq(EBIClient):
    """Client for EMBOSS backtranseq nucleotide to protein translation."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('EMBOSS backtranseq', 'https://www.ebi.ac.uk/Tools/services/rest/emboss_backtranseq', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run EMBOSS backtranseq translation."""
        return self.run_job(email, sequence, async_job, title, **params)

class EMBOSSPepinfo(EBIClient):
    """Client for EMBOSS pepinfo protein property analysis."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('EMBOSS pepinfo', 'https://www.ebi.ac.uk/Tools/services/rest/emboss_pepinfo', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run EMBOSS pepinfo analysis."""
        return self.run_job(email, sequence, async_job, title, **params)

class EMBOSSTranseq(EBIClient):
    """Client for EMBOSS transeq nucleotide to protein translation."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('EMBOSS transeq', 'https://www.ebi.ac.uk/Tools/services/rest/emboss_transeq', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run EMBOSS transeq translation."""
        return self.run_job(email, sequence, async_job, title, **params)

class InterProScan5(EBIClient):
    """Client for InterProScan 5 protein function analysis."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('InterProScan 5', 'https://www.ebi.ac.uk/Tools/services/rest/iprscan5', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run InterProScan 5 analysis."""
        return self.run_job(email, sequence, async_job, title, **params)

class Lalign(EBIClient):
    """Client for Lalign local sequence alignment."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('Lalign', 'https://www.ebi.ac.uk/Tools/services/rest/lalign', debug_level, output_level)

    def run(self, email: str, sequence: str, sequence_b: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run Lalign alignment."""
        return self.run_job(email, sequence, async_job, title, sequence_b=sequence_b, **params)

class Mafft(EBIClient):
    """Client for MAFFT multiple sequence alignment."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('MAFFT', 'https://www.ebi.ac.uk/Tools/services/rest/mafft', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run MAFFT alignment."""
        return self.run_job(email, sequence, async_job, title, **params)

class Muscle(EBIClient):
    """Client for MUSCLE multiple sequence alignment."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('MUSCLE', 'https://www.ebi.ac.uk/Tools/services/rest/muscle', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run MUSCLE alignment."""
        return self.run_job(email, sequence, async_job, title, **params)

class NCBIBlast(EBIClient):
    """Client for NCBI BLAST sequence similarity search."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('NCBI BLAST', 'https://www.ebi.ac.uk/Tools/services/rest/ncbiblast', debug_level, output_level)

    def run(self, email: str, sequence: str, program: str, database: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run NCBI BLAST search."""
        return self.run_job(email, sequence, async_job, title, program=program, database=database, **params)

class Pratt(EBIClient):
    """Client for Pratt pattern discovery."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('Pratt', 'https://www.ebi.ac.uk/Tools/services/rest/pratt', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run Pratt pattern discovery."""
        return self.run_job(email, sequence, async_job, title, **params)

class TCoffee(EBIClient):
    """Client for T-Coffee multiple sequence alignment."""
    def __init__(self, debug_level: int = 0, output_level: int = 1):
        super().__init__('T-Coffee', 'https://www.ebi.ac.uk/Tools/services/rest/tcoffee', debug_level, output_level)

    def run(self, email: str, sequence: str, async_job: bool = False, title: Optional[str] = None, **params) -> Union[str, bytes]:
        """Run T-Coffee alignment."""
        return self.run_job(email, sequence, async_job, title, **params)