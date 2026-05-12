data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "chat_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "${var.project_name}-chat-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 29
  memory_size      = 256

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.chat_history.name
      MODEL_ID   = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
