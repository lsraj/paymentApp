# Terraform cheatseet

Terraform is a powerful tool for managing infrastructure as code. Here are some basic commands that are essential for using Terraform:

1. `terraform init`

    - Purpose: Initializes a new or existing Terraform configuration directory. It downloads the necessary provider plugins and sets up the working directory.
    - Usage: `terraform init`


2. `terraform plan`

    - Purpose: Creates an execution plan, which shows what actions Terraform will take to achieve the desired state defined in your configuration files. It helps to preview changes before applying them.
    - Usage: `terraform plan`


3. `terraform apply`

    - Purpose: Applies the changes required to reach the desired state of the configuration. It creates or updates resources based on the execution plan.
    - Usage: `terraform apply`


4. `terraform destroy`

    - Purpose: Destroys the resources managed by Terraform. It removes all the resources defined in your configuration files.
    - Usage: `terraform destroy`


5. `terraform validate`

    - Purpose: Validates the configuration files for syntax and internal consistency. It checks if the configuration is valid and will work with the current version of Terraform.
    - Usage: `terraform validate`


6. `terraform fmt`

    - Purpose: Formats the Terraform configuration files to a canonical format and style. This helps keep the code consistent and readable.
    - Usage: `terraform fmt`


7. `terraform show`

    - Purpose: Displays the current state or a plan in a human-readable format. It can be used to inspect the state file or see the results of terraform plan.
    - Usage: `terraform show`


8. `terraform output`

    - Purpose: Extracts the values of output variables from the Terraform state file. Useful for retrieving information that other configurations or scripts might need.
    - Usage: `terraform output`


9. `terraform refresh`

    - Purpose: Updates the state file with the latest information from the infrastructure. This is useful if you suspect that the state file and the real-world infrastructure are out of sync.
    - Usage: `terraform refresh`


10. `terraform state`

    - Purpose: Provides various subcommands to interact with the state file, such as listing resources, moving resources, or removing resources from the state.
    - Usage: `terraform state <subcommand>`


11. `terraform taint`

    - Purpose: Marks a resource for recreation during the next terraform apply. It is used to force the recreation of a resource if it's known to be in a bad state.
    - Usage: `terraform taint <resource>`


12. `terraform untaint`:

    - Purpose: Removes the "tainted" status from a resource, which prevents it from being recreated during the next terraform apply.
    - Usage: `terraform untaint <resource>`
