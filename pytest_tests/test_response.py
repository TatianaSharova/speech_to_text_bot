from http import HTTPStatus

import requests


def test_openai_api_availability(openai_endpoint, openai_request_headers):
    '''Проверка доступа к API OpenAI.'''
    params = {
        'url': openai_endpoint,
        'headers': openai_request_headers
    }
    response = requests.get(**params)
    assert response.status_code == HTTPStatus.OK
