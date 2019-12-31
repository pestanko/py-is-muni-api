import is_api.log_config
from .client import IsApiClient         # noqa: F401
from .files_api import FilesApiClient   # noqa: F401

__version__ = '0.2'

is_api.log_config.load_config()
