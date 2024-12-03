
variable "enable_rate_limit" {
  description = "enable payApp rate limiting"
  type        = bool
  default     = true
}

# Basic plan default settings:
# - 500 requests per month;
# - 5 requests per second;
# - 10 requests in burst.

# max number of requests allowed in the period
variable "basic_plan_quota_limit" {
  description = "PayApp API Gateway basic plan quota limit"
  type        = number
  default     = 500
}
# quota period can be DAY, WEEK, or MONTH
variable "basic_plan_quota_period" {
  description = "PayApp API Gateway basic plan quota period"
  type        = string
  default     = "MONTH"
}
# allowed requests per second
variable "basic_plan_rate_limit" {
  description = "PayApp API Gateway basic plan rate limit"
  type        = number
  default     = 5
}
variable "basic_plan_burst_limit" {
  description = "PayApp API Gateway basic plan burst limit"
  type        = number
  default     = 10
}

# create resource for basic plan
resource "aws_api_gateway_usage_plan" "basic_usage_plan" {
  name = "basic-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_stage.app_stage.stage_name
  }

  quota_settings {
    limit  = var.basic_plan_quota_limit
    period = var.basic_plan_quota_period
  }

  throttle_settings {
    burst_limit = var.basic_plan_burst_limit
    rate_limit  = var.basic_plan_rate_limit
  }
}

# create key for basic plan. this can be controlled with enable_rate_limit variable.
resource "aws_api_gateway_api_key" "basic_plan_api_key" {
  name        = "basic-plan-api-key"
  description = "PayApp basic plan API Key for rate limiting"
  enabled     = var.enable_rate_limit
}

# associate the api key with the basic plan
resource "aws_api_gateway_usage_plan_key" "basic_usage_plan_key" {
  usage_plan_id = aws_api_gateway_usage_plan.basic_usage_plan.id
  key_id        = aws_api_gateway_api_key.basic_plan_api_key.id
  key_type      = "API_KEY"
}

# Standard plan default settings (double the basic plan settings)
# - 1000 requests per month;
# - 10 requests per second;
# - 20 requests in burst.
# max number of requests allowed in the period
variable "standard_plan_quota_limit" {
  description = "PayApp API Gateway standard plan quota limit"
  type        = number
  default     = 1000
}
# quota period can be DAY, WEEK, or MONTH
variable "standard_plan_quota_period" {
  description = "PayApp API Gateway standard plan quota period"
  type        = string
  default     = "MONTH"
}
# allowed requests per second
variable "standard_plan_rate_limit" {
  description = "PayApp API Gateway standard plan rate limit"
  type        = number
  default     = 10
}
variable "standard_plan_burst_limit" {
  description = "PayApp API Gateway standard plan burst limit"
  type        = number
  default     = 20
}

# create resource for standard plan
resource "aws_api_gateway_usage_plan" "standard_usage_plan" {
  name = "standard-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_stage.app_stage.stage_name
  }

  quota_settings {
    limit  = var.standard_plan_quota_limit
    period = var.standard_plan_quota_period
  }

  throttle_settings {
    burst_limit = var.standard_plan_burst_limit
    rate_limit  = var.standard_plan_rate_limit
  }
}

# create key for standard plan. this can be controlled with enable_rate_limit variable.
resource "aws_api_gateway_api_key" "standard_plan_api_key" {
  name        = "standard-plan-api-key"
  description = "PayApp standard plan API Key for rate limiting"
  enabled     = var.enable_rate_limit
}

# associate the api key with the basic plan
resource "aws_api_gateway_usage_plan_key" "standard_usage_plan_key" {
  usage_plan_id = aws_api_gateway_usage_plan.standard_usage_plan.id
  key_id        = aws_api_gateway_api_key.standard_plan_api_key.id
  key_type      = "API_KEY"
}


# Premium plan default settings (3 times the basic plan settings):
# - 1500 requests per month;
# - 15 requests per second;
# - 30 requests in burst.
variable "premium_plan_quota_limit" {
  description = "PayApp API Gateway premium plan quota limit"
  type        = number
  default     = 1500
}
# quota period can be DAY, WEEK, or MONTH
variable "premium_plan_quota_period" {
  description = "PayApp API Gateway premium plan quota period"
  type        = string
  default     = "MONTH"
}
# allowed requests per second
variable "premium_plan_rate_limit" {
  description = "PayApp API Gateway premium plan rate limit"
  type        = number
  default     = 15
}
variable "premium_plan_burst_limit" {
  description = "PayApp API Gateway premium plan burst limit"
  type        = number
  default     = 30
}

# create resource for premium plan
resource "aws_api_gateway_usage_plan" "premium_usage_plan" {
  name = "premium-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_stage.app_stage.stage_name
  }

  quota_settings {
    limit  = var.premium_plan_quota_limit
    period = var.premium_plan_quota_period
  }

  throttle_settings {
    burst_limit = var.premium_plan_burst_limit
    rate_limit  = var.premium_plan_rate_limit
  }
}

# create key for premium plan. this can be controlled with enable_rate_limit variable.
resource "aws_api_gateway_api_key" "premium_plan_api_key" {
  name        = "premium-plan-api-key"
  description = "PayApp premium plan API Key for rate limiting"
  enabled     = var.enable_rate_limit
}

# associate the api key with the premium plan
resource "aws_api_gateway_usage_plan_key" "premium_usage_plan_key" {
  usage_plan_id = aws_api_gateway_usage_plan.premium_usage_plan.id
  key_id        = aws_api_gateway_api_key.premium_plan_api_key.id
  key_type      = "API_KEY"
}