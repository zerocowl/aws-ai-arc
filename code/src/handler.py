import json
import time
from database import get_history, save_interaction
from ai_client import invoke_model
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    path = event.get('path', '')
    http_method = event.get('httpMethod', '')
    path_parameters = event.get('pathParameters', {}) or {}
    session_id = path_parameters.get('sessionId')

    if not session_id:
        return _build_response(400, {"error": "sessionId is required"})

    try:
        if http_method == 'POST' and path.endswith(session_id):
            return handle_post_chat(event, session_id)
        elif http_method == 'GET' and path.endswith('history'):
            return handle_get_history(event, session_id)
        else:
            return _build_response(404, {"error": "Not Found"})
    except Exception as e:
        logger.error(f"Internal Error: {e}")
        return _build_response(500, {"error": "Internal Server Error"})


def handle_post_chat(event, session_id):
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return _build_response(400, {"error": "Invalid JSON body"})

    user_message = body.get('message')
    if not user_message:
        return _build_response(400, {"error": "message field is required in body"})

    try:
        # 1. Recuperar histórico
        history = get_history(session_id, limit=10)
        
        # 2. Invocação do Bedrock
        assistant_message, input_tokens, output_tokens = invoke_model(history, user_message)
        
        # 3. Persistência
        save_interaction(session_id, user_message, assistant_message, input_tokens, output_tokens)
        
        # 4. Resposta
        return _build_response(200, {
            "sessionId": session_id,
            "message": assistant_message,
            "role": "assistant",
            "timestamp": int(time.time()),
            "inputTokens": input_tokens,
            "outputTokens": output_tokens
        })
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        error_msg = str(e)
        if any(err in error_msg for err in ["ThrottlingException", "ModelNotReadyException", "ServiceUnavailableException"]):
             return _build_response(503, {"error": "Service Temporarily Unavailable - Throttling or Bedrock Unavailable"})
        return _build_response(500, {"error": "Error processing your request"})

def handle_get_history(event, session_id):
    query_params = event.get('queryStringParameters') or {}
    limit_str = query_params.get('limit', '10')
    
    try:
        limit = int(limit_str)
        limit = min(max(1, limit), 50) # Range de 1 até no max 50
    except ValueError:
        return _build_response(400, {"error": "limit query parameter must be an integer"})
        
    history = get_history(session_id, limit=limit)
    
    # Remover campos internos das respostas antes de enviar (ttl, etc)
    clean_history = []
    for item in history:
        clean_history.append({
            "role": item.get("role"),
            "message": item.get("message"),
            "timestamp": item.get("timestamp")
        })
        
    return _build_response(200, {
        "sessionId": session_id,
        "history": clean_history
    })

def _build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }
