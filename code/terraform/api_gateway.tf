resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "FinTrack AI Insights API"
}

resource "aws_api_gateway_resource" "chat" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "chat"
}

resource "aws_api_gateway_resource" "session" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.chat.id
  path_part   = "{sessionId}"
}

resource "aws_api_gateway_method" "post_chat" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.session.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_post_chat" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.session.id
  http_method             = aws_api_gateway_method.post_chat.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.chat_lambda.invoke_arn
}

resource "aws_api_gateway_resource" "history" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.session.id
  path_part   = "history"
}

resource "aws_api_gateway_method" "get_history" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.history.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_get_history" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.history.id
  http_method             = aws_api_gateway_method.get_history.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.chat_lambda.invoke_arn
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chat_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "api" {
  depends_on = [
    aws_api_gateway_integration.lambda_post_chat,
    aws_api_gateway_integration.lambda_get_history
  ]
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.session.id,
      aws_api_gateway_method.post_chat.id,
      aws_api_gateway_integration.lambda_post_chat.id,
      aws_api_gateway_resource.history.id,
      aws_api_gateway_method.get_history.id,
      aws_api_gateway_integration.lambda_get_history.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.api.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "prod"
}
