
resource "aws_cognito_user_pool" "payApp_user_pool" {
  name = "payApp_user_pool"
  password_policy {
    minimum_length    = 8
    require_lowercase = false
    require_uppercase = false
    require_numbers   = false
    require_symbols   = false
  }
}

resource "aws_cognito_user_pool_client" "payApp_userpool_client" {
  name                                 = "payApp_userpool_client"
  user_pool_id                         = aws_cognito_user_pool.payApp_user_pool.id
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["aws.cognito.signin.user.admin"]
  supported_identity_providers         = ["COGNITO"]
  explicit_auth_flows                  = ["ADMIN_NO_SRP_AUTH", "USER_PASSWORD_AUTH"]
  callback_urls                        = ["https://example.com"]
  prevent_user_existence_errors        = "ENABLED"
}

resource "aws_cognito_user" "payApp_user" {
  user_pool_id = aws_cognito_user_pool.payApp_user_pool.id
  username     = var.payApp_username
  password     = var.payApp_password
}

resource "aws_api_gateway_authorizer" "payApp_authorizer" {
  name                             = "payApp_authorizer"
  rest_api_id                      = aws_api_gateway_rest_api.api.id
  type                             = "COGNITO_USER_POOLS"
  provider_arns                    = [aws_cognito_user_pool.payApp_user_pool.arn]
  identity_source                  = "method.request.header.Authorization" # Where the ID Token will be passed (Authorization header)
  authorizer_result_ttl_in_seconds = 300                                   # Cache the result for 5 minutes (optional)
}
