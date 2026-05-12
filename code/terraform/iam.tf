data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project_name}-lambda-role-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_xray" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

data "aws_iam_policy_document" "lambda_custom_policy" {
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:GetItem"
    ]
    resources = [aws_dynamodb_table.chat_history.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = ["arn:aws:bedrock:${var.aws_region}::foundation-model/us.anthropic.claude-haiku-4-5-20251001-v1:0", "arn:aws:bedrock:${var.aws_region}::foundation-model/us.anthropic.claude-haiku-4-5-20251001-v1:0", "*"]
  }
}

resource "aws_iam_policy" "lambda_custom_policy" {
  name   = "${var.project_name}-lambda-policy-${var.environment}"
  policy = data.aws_iam_policy_document.lambda_custom_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_custom_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_custom_policy.arn
}
