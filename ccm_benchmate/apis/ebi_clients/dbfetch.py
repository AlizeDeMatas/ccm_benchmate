
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.request import __version__ as urllib_version


from ccm_demo.apis.ebi_clients.utils import *

logger = logging.getLogger(__name__)

class DbfetchError(Exception):
    """Custom exception for Dbfetch client errors."""
    pass

class DbfetchClient:
    """Client for EBI Dbfetch service."""
    def __init__(self, base_url: str = 'https://www.ebi.ac.uk/Tools/dbfetch/dbfetch', debug_level: int = 0, output_level: int = 1):
        """Initialize Dbfetch client."""
        self.base_url = base_url.rstrip('/')
        self.debug_level = debug_level
        self.output_level = output_level
        self.version = '2022-09-13 12:15'
        self.user_agent = self._get_user_agent()

    def _get_user_agent(self) -> str:
        """Generate user agent string."""
        urllib_agent = f'Python-urllib/{urllib_version}'
        try:
            python_version = platform.python_version()
            python_sys = platform.system()
        except ValueError:
            python_version, python_sys = "Unknown", "Unknown"
        LIM = 256
        return f'EBI-Sample-Client/{self.version} (dbfetch.py; Python {python_version}; {python_sys}) {urllib_agent}'[:LIM]

    def _rest_request(self, url: str) -> bytes:
        """Perform a REST request."""
        try:
            http_headers = {'User-Agent': self.user_agent}
            req = Request(url, None, http_headers)
            with urlopen(req) as response:
                return response.read()
        except HTTPError as ex:
            logger.error(f'HTTP Error: {str(ex)}')
            raise DbfetchError(f'Failed to fetch {url}: {str(ex)}')

    def get_supported_dbs(self) -> List[str]:
        """List available databases."""
        content = self._rest_request(f'{self.base_url}/getSupportedDBs').decode('utf-8')
        return [db.strip() for db in content.split('\n') if db.strip()]

    def get_supported_formats(self) -> List[Dict[str, str]]:
        """List available databases with formats."""
        content = self._rest_request(f'{self.base_url}/getSupportedFormats').decode('utf-8')
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return [{'db': line.strip(), 'format': ''} for line in content.split('\n') if line.strip()]

    def get_supported_styles(self) -> List[Dict[str, str]]:
        """List available databases with styles."""
        content = self._rest_request(f'{self.base_url}/getSupportedStyles').decode('utf-8')
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return [{'db': line.strip(), 'style': ''} for line in content.split('\n') if line.strip()]

    def get_db_formats(self, db_name: str) -> List[str]:
        """List formats for a specified database."""
        content = self._rest_request(f'{self.base_url}/getDbFormats/{db_name}').decode('utf-8')
        return [fmt.strip() for fmt in content.split('\n') if fmt.strip()]

    def get_format_styles(self, db_name: str, db_format: str) -> List[str]:
        """List styles for a specified database and format."""
        content = self._rest_request(f'{self.base_url}/getFormatStyles/{db_name}/{db_format}').decode('utf-8')
        return [style.strip() for style in content.split('\n') if style.strip()]

    def fetch_data(self, db_name_id: str, format: Optional[str] = None, style: Optional[str] = None) -> bytes:
        """Retrieve a database entry."""
        url = f'{self.base_url}/fetchData/{db_name_id}'
        if format:
            url += f'/{format}'
            if style:
                url += f'/{style}'
        return self._rest_request(url)

    def fetch_batch(self, db_name: str, id_list: str, format: Optional[str] = None, style: Optional[str] = None) -> bytes:
        """Retrieve multiple database entries."""
        url = f'{self.base_url}/fetchBatch/{db_name}/{id_list}'
        if format:
            url += f'/{format}'
            if style:
                url += f'/{style}'
        return self._rest_request(url)