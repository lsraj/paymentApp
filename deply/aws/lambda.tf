resource "aws_lambda_function" "payment_lambda" {

  function_name    = "payment_lambda"
  filename         = "../../lambda/paymentApp-lambda.zip"
  source_code_hash = filebase64sha256("../../lambda/paymentApp-lambda.zip")
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler" # Your Python handler function
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

}

