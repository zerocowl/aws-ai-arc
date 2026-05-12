variable "aws_region" {
  description = "Região para o deploy"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Nome do ambiente (ex: sandbox, prod)"
  type        = string
  default     = "sandbox"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "fintrack-ai-insights"
}

variable "table_name" {
  description = "Nome da tabela do DynamoDB"
  type        = string
  default     = "fintrack-chat-history"
}
