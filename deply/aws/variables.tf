variable "aws_region" {
  type        = string
  description = "AWS Region"
}

variable "disbursements_table_name" {
  type        = string
  description = "Disbursement Table in Dynamodb"
}

variable "customers_table_name" {
  type        = string
  description = "Customers Table in Dynamodb"
}

variable "billing_mode" {
  type        = string
  description = "Dynamodb Billing Mode"
}

variable "RCU" {
  type        = number
  description = "Read Capacity Units"
}

variable "WCU" {
  type        = number
  description = "Write Capacity Units"
}


variable "paypal_sandbox_url" {
  description = "PAYPAL_SANDBOX_URL"
  type        = string
  sensitive   = true
}

variable "paypal_clinet_id" {
  description = "PAYPAL_CLIENT_ID"
  type        = string
  sensitive   = true
}

variable "paypal_secret" {
  description = "PAYPAL_SECRET"
  type        = string
  sensitive   = true
}

