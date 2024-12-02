
# Output the API Gateway URL (Endpoint)
output "api_gateway_url" {
  value = "${aws_api_gateway_deployment.payment_apigateway_deploy.invoke_url}${aws_api_gateway_stage.app_stage.stage_name}"
}

output "user_pool_id" {
  value = aws_cognito_user_pool.payApp_user_pool.id
}

output "client_id" {
  value     = aws_cognito_user_pool_client.payApp_userpool_client
  sensitive = true
}