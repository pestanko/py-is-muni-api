import pytest

import is_api
import is_api.log_config

is_api.log_config.load_config()


@pytest.fixture()
def stub_params() -> dict:
    return dict(domain='localhost', token='secret_token',
                course_code='PB071', faculty_id=101)


@pytest.fixture()
def is_stub(stub_params) -> is_api.IsApiClient:
    return is_api.IsApiClient(**stub_params)
