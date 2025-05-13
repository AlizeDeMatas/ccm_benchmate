import logging
import os
import sys
import time
import platform
import re
import requests
from urllib.parse import urlparse
from urllib.request import __version__ as urllib_version
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class EBIClientError(Exception):
    """Custom exception for EBI client errors."""
    pass

def setup_session(max_retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    """Create a requests session with retry logic."""
    session = requests.Session()
    retries = Retry(total=max_retries, backoff_factor=backoff_factor, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def printDebugMessage(functionName: str, message: str, level: int, debugLevel: int = 0) -> None:
    """Log debug message if debug level is sufficient."""
    if level <= debugLevel:
        logger.debug(f'[{functionName}] {message}')

def getUserAgent(clientRevision: str) -> str:
    """Generate user agent string for HTTP requests."""
    printDebugMessage('getUserAgent', 'Begin', 11)
    urllib_agent = f'Python-urllib/{urllib_version}'
    try:
        python_version = platform.python_version()
        python_sys = platform.system()
    except ValueError:
        python_version, python_sys = "Unknown", "Unknown"
    user_agent = f'EBI-Sample-Client/{clientRevision} ({os.path.basename(__file__)}; Python {python_version}; {python_sys}) {urllib_agent}'
    printDebugMessage('getUserAgent', f'user_agent: {user_agent}', 12)
    printDebugMessage('getUserAgent', 'End', 11)
    return user_agent

def restRequest(url: str, user_agent: str, session: Optional[requests.Session] = None) -> bytes:
    """Perform a REST (HTTP GET) request with retries."""
    printDebugMessage('restRequest', f'url: {url}', 11)
    try:
        session = session or setup_session()
        http_headers = {'User-Agent': user_agent}
        response = session.get(url, headers=http_headers)
        response.raise_for_status()
        content = response.content
    except requests.exceptions.RequestException as ex:
        logger.error(f'HTTP Error: {str(ex)}')
        raise EBIClientError(f'Failed to fetch {url}: {str(ex)}')
    printDebugMessage('restRequest', 'End', 11)
    return content

def getIdFromLocation(location: str) -> str:
    """Extract job ID from HTTP Location header."""
    printDebugMessage('getIdFromLocation', f'location: {location}', 11)
    try:
        jobId = os.path.basename(urlparse(location).path)
        printDebugMessage('getIdFromLocation', f'jobId: {jobId}', 11)
        return jobId
    except Exception as ex:
        logger.error(f'Invalid location header: {location}')
        raise EBIClientError(f'Cannot extract job ID from {location}: {str(ex)}')

def readFile(fileName: str) -> str:
    """Read content from a file."""
    printDebugMessage('readFile', f'Reading {fileName}', 11)
    try:
        content = Path(fileName).read_text(encoding='utf-8')
        printDebugMessage('readFile', 'End', 11)
        return content
    except IOError as ex:
        logger.error(f'Cannot read file {fileName}: {str(ex)}')
        raise EBIClientError(f'Failed to read file {fileName}: {str(ex)}')

def clientPoll(jobId: str, baseUrl: str, user_agent: str, session: Optional[requests.Session] = None) -> str:
    """Poll job status until completion."""
    printDebugMessage('clientPoll', f'jobId: {jobId}', 1)
    status = 'PENDING'
    while status in ('RUNNING', 'PENDING'):
        status = serviceGetStatus(jobId, baseUrl, user_agent, session)
        printDebugMessage('clientPoll', f'status: {status}', 2)
        if status in ('RUNNING', 'PENDING'):
            time.sleep(3)
    return status

def serviceRun(email: str, title: Optional[str], params: Dict[str, Any], baseUrl: str, user_agent: str, async_job: bool = False, session: Optional[requests.Session] = None) -> Union[str, bytes]:
    """Submit a job to the service."""
    printDebugMessage('serviceRun', 'Begin', 1)
    if not checkEmailFormat(email):
        logger.error('Invalid email address')
        raise EBIClientError('Invalid email address')
    requestUrl = f'{baseUrl}/run'
    params = params.copy()
    params['email'] = email
    if title:
        params['title'] = title
    try:
        session = session or setup_session()
        response = session.post(requestUrl, data=params, headers={'User-Agent': user_agent})
        response.raise_for_status()
        if async_job:
            jobId = getIdFromLocation(response.headers.get('Location', ''))
            print(jobId)
            return jobId
        return response.content
    except requests.exceptions.RequestException as ex:
        logger.error(f'HTTP Error: {str(ex)}')
        raise EBIClientError(f'Failed to submit job to {requestUrl}: {str(ex)}')

def serviceGetStatus(jobId: str, baseUrl: str, user_agent: str, session: Optional[requests.Session] = None) -> str:
    """Get the status of a job."""
    printDebugMessage('serviceGetStatus', f'jobId: {jobId}', 1)
    requestUrl = f'{baseUrl}/status/{jobId}'
    content = restRequest(requestUrl, user_agent, session)
    return content.decode('utf-8')

def serviceGetResult(jobId: str, resultType: str, baseUrl: str, user_agent: str, session: Optional[requests.Session] = None) -> bytes:
    """Retrieve a job result."""
    printDebugMessage('serviceGetResult', f'jobId: {jobId}, resultType: {resultType}', 1)
    requestUrl = f'{baseUrl}/result/{jobId}/{resultType}'
    return restRequest(requestUrl, user_agent, session)

def serviceGetResultTypes(jobId: str, baseUrl: str, user_agent: str, session: Optional[requests.Session] = None) -> List[Dict[str, str]]:
    """Get available result types for a job."""
    printDebugMessage('serviceGetResultTypes', f'jobId: {jobId}', 1)
    requestUrl = f'{baseUrl}/resulttypes/{jobId}'
    content = restRequest(requestUrl, user_agent, session)
    return parse_result_types(content)

def storeFile(fileName: str, content: bytes) -> None:
    """Store content to a file."""
    printDebugMessage('storeFile', f'Writing {fileName}', 1)
    try:
        Path(fileName).write_bytes(content)
    except IOError as ex:
        logger.error(f'Cannot write file {fileName}: {str(ex)}')
        raise EBIClientError(f'Failed to write file {fileName}: {str(ex)}')

def checkEmailFormat(email: str) -> bool:
    """Validate email address format."""
    emailPattern = r'^[^@]+@[^@]+$'
    return bool(re.match(emailPattern, email))

def parse_result_types(xml_content: bytes) -> List[Dict[str, str]]:
    """Parse XML result types using xmltramp2."""
    try:
        import xmltramp2
        xml_doc = xmltramp2.parse(xml_content.decode('utf-8'))
        result_types = []
        for rt in xml_doc['resultType']:
            result_types.append({
                'identifier': str(rt.identifier),
                'label': str(rt.label) if hasattr(rt, 'label') else '',
                'description': str(rt.description) if hasattr(rt, 'description') else '',
                'mediaType': str(rt.mediaType) if hasattr(rt, 'mediaType') else ''
            })
        return result_types
    except ImportError:
        logger.warning('xmltramp2 not installed; falling back to simple parsing')
        return [{'identifier': rt} for rt in xml_content.decode('utf-8').split()]
    except Exception as ex:
        logger.error(f'Failed to parse result types: {str(ex)}')
        raise EBIClientError(f'Failed to parse result types: {str(ex)}')