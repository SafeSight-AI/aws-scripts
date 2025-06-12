variable "aws_region" { // Without this variable, terraform thinks we are in eu-central-2
  type    = string
  default = "us-east-1"
}

variable "iac_test_bucket_name" {
    type        = string
    default     = "safesightai-iac-bucket"
    description = "Just a simple test to get a grip of the IaC workflow"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
}