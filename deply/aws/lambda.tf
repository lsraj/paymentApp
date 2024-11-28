
resource "aws_lambda_function" "payment_lambda" {

  function_name    = "paymentLambda"
  filename         = "../../lambda/paymentApp-lambda.zip"
  source_code_hash = filebase64sha256("../../lambda/paymentApp-lambda.zip")
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  memory_size      = 128
  timeout          = 60

  environment {
    variables = {
      PAYPAL_SANDBOX_URL = var.paypal_sandbox_url
      PAYPAL_CLIENT_ID   = var.paypal_clinet_id
      PAYPAL_SECRET      = var.paypal_secret
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_dynamodb_attachment,
    aws_iam_role_policy_attachment.lambda_logs,
  ]

}

# create IAM role for lambda
resource "aws_iam_role" "lambda_role" {
  name               = "PaymentAppLambdaRole"
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

# create IAM policy for lambda to interact with DynamoDB (basic access)
resource "aws_iam_policy" "dynamodb_access_policy" {
  name        = "PaymentAppDynamodbPolicy"
  description = "IAM policy to access Payment App's DynamoDB"

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
        Effect = "Allow"
        Resource = [
          aws_dynamodb_table.disbursements.arn,
          aws_dynamodb_table.customers.arn
        ]
      }
    ]
  })
}

# create cloudwatch logging group for lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.payment_lambda.function_name}"
  retention_in_days = var.cloudwatch_logs_retention_days
}

#create IAM policy for lambda to send logs to cloudwatch
resource "aws_iam_policy" "lambda_cloudwatch_logging" {
  name        = "lambdaLogginPolicy"
  description = "IAM policy for logging from a lambda"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:*",
        "Effect" : "Allow"
      }
    ]
  })
}

# attach dynamodb access policy to lambda role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_access_policy.arn
}

# attach cloudwatch logging policy to lambda role
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_logging.arn
}

