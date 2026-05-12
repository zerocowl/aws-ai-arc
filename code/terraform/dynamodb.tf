resource "aws_dynamodb_table" "chat_history" {
  name           = var.table_name
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "sessionId"
  range_key      = "timestamp"

  attribute {
    name = "sessionId"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
