import openai
import pytest

URL = 'https://api.openai.com/v1/models'

HEADERS = {'Authorization': f'Bearer {openai.api_key}'}


@pytest.fixture
def openai_endpoint():
    return URL


@pytest.fixture
def openai_request_headers():
    return HEADERS
