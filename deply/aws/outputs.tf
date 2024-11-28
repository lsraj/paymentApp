

# Output the API Gateway URL (Endpoint)
output "api_gateway_url" {
  value = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.app_stage.stage_name}"

}
