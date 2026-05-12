# Guia de Implementação de Infraestrutura: FinTrack AI Insights

Este documento detalha os requisitos técnicos para a criação da infraestrutura serverless na AWS utilizando **Terraform**. O objetivo é suportar o microserviço de IA Generativa da FinTrack.

## 1. Requisitos de Configuração Global

* **Provider:** AWS.
* **Versão do Terraform:** >= 1.0.
* 
**Região:** `us-east-1` (Recomendado para acesso ao Amazon Bedrock).


* 
**Arquivos Obrigatórios:** `api_gateway.tf`, `lambda.tf`, `dynamodb.tf`, `iam.tf`, `outputs.tf`, `variables.tf`.



## 2. Definição dos Recursos (Terraform)

### A. Banco de Dados (DynamoDB)

Crie uma tabela para persistência do histórico de chat:

* **Nome:** Definido via variável (ex: `fintrack-chat-history`).
* 
**Chave de Partição (Hash Key):** `sessionId` (String).


* 
**Chave de Classificação (Range Key):** `timestamp` (String).


* 
**TTL (Time to Live):** Ativar no atributo `ttl` (24 horas de retenção).



### B. Orquestração (AWS Lambda)

Configure a função que processará a lógica de negócio:

* 
**Runtime:** Python 3.14.


* 
**Handler:** `handler.lambda_handler` (ou conforme estrutura de pastas).


* **Variáveis de Ambiente:**
* 
`TABLE_NAME`: Nome da tabela DynamoDB criada.


* 
`MODEL_ID`: Valor fixo `claude-haiku-4-5-20251001`.




* 
**Observabilidade:** Habilitar suporte a logs no CloudWatch e rastreamento ativo com AWS X-Ray.



### C. Segurança e Permissões (IAM)

A Lambda deve possuir uma Role com as seguintes permissões mínimas:

1. 
**DynamoDB:** `PutItem`, `Query` e `GetItem` na tabela específica.


2. 
**Amazon Bedrock:** `bedrock:InvokeModel` para o modelo Claude Haiku.


3. 
**Logs:** Permissões básicas para criar grupos de logs e enviar eventos ao CloudWatch.



### D. Ponto de Entrada (Amazon API Gateway)

Configurar uma API REST com os seguintes recursos:

1. **Endpoint POST `/chat/{sessionId}`:**
* Integração do tipo Lambda Proxy.
* Validação de body JSON obrigatória (campo `message`).




2. **Endpoint GET `/chat/{sessionId}/history`:**
* Integração do tipo Lambda Proxy.
* Suporte a Query Parameter `limit` (default 10, max 50).





## 3. Variáveis e Outputs

### Variáveis (`variables.tf`)

* `aws_region`: Região para o deploy.
* `environment`: Nome do ambiente (ex: `sandbox`, `prod`).
* `project_name`: `fintrack-ai-insights`.

### Outputs (`outputs.tf`)

* 
`api_endpoint`: A URL base do API Gateway para testes no Postman.


* `lambda_function_arn`: ARN da função Lambda criada.

---

## 4. Instruções de Execução para o Modelo de LLM

Ao gerar o código, certifique-se de:

1. 
**Modularidade:** Organize os recursos em arquivos separados conforme listado acima.


2. 
**Boas Práticas:** Use `terraform.tfvars.example` para mascarar valores sensíveis.


3. 
**Tratamento de Erros:** O modelo deve considerar a política de retry e backoff para chamadas do Bedrock nas configurações de integração, se aplicável.