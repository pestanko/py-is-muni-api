import is_api.log_config
from .client import IsApiClient
from .files_api import FilesApiClient

__version__ = '0.2'

is_api.log_config.load_config()
