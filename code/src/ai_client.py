import boto3
import json
import logging
from botocore.config import Config
from botocore.exceptions import ClientError
from constants import MODEL_ID, SYSTEM_PROMPT

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração de Retry com Backoff Exponencial nativo do botocore
retry_config = Config(
    retries = {
        'max_attempts': 5,
        'mode': 'standard'
    }
)

bedrock_client = boto3.client('bedrock-runtime', config=retry_config)

def invoke_model(history: list, user_message: str):
    messages = []
    for item in history:
        messages.append({
            "role": item.get('role', 'user'),
            "content": [{"type": "text", "text": item.get('message', '')}]
        })
    
    messages.append({
        "role": "user",
        "content": [{"type": "text", "text": user_message}]
    })

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": messages
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )
        response_body = json.loads(response.get('body').read())
        
        assistant_message = response_body.get('content', [{}])[0].get('text', '')
        usage = response_body.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        return assistant_message, input_tokens, output_tokens
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Bedrock API Error: {error_code} - {e}")
        # Lançar exceção para ser tratada no handler (e converter em 503 HTTP)
        raise e
