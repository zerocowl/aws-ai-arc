import os
import time
import boto3
from boto3.dynamodb.conditions import Key
from constants import TABLE_NAME

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def get_history(session_id: str, limit: int = 10):
    try:
        response = table.query(
            KeyConditionExpression=Key('sessionId').eq(session_id),
            ScanIndexForward=False, # Obtém os mais recentes primeiro
            Limit=limit
        )
        items = response.get('Items', [])
        # Retorna ordenado do mais antigo pro mais recente
        return sorted(items, key=lambda x: x['timestamp'])
    except Exception as e:
        print(f"Error getting history: {e}")
        return []

def save_interaction(session_id: str, user_message: str, assistant_message: str, input_tokens: int, output_tokens: int):
    try:
        current_time = int(time.time())
        ttl = current_time + (24 * 60 * 60) # + 24 horas
        
        # Salva a mensagem do usuário
        table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': str(current_time),
                'role': 'user',
                'message': user_message,
                'ttl': ttl
            }
        )
        
        # Salva a resposta do assistente (adiciona +1 para ordenar na frente do usuário em ms)
        table.put_item(
            Item={
                'sessionId': session_id,
                'timestamp': str(current_time + 1),
                'role': 'assistant',
                'message': assistant_message,
                'inputTokens': input_tokens,
                'outputTokens': output_tokens,
                'ttl': ttl
            }
        )
    except Exception as e:
        print(f"Error saving interaction: {e}")
        raise e
