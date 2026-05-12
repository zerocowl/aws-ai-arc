output "api_endpoint" {
  description = "A URL base do API Gateway"
  value       = aws_api_gateway_stage.prod.invoke_url
}

output "lambda_function_arn" {
  description = "ARN da função Lambda criada"
  value       = aws_lambda_function.chat_lambda.arn
}
