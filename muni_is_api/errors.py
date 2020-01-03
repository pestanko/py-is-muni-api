class ISApiError(Exception):
    def __init__(self, message, *args, **kwargs):
        super(ISApiError, self).__init__(*args, **kwargs)
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    def what(self) -> str:
        return f"API Error [{self.__class__.__name__}]: {self.message}"

    def __str__(self) -> str:
        return self.what()
