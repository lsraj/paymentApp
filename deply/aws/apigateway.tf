
/*
* Core resources required to integrate AWS  API Gateay with AWS Lambda are:
* - aws_api_gateway_rest_api
* - aws_api_gateway_resource
* - aws_api_gateway_method
* - aws_api_gateway_integration
* - aws_lambda_permission
* - aws_api_gateway_deployment
*
* aws_api_gateway_model resource also important to validate API request body.
**/

# API Gateway Setup
resource "aws_api_gateway_rest_api" "api" {
  name        = "paymentAppAPI"
  description = "API Gateway for paymentApp"
}

# create resource /v1
resource "aws_api_gateway_resource" "v1" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "v1"
}

# create resource /v1/api
resource "aws_api_gateway_resource" "v1_api" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.v1.id
  path_part   = "api"
}

# create resource /v1/api/customer
resource "aws_api_gateway_resource" "v1_api_customer" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.v1_api.id
  path_part   = "customer"
}

# create resource /v1/api/customer/{customer_id}
resource "aws_api_gateway_resource" "get_customer_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.v1_api_customer.id
  path_part   = "{customer_id}"
}

# create resource /v1/api/payments
resource "aws_api_gateway_resource" "v1_api_payments" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.v1_api.id
  path_part   = "payments"
}

# create POST method on /v1/api/customer
resource "aws_api_gateway_method" "post_customer" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.v1_api_customer.id
  http_method   = "POST"
  authorization = "NONE"

  request_models = {
    "application/json" = aws_api_gateway_model.customer_request_model.name
  }

  # ensure the request body model is created before the method
  depends_on = [aws_api_gateway_model.customer_request_model]
}

# create GET method on /v1/api/customer/{customer_id}
resource "aws_api_gateway_method" "get_customer" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.get_customer_id.id
  http_method   = "GET"
  authorization = "NONE"

  # TBD (Rajesham)
  # request_validator_id = aws_api_gateway_request_validator.id
  request_parameters = {
    "method.request.path.customer_id" = true # customer_id is required in path
  }
}

# create POST Method on /v1/api/payments
resource "aws_api_gateway_method" "post_payments" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.v1_api_payments.id
  http_method   = "POST"
  authorization = "NONE"

  request_models = {
    "application/json" = aws_api_gateway_model.payments_request_model.name
  }
  depends_on = [aws_api_gateway_model.payments_request_model]
}

# define the request body model for /v1/api/customer
resource "aws_api_gateway_model" "customer_request_model" {
  rest_api_id  = aws_api_gateway_rest_api.api.id
  name         = "CustomerRequestModel"
  content_type = "application/json"
  schema = jsonencode({
    "type" : "object",
    "properties" : {
      "customer_id" : {
        "type" : "string"
      },
      "email" : {
        "type" : "string",
        "format" : "email"
      }
    },
    "required" : ["customer_id", "email"]
  })
}

# define the request body model for /v1/api/payments
resource "aws_api_gateway_model" "payments_request_model" {
  rest_api_id  = aws_api_gateway_rest_api.api.id
  name         = "PaymentsRequestModel"
  content_type = "application/json"
  schema = jsonencode({
    "type" : "object",
    "properties" : {
      "customer_id" : {
        "type" : "string"
      },
      "email" : {
        "type" : "string",
        "format" : "email"
      },
      "amount" : {
        "type" : "number",
        "format" : "float"
      },
      "currency" : {
        "type" : "string"
      }
    },
    "required" : ["customer_id", "email", "amount", "currency"]
  })
}

# lambda integration for /v1/api/customer
resource "aws_api_gateway_integration" "customer_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.v1_api_customer.id
  http_method = aws_api_gateway_method.post_customer.http_method

  # Note: For API Gateway and lambda integration, the integration_http_method
  # is always "POST". When API Gateway invokes a Lambda function via AWS Proxy
  # integration (AWS_PROXY), the HTTP method API Gateway uses to call Lambda
  # is always POST, regardless of the method (e.g., GET, POST, PUT, etc.) you
  # define for the resource.
  integration_http_method = "POST"

  type = "AWS_PROXY"
  uri  = aws_lambda_function.payment_lambda.invoke_arn
}

# lambda integration for /v1/api/customer/{customer_id}
resource "aws_api_gateway_integration" "customer_id_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.get_customer_id.id
  http_method             = aws_api_gateway_method.get_customer.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.payment_lambda.invoke_arn
  request_parameters = {
    "integration.request.path.customer_id" = "method.request.path.customer_id"
  }
}

# lambda lntegration for /v1/api/payments
resource "aws_api_gateway_integration" "payments_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.v1_api_payments.id
  http_method             = aws_api_gateway_method.post_payments.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.payment_lambda.invoke_arn
}

# permissions to allow API Gateway to invoke lambda (Customer)
resource "aws_lambda_permission" "allow_api_gateway_customer" {
  statement_id  = "AllowExecutionFromPaymentAppAPIGateway" # some unique name
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.payment_lambda.function_name
  principal     = "apigateway.amazonaws.com"
}


resource "aws_api_gateway_deployment" "payment_apigateway_deploy" {

  rest_api_id = aws_api_gateway_rest_api.api.id

  # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment:
  #
  # When the REST API configuration involves other Terraform resources
  # (aws_api_gateway_integration resource, etc.), the dependency setup
  # can be done with implicit resource references in the 'triggers' argument
  # or explicit resource references using the resource depends_on meta-argument.
  # The triggers argument should be preferred over 'depends_on', since depends_on
  # can only capture dependency ordering and will not cause the resource to
  # recreate (redeploy the REST API) with upstream configuration changes.

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.api.body,
      aws_api_gateway_resource.v1.id,
      aws_api_gateway_resource.v1_api.id,
      aws_api_gateway_resource.v1_api_customer.id,
      aws_api_gateway_resource.v1_api_payments.id,
      aws_api_gateway_method.post_customer.id,
      aws_api_gateway_method.get_customer.id,
      aws_api_gateway_method.post_payments.id,
      aws_api_gateway_integration.customer_integration.id,
      aws_api_gateway_integration.customer_id_integration.id,
      aws_api_gateway_integration.payments_integration.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "app_stage" {
  deployment_id = aws_api_gateway_deployment.payment_apigateway_deploy.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = var.payment_app_apigateway_stage
}
