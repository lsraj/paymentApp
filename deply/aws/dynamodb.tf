
# create Disbursements table
resource "aws_dynamodb_table" "disbursements" {
  name           = var.disbursements_table_name
  billing_mode   = var.billing_mode
  read_capacity  = var.RCU
  write_capacity = var.WCU

  # table keys
  hash_key  = "customer_id" # Partition Key
  range_key = "payment_id"  # Sort Key

  attribute {
    name = "customer_id"
    type = "S" # String
  }

  attribute {
    name = "payment_id"
    type = "S" # String
  }

  # Optional: Time to Live (TTL) configuration (e.g., for expiring old records)
  ttl {
    # attribute_name = "timestamp"
    enabled = false # Set to true if you want TTL enabled on the timestamp attribute
  }

  # Optional: Tags for the DynamoDB table
  tags = {
    Name        = "Disbursements Table"
    Environment = "Test"
  }
}

# create Customers table
resource "aws_dynamodb_table" "customers" {
  name           = var.customers_table_name
  billing_mode   = var.billing_mode
  read_capacity  = var.RCU
  write_capacity = var.WCU

  hash_key = "customer_id" # Partition Key

  attribute {
    name = "customer_id"
    type = "S" # String
  }

  # Optional: Time to Live (TTL) configuration (e.g., for expiring old records)
  ttl {
    # attribute_name = "timestamp"
    enabled = false # Set to true if you want TTL enabled on the timestamp attribute
  }

  # Optional: Tags for the DynamoDB table
  tags = {
    Name        = "Customers Table"
    Environment = "Test"
  }
}
