variable "vpc_id" {
  description = "The ID of the VPC in the Security Group"
  type        = string
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g. dev, staging, prod)"
}