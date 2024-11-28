
/*
* Core resources required to integrate AWS API Gateay with AWS Lambda are:
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

  endpoint_configuration {
    types = ["REGIONAL"]
  }
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
  request_validator_id = aws_api_gateway_request_validator.req_validator.id

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
  request_validator_id = aws_api_gateway_request_validator.req_validator.id

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

resource "aws_api_gateway_request_validator" "req_validator" {
  name                        = "RequestBodyValidator"
  rest_api_id                 = aws_api_gateway_rest_api.api.id
  validate_request_body       = true
  validate_request_parameters = false
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
        "pattern" : "^[A-Za-z0-9]{8,20}$",
        "minLength" : 8,
        "maxLength" : 20
      },
      "email" : {
        "type" : "string",
        "format" : "email",
        "pattern" : "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
        # example: a@b.c
        "minLength" : 5,
        # see RFC 5321 and RFC 5322
        "maxLength" : 254
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
        "type" : "string",
        "pattern" : "^[A-Za-z0-9]{8,20}$",
        "minLength" : 8,
        "maxLength" : 20
      },
      "email" : {
        "type" : "string",
        "format" : "email",
        "pattern" : "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        # example: a@b.c
        "minLength" : 5,
        # see RFC 5321 and RFC 5322
        "maxLength" : 254
      },
      "amount" : {
        "type" : "number",
        "minimum" : 1,
        "maximum" : 1000000

      },
      "currency" : {
        "type" : "string",
        "enum" : ["USD", "INR", "EUR", "JPY", "GBP"]
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

  /* TBD
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.pay_app_api_gateway_loggroup.arn
  }
  */
}

# create IAM role for lambda
resource "aws_iam_role" "pay_app_apigateway_role" {
  name               = "PaymentAppAPIGatewayRole"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": ["apigateway.amazonaws.com"]
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  EOF
}

# allow API gateway to push logs to CloudWatch
resource "aws_api_gateway_account" "pay_app_apigateway_account" {
  cloudwatch_role_arn = aws_iam_role.pay_app_apigateway_role.arn
}

# attach cloudWatch policy to IAM role
resource "aws_iam_role_policy_attachment" "pay_app_cloudwatch_log_policy" {
  role       = aws_iam_role.pay_app_apigateway_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}


 # enable all methods full request and response logs to cloudWatch
 resource "aws_api_gateway_method_settings" "payapp_cloudwatch_logs" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.app_stage.stage_name
  method_path = "*/*"

  settings {
    logging_level      = "INFO"
    metrics_enabled    = true
    data_trace_enabled = true
  }
}
