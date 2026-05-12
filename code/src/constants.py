import os

SYSTEM_PROMPT = """Você é o Assistente Financeiro da FinTrack.
Seu objetivo é ajudar o usuário com insights financeiros de forma clara e objetiva."""

MODEL_ID = os.getenv("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
TABLE_NAME = os.getenv("TABLE_NAME", "fintrack-chat-history")
