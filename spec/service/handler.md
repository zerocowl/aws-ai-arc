# Especificação Técnica: Lambda Al Insights Chat

Este documento descreve a lógica de negócio, os requisitos de runtime e a estrutura de código para o microserviço de assistência financeira. 

## 1. Definições de Ambiente

* 
**Runtime:** Python 3.14. 


* 
**SDK:** `boto3` (atualizado para suporte ao Amazon Bedrock). 


* 
**Variáveis de Ambiente:** 


* `TABLE_NAME`: Nome da tabela DynamoDB para persistência do histórico.
* `MODEL_ID`: `claude-haiku-4-5-20251001`.


* **Timeout Recomendado:** 29 segundos (limite do API Gateway).
* **Memória:** 128MB a 256MB (ajustar conforme consumo do SDK).

## 2. Fluxo de Execução (Handler)

O ponto de entrada deve seguir rigorosamente esta sequência: 

1. **Validação:** Extrair `sessionId` do path e `message` do body. Validar se o JSON é válido. 


2. **Recuperação de Histórico:** Consultar o DynamoDB usando o `sessionId`. Recuperar as últimas $N$ mensagens (ordenadas por timestamp). 


3. 
**Construção do Prompt:** 


* **System Prompt:** Definido internamente no código, instruindo o modelo a agir como o "Assistente Financeiro da FinTrack".
* **Contexto:** Concatenar o System Prompt + Histórico (User/Assistant) + Nova mensagem do usuário.


4. 
**Invocação do Bedrock:** Chamar `bedrock-runtime.invoke_model()` com o `MODEL_ID` e o payload formatado para as mensagens do Claude. 


5. 
**Persistência:** Gravar no DynamoDB a mensagem enviada pelo usuário e a resposta gerada pelo assistente. 


* 
**Atributo TTL:** Adicionar um campo `ttl` com o valor de `current_time + 24h` em formato Epoch (Integer). 




6. 
**Resposta:** Retornar status 200 com o JSON contendo `sessionId`, `message`, `role`, `timestamp` e os metadados de tokens (`inputTokens`, `outputTokens`). 



## 3. Resiliência e Tratamento de Erros

A implementação deve incluir lógica de **Backoff Exponencial** para os seguintes erros do Bedrock: 

* `ThrottlingException`
* `ModelNotReadyException`
* `ServiceUnavailableException`

Erros de validação (`ValidationException`) ou erros internos devem retornar uma estrutura JSON padronizada com o código HTTP apropriado. 

## 4. Estrutura de Código Sugerida

Para garantir a testabilidade e modularidade (conforme critério E1), o código deve ser organizado assim: 

```text
src/
├── handler.py           # Entrada da Lambda e orquestração do fluxo
├── database.py          # Módulo de interface com DynamoDB (Get/Put)
├── ai_client.py         # Módulo de interface com Amazon Bedrock
├── constants.py         # System Prompt e configurações fixas
└── requirements.txt     # Dependências (boto3, etc.)

```

## 5. Requisitos de Testes Unitários

A suíte de testes (Pytest) deve cobrir obrigatoriamente: 

* 
**Mocking:** Utilizar `moto` ou `pytest-mock` para simular chamadas ao DynamoDB e Bedrock. 


* **Cenários:**
* Sucesso em uma sessão nova (histórico vazio). 


* Sucesso em sessão existente (histórico presente no prompt). 


* Falha ao atingir o limite de throttling do Bedrock após retentativas. 




* 
**Cobertura:** Mínimo de 70%. 

