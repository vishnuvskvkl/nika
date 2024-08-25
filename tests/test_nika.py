import pytest
from nika import Nika

@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("openai.ChatCompletion.create")

def test_generate_response(mock_openai):
    agent = Nika(api_key="fake-api-key")
    mock_openai.return_value = {
        'choices': [{'message': {'content': "Hello, World!"}}]
    }
    response = agent.generate_response("Hello?")
    assert response == "Hello, World!"


