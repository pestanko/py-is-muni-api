import muni_is_api.log_config
from muni_is_api.client import IsApiClient         # noqa: F401
from muni_is_api.files_api import FilesApiClient   # noqa: F401

__version__ = '0.8.0'

muni_is_api.log_config.load_config()
