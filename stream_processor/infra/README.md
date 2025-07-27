# Terraform Infrastructure

This repository contains Terraform scripts to manage and provision infrastructure for the Stream Processor project.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) installed on your local machine.
- AWS CLI configured with appropriate credentials.
- Access to the AWS account where the infrastructure will be deployed.

## Structure

The Terraform configuration is organized into several different modules, each of which handle a different AWS service

## Usage

1. **Initialize Terraform**:
    ```bash
    terraform init
    ```

2. **Validate Configuration**:
    ```bash
    terraform validate
    ```

3. **Plan Changes**:
    ```bash
    terraform plan
    ```

4. **Apply Changes**:
    ```bash
    terraform apply
    ```

5. **Destroy Infrastructure** (if needed):
    ```bash
    terraform destroy
    ```

## Variables

Define required variables in a `terraform.tfvars` file or pass them directly during execution. Example:

```hcl
aws_region = "us-east-1"
environment = "dev"
```

## Outputs

After applying, Terraform will display the outputs, such as resource IDs and endpoints. These can also be accessed using:

```bash
terraform output
```

## Notes

- Ensure proper IAM permissions for the AWS credentials used.
- Review the `backend` configuration for state management.

## License

This project is licensed under the MIT License.