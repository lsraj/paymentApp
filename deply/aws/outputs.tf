
# Output the API Gateway URL (Endpoint)
output "api_gateway_url" {
  value = "${aws_api_gateway_deployment.payment_apigateway_deploy.invoke_url}${aws_api_gateway_stage.app_stage.stage_name}"
}
