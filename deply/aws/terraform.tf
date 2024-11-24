# contains a single terraform block to define required_providers and required_version

terraform {

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.58.0"
    }
  }

  # The ~> symbol allows the patch version to be greater than 2 but requires the major
  # and minor versions (1.9) to match the version that the configuration specifies.
  # Terraform will error if you attempt to use this configuration with a more recent
  # version than 1.9.x (such as 1.10.1 or 2.0.0), because of this required_version setting.

  required_version = "~> 1.9.2"
}

