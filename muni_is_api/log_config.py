"""
Logging configuration module
"""
import logging
import tempfile
from logging.config import dictConfig
from pathlib import Path


class Logging:
    def __init__(self, config):
        self._config = config

    @property
    def global_log_level(self):
        if not self._config:
            return 'DEBUG'
        return self._config.get('log_level_global', 'DEBUG')

    @property
    def file_log_level(self):
        if not self._config:
            return 'INFO'
        return self._config.get('log_level_file', self.global_log_level)

    @property
    def console_log_level(self):
        if not self._config:
            return 'DEBUG'
        return self._config.get('log_level_console', self.global_log_level)

    @property
    def handlers(self):
        return {
            'console': self.get_handler_console(),
            'results_file': self.get_logger_file('results'),
        }

    @property
    def formatters(self):
        return {
            'verbose': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
            'simple': {'format': '%(levelname)s %(message)s'},
            'colored_console': {
                '()': 'coloredlogs.ColoredFormatter',
                'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                'datefmt': '%H:%M:%S'
            },
        }

    @property
    def loggers(self) -> dict:
        return {
            'muni_is_api': {
                'handlers': ['console', 'results_file'],
                'level': self.global_log_level, 'propagate': True
            },
            'tests': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
        }

    @property
    def logger_config(self):
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': self.formatters,
            'handlers': self.handlers,
            'loggers': self.loggers,
        }

    @property
    def results_dir(self) -> Path:
        results = self._config.paths.results if self._config else tempfile.gettempdir()
        return Path(results)

    def get_logger_file(self, name, level: str = None):
        level = level or self.file_log_level
        results_dir = self.results_dir
        if not results_dir.exists():
            results_dir.mkdir(parents=True)
        return {
            'level': level,
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': str(self.results_dir / f'{name}.log'),
            'maxBytes': 5000000,  # 5MB
            'backupCount': 5
        }

    def get_handler_console(self, level: str = None):
        level = level or self.console_log_level
        return {
            'level': level, 'class': 'logging.StreamHandler', 'formatter': 'colored_console'
        }

    def load_config(self):
        """Loads config based on the config type
        Args:
        """
        add_custom_log_level()
        dictConfig(self.logger_config)


TRACE_LOG_LVL = 9


def _trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LOG_LVL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(TRACE_LOG_LVL, message, args, **kws)


def add_custom_log_level():
    logging.addLevelName(TRACE_LOG_LVL, 'TRACE')
    logging.Logger.trace = _trace


def load_config(config=None):
    return Logging(config=config).load_config()
