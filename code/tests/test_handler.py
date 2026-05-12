import json
import pytest
from unittest.mock import patch
import sys
import os

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import handler

@pytest.fixture
def mock_event_post():
    return {
        "httpMethod": "POST",
        "path": "/chat/123",
        "pathParameters": {"sessionId": "123"},
        "body": json.dumps({"message": "Hello"})
    }

@pytest.fixture
def mock_event_get():
    return {
        "httpMethod": "GET",
        "path": "/chat/123/history",
        "pathParameters": {"sessionId": "123"},
        "queryStringParameters": {"limit": "5"}
    }

@patch('handler.get_history')
@patch('handler.invoke_model')
@patch('handler.save_interaction')
def test_handle_post_chat_success_new_session(mock_save, mock_invoke, mock_get_history, mock_event_post):
    mock_get_history.return_value = []
    mock_invoke.return_value = ("Hi there!", 10, 20)
    
    response = handler.lambda_handler(mock_event_post, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == "Hi there!"
    assert body['sessionId'] == "123"
    mock_get_history.assert_called_once_with("123", limit=10)
    mock_invoke.assert_called_once_with([], "Hello")
    mock_save.assert_called_once_with("123", "Hello", "Hi there!", 10, 20)

@patch('handler.get_history')
@patch('handler.invoke_model')
@patch('handler.save_interaction')
def test_handle_post_chat_success_existing_session(mock_save, mock_invoke, mock_get_history, mock_event_post):
    mock_get_history.return_value = [{"role": "user", "message": "previous"}]
    mock_invoke.return_value = ("Hi there!", 10, 20)
    
    response = handler.lambda_handler(mock_event_post, None)
    
    assert response['statusCode'] == 200
    mock_invoke.assert_called_once_with([{"role": "user", "message": "previous"}], "Hello")

@patch('handler.get_history')
@patch('handler.invoke_model')
def test_handle_post_chat_throttling_error(mock_invoke, mock_get_history, mock_event_post):
    mock_get_history.return_value = []
    mock_invoke.side_effect = Exception("ThrottlingException")
    
    response = handler.lambda_handler(mock_event_post, None)
    
    assert response['statusCode'] == 503

@patch('handler.get_history')
def test_handle_get_history_success(mock_get_history, mock_event_get):
    mock_get_history.return_value = [{"role": "user", "message": "test", "timestamp": "123"}]
    
    response = handler.lambda_handler(mock_event_get, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['history']) == 1
    mock_get_history.assert_called_once_with("123", limit=5)
