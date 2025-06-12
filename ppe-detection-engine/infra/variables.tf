variable "iac_test_bucket_name" {
    type        = string
    default     = "safesightai-iac-bucket"
    description = "Just a simple test to get a grip of the IaC workflow"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}
