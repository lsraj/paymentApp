
# Create DynamoDB Table for Disbursements
resource "aws_dynamodb_table" "disbursements" {
  name           = var.disbursements_table_name
  billing_mode   = var.billing_mode
  read_capacity  = var.RCU
  write_capacity = var.WCU

  # Define the table keys
  hash_key  = "customer_id" # Partition Key
  range_key = "payment_id"   # Sort Key

  # Define the attributes for the keys

  attribute {
    name = "customer_id"
    type = "S" # String
  }

  attribute {
    name = "payment_id"
    type = "S" # String
  }

  # Optional: Time to Live (TTL) configuration (e.g., for expiring old records)
  ttl {
    # attribute_name = "timestamp"
    enabled        = false # Set to true if you want TTL enabled on the timestamp attribute
  }

  # Optional: Tags for the DynamoDB table
  tags = {
    Name        = "Disbursements Table"
    Environment = "Test"
  }
}

# Create DynamoDB Table for Disbursements
resource "aws_dynamodb_table" "customers" {
  name           = var.customers_table_name
  billing_mode   = var.billing_mode
  read_capacity  = var.RCU
  write_capacity = var.WCU

  # Define the table keys
  hash_key  = "customer_id" # Partition Key

  # Define the attributes for the keys

  attribute {
    name = "customer_id"
    type = "S" # String
  }

  # Optional: Time to Live (TTL) configuration (e.g., for expiring old records)
  ttl {
    # attribute_name = "timestamp"
    enabled        = false # Set to true if you want TTL enabled on the timestamp attribute
  }

  # Optional: Tags for the DynamoDB table
  tags = {
    Name        = "Customers Table"
    Environment = "Test"
  }
}

# IAM Role for Lambda to interact with DynamoDB
resource "aws_iam_role" "lambda_role" {
  name               = "LambdaDynamodbRole"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": ["lambda.amazonaws.com"]
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

# IAM Policy for Lambda to interact with DynamoDB (basic access)
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "LambdaDynamodbPolicy"
  description = "IAM policy to allow Lambda functions to access DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:GetItem"
        ]
        Effect   = "Allow"
        Resource = [
            aws_dynamodb_table.disbursements.arn,
            aws_dynamodb_table.customers.arn
        ]
      }
    ]
  })
}

# Attach the policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}

# Data source for IAM Role assume policy document (for Lambda execution role)
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
