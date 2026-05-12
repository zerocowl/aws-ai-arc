# FinTrack AI Insights

Microsserviço de assistência financeira rodando na AWS (Lambda + API Gateway + DynamoDB + Amazon Bedrock).

## Pré-requisitos

1. **Conta AWS** configurada localmente.
2. **AWS CLI** instalado (`aws configure`).
3. **Terraform** (>= 1.0) instalado.
4. O modelo **Claude 3 Haiku** precisa estar habilitado no **Amazon Bedrock** da sua conta, na região `us-east-1` (Vá no console da AWS: Bedrock > Model access).

## Como Fazer o Deploy

### 1. Configurar e Inicializar

Abra o terminal, navegue até a pasta `terraform` e inicialize:

```bash
cd terraform
terraform init
```

### 2. Verificar o Plano de Execução

Veja o que o Terraform vai criar na sua conta:

```bash
terraform plan
```

### 3. Aplicar e Fazer o Deploy

Esse comando fará o zip do código em `src/` e publicará toda a infraestrutura:

```bash
terraform apply
```
*Digite `yes` para confirmar.*

### 4. Testar a API

No final da execução, o Terraform exibirá a URL do seu API Gateway (procure por `api_endpoint`).

**Enviar uma mensagem:**
```bash
curl -X POST https://<SEU_API_ID>.execute-api.us-east-1.amazonaws.com/prod/chat/sessao-123 \
  -H "Content-Type: application/json" \
  -d '{"message": "Como posso economizar 20% do meu salário?"}'
```

**Ver histórico de conversas:**
```bash
curl -X GET "https://<SEU_API_ID>.execute-api.us-east-1.amazonaws.com/prod/chat/sessao-123/history?limit=10"
```

## Como Remover a Infraestrutura

Para evitar custos indesejados, você pode excluir tudo facilmente:

```bash
terraform destroy
```
*Digite `yes` para confirmar.*
